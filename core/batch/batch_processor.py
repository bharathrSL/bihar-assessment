"""Resumable, parallel-safe per-PDF fixed-booklet processor."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import hashlib, fitz, cv2, yaml
import numpy as np
from core.models import Answer, Record
from core.utils import read_json, write_json
from core.questionnaire.schema_loader import SchemaLoader
from core.questionnaire.prompt_builder import PromptBuilder
from core.preprocessing.image_cleaner import ImageCleaner
from core.preprocessing.deskew import Deskewer
from core.preprocessing.shadow_removal import ShadowRemover
from core.preprocessing.noise_removal import NoiseRemover
from core.preprocessing.image_quality import ImageQuality
from core.localization.booklet_layout import BookletLayout
from core.localization.question_locator import QuestionLocator
from core.localization.crop_generator import CropGenerator
from core.localization.page_alignment import PageAligner
from core.localization.spread_splitter import SpreadSplitter
from core.checkbox.checkbox_detector import CheckboxDetector
from core.checkbox.checkbox_classifier import CheckboxClassifier
from core.handwriting.handwriting_cropper import HandwritingCropper
from core.handwriting.handwriting_quality import HandwritingQuality
from core.ai.gemini_provider import GeminiProvider
from core.ai.response_parser import ResponseParser
from core.ai.retry import Retry
from core.ai.confidence import ConfidenceEngine
from core.rules.rule_engine import RuleEngine
from core.questionnaire.validator import Validator

class BatchProcessor:
    def __init__(self, config_dir: str | Path, output_dir: str | Path):
        self.config=Path(config_dir); self.output=Path(output_dir); self.output.mkdir(parents=True,exist_ok=True)
        self.settings=yaml.safe_load((self.config/"settings.yaml").read_text(encoding="utf-8")); self.questions=SchemaLoader(self.config/"questionnaire.json").load()
        self.page_count = int(self.settings["logical_page_count"])
        if self.page_count != max(question.page for question in self.questions):
            raise ValueError("logical_page_count must match the highest question page")
        self.source_spread_count = int(self.settings["source_spread_count"])
        self.spread_map = {1: (12, 1), 2: (2, 3), 3: (4, 5), 4: (6, 7), 5: (8, 9), 6: (10, 11)}
        if self.source_spread_count != len(self.spread_map):
            raise ValueError("source_spread_count does not match the configured booklet spread map")
        self.splitter = SpreadSplitter(float(self.settings["spread_gutter_fraction"]))
        self.layout=BookletLayout(self.config/"pages.json"); self.prompt=PromptBuilder(self.config/"prompts.yaml").build(self.questions)
        self.state_path=self.output/self.settings["state_file"]
        self.reference_pages = self._load_reference_pages()

    def _render_pdf_page(self, page: fitz.Page) -> np.ndarray:
        pix = page.get_pixmap(dpi=int(self.settings["render_dpi"]), alpha=False)
        image = cv2.imdecode(np.frombuffer(pix.tobytes("png"), np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Unable to render source PDF page")
        return image

    def _load_reference_pages(self) -> dict[int, np.ndarray]:
        """Create twelve logical reference pages from the one master booklet."""
        path = (self.config / self.settings["reference_master_pdf"]).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Reference master PDF is missing: {path}")
        document = fitz.open(path)
        if len(document) != self.source_spread_count:
            raise ValueError(f"Reference master must have {self.source_spread_count} scanned spreads; found {len(document)}")
        references: dict[int, np.ndarray] = {}
        for spread_number, (left_page, right_page) in self.spread_map.items():
            spread = self.splitter.split(self._render_pdf_page(document[spread_number - 1]), left_page, right_page)
            references[spread.left_page] = spread.left
            references[spread.right_page] = spread.right
        return references
    def _state(self) -> dict: return read_json(self.state_path) if self.state_path.exists() else {"completed":{}}
    def estimate(self, pdfs: list[Path]) -> dict:
        spreads=sum(len(fitz.open(p)) for p in pdfs)
        return {"pdfs":len(pdfs),"source_spreads":spreads,"logical_pages":spreads * 2,"estimated_minutes":round(spreads*.16,1),"estimated_ai_cost_usd":round(spreads*.004,2)}
    def process_folder(self, input_dir: str | Path) -> list[Record]:
        pdfs=sorted(Path(input_dir).glob("*.pdf")); state=self._state(); pending=[p for p in pdfs if str(p.resolve()) not in state["completed"]]
        records=[]
        with ThreadPoolExecutor(max_workers=int(self.settings["workers"])) as pool:
            futures={pool.submit(self.process_pdf,p):p for p in pending}
            for future in as_completed(futures):
                record=future.result(); records.append(record); state["completed"][str(futures[future].resolve())]=record.to_dict(); write_json(self.state_path,state)
        records.extend(self._record_from_dict(x) for x in state["completed"].values() if x["record_id"] not in {r.record_id for r in records})
        return sorted(records,key=lambda r:r.pdf)
    def _record_from_dict(self, data: dict) -> Record:
        return Record(data["record_id"],data["pdf"],{k:Answer(**v) for k,v in data["answers"].items()},data["confidence"],data["review"],data.get("audit",[]))
    def process_pdf(self, pdf: Path) -> Record:
        errors=Validator.validate_pdf(pdf); record_id=hashlib.sha256(pdf.read_bytes()).hexdigest()[:16]
        if errors: return Record(record_id,pdf.name,{},0,True,errors)
        doc=fitz.open(pdf)
        if len(doc) != self.source_spread_count:
            return Record(
                record_id,
                pdf.name,
                {},
                0,
                True,
                [f"Expected {self.source_spread_count} two-page spreads; found {len(doc)}"],
            )
        crops={}; page_quality={}; checkbox_meta={}; writing_quality={}; locator=QuestionLocator(self.layout); generator=CropGenerator(locator,self.output/"crops")
        by_page = {
            page: [question for question in self.questions if question.page == page]
            for page in range(1, self.page_count + 1)
        }
        for spread_number, (left_page, right_page) in self.spread_map.items():
            split = self.splitter.split(self._render_pdf_page(doc[spread_number - 1]), left_page, right_page)
            for number, raw_image in ((split.left_page, split.left), (split.right_page, split.right)):
                image = Deskewer().correct(NoiseRemover().remove(ShadowRemover().remove(raw_image)))
                image = PageAligner().align(image, self.reference_pages[number])
                image = ImageCleaner().clean(image)
                page_quality[number]=ImageQuality().score(image)
                for q in by_page[number]:
                    crop,path=generator.crop(image,number,q.id,record_id); crops[q.id]=path
                    if "choice" in q.type:
                        marks=CheckboxDetector().detect(crop,len(q.options)); checkbox_meta[q.id]=CheckboxClassifier().classify(marks,q.options)
                    else: writing_quality[q.id]=HandwritingQuality().score(HandwritingCropper().prepare(crop))
        debug_root = self.output / "debug"
        (debug_root / "prompts").mkdir(parents=True, exist_ok=True)
        (debug_root / "prompts" / f"{record_id}.txt").write_text(self.prompt, encoding="utf-8")
        provider=GeminiProvider(self.settings["gemini_model"],ResponseParser(),Retry(self.settings["max_retries"],self.settings["retry_backoff_seconds"]))
        ai={a.question_id:a for a in provider.extract(self.prompt,crops,self.questions,debug_root / "responses" / record_id)}
        answers={}; audit=[]; engine=ConfidenceEngine(); rules=RuleEngine()
        for q in self.questions:
            answer=ai.get(q.id,Answer(q.id,confidence=0,review_required=True,raw_observations="missing AI answer"))
            checkbox=0.; handwriting=writing_quality.get(q.id,0.)
            if q.id in checkbox_meta:
                detected,checkbox,obs=checkbox_meta[q.id]
                # Computer vision contributes confidence only. It must never fill
                # an answer when Gemini is unavailable or intentionally returns
                # an empty response, because checkbox outlines otherwise look
                # like selected answers.
                answer.raw_observations=f"{answer.raw_observations}; CV cross-check: {obs}"
            issues=rules.evaluate(answer,q); answer.final_confidence=engine.calculate(answer.confidence,checkbox,page_quality[q.page],handwriting,not issues)
            answer.review_required=answer.review_required or bool(issues) or answer.final_confidence<float(self.settings["review_confidence_threshold"])
            audit.extend(f"{q.id}: {issue}" for issue in issues); answers[q.id]=answer
        confidence=round(sum(a.final_confidence for a in answers.values())/34,3)
        return Record(record_id,pdf.name,answers,confidence,any(a.review_required for a in answers.values()),audit)
