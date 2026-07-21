"""Google GenAI provider for checkbox interpretation and Hindi handwriting."""
from pathlib import Path
import os
import json
import time
import traceback
from dotenv import load_dotenv
from google.genai import types
from core.ai.retry import Retry
from core.ai.response_parser import ResponseParser
from core.models import Question, Answer
class GeminiProvider:
    def __init__(self, model: str, parser: ResponseParser, retry: Retry): self.model,self.parser,self.retry=model,parser,retry
    def extract(self, prompt: str, crops: dict[str, Path], questions: list[Question], debug_dir: Path | None = None) -> list[Answer]:
        # Supports a local .env for VS Code runs while retaining normal environment
        # variable deployment. The .env file is excluded from version control.
        load_dotenv()
        key=os.getenv("GEMINI_API_KEY")
        if not key:
            return [Answer(q.id, confidence=0, review_required=True, raw_observations="Gemini was not called: GEMINI_API_KEY is unavailable") for q in questions]
        for question in questions:
            crop = crops.get(question.id)
            if crop is None or not crop.exists() or crop.stat().st_size == 0:
                raise FileNotFoundError(f"Missing or empty crop for {question.id}: {crop}")
        if debug_dir:
            debug_dir.mkdir(parents=True, exist_ok=True)
            (debug_dir / "request.json").write_text(json.dumps({"model": self.model, "question_ids": [q.id for q in questions], "crop_paths": {q.id: str(crops[q.id]) for q in questions}, "prompt_length": len(prompt)}, indent=2), encoding="utf-8")
        from google import genai
        client=genai.Client(api_key=key)
        parts = [types.Part.from_text(text=prompt)]
        parts.extend(
            types.Part.from_bytes(data=crops[question.id].read_bytes(), mime_type="image/png")
            for question in questions
        )
        contents = [types.Content(role="user", parts=parts)]
        started = time.monotonic()
        try:
            response=self.retry.run(lambda: client.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0,
                ),
            ))
            if debug_dir:
                (debug_dir / "raw_response.txt").write_text(response.text or "", encoding="utf-8")
                (debug_dir / "response_metadata.json").write_text(json.dumps({"latency_seconds": round(time.monotonic() - started, 3), "finish_reason": str(getattr(response, "finish_reason", None)), "usage": str(getattr(response, "usage_metadata", None))}, indent=2), encoding="utf-8")
            answers = self.parser.parse(response.text)
            if debug_dir:
                (debug_dir / "parsed.json").write_text(json.dumps([answer.to_dict() for answer in answers], ensure_ascii=False, indent=2), encoding="utf-8")
            return answers
        except Exception:
            if debug_dir:
                (debug_dir / "exception.txt").write_text(traceback.format_exc(), encoding="utf-8")
            raise
