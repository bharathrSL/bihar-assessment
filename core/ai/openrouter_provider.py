"""OpenRouter vision provider for the fixed-questionnaire extraction contract."""
from __future__ import annotations

import base64
import json
import time
import traceback
from pathlib import Path

from dotenv import load_dotenv

from core.ai.response_parser import ResponseParser
from core.ai.retry import Retry
from core.models import Answer, Question, StudentInfo
from llm_provider import LLMClient


class OpenRouterProvider:
    """Send all question crops to a vision-capable OpenRouter model."""

    def __init__(self, model: str, parser: ResponseParser, retry: Retry):
        self.model, self.parser, self.retry = model, parser, retry

    def extract(
        self,
        prompt: str,
        crops: dict[str, Path],
        questions: list[Question],
        debug_dir: Path | None = None,
    ) -> tuple[StudentInfo, list[Answer]]:
        load_dotenv()
        client = LLMClient(model_name=self.model)
        if not client.active_token:
            return (
                StudentInfo(),
                [
                    Answer(
                        q.id,
                        confidence=0,
                        review_required=True,
                        raw_observations="OpenRouter was not called: OPENROUTER_API_KEY is unavailable",
                    )
                    for q in questions
                ],
            )

        # for question in questions:
        #     crop = crops.get(question.id)
        #     if crop is None or not crop.exists() or crop.stat().st_size == 0:
        #         raise FileNotFoundError(f"Missing or empty crop for {question.id}: {crop}")

        for name, image in crops.items():
            if image is None or not image.exists() or image.stat().st_size == 0:
                raise FileNotFoundError(f"Missing image: {image}")

        if debug_dir:
            debug_dir.mkdir(parents=True, exist_ok=True)
            (debug_dir / "request.json").write_text(
                json.dumps({"provider": "openrouter", "model": self.model,
                            "image_count": len(crops),
                            "image_paths": {str(k): str(v) for k, v in crops.items()},
                            "prompt_length": len(prompt)}, indent=2),
                encoding="utf-8",
            )

        contents: list[object] = [prompt]
        # contents.extend({"mime_type": "image/png", "data": base64.b64encode(crops[q.id].read_bytes()).decode("ascii")}
        #                 for q in questions)
        for _, image_path in sorted(crops.items()):
            contents.append({
                "mime_type": "image/png",
                "data": base64.b64encode(image_path.read_bytes()).decode("ascii"),
            })
        started = time.monotonic()
        try:
            response = self.retry.run(lambda: client.generate_content(contents, max_retries=1))
            if debug_dir:
                (debug_dir / "raw_response.txt").write_text(response.text or "", encoding="utf-8")
                (debug_dir / "response_metadata.json").write_text(
                    json.dumps({"latency_seconds": round(time.monotonic() - started, 3),
                                "usage": vars(response.usage_metadata)}, indent=2), encoding="utf-8")
            student, answers = self.parser.parse(response.text)
            if debug_dir:
                (debug_dir / "parsed.json").write_text(
                    json.dumps(
                        {
                            "student": student.to_dict(),
                            "answers": [answer.to_dict() for answer in answers],
                        },
                        ensure_ascii=False,
                        indent=2,
                    ),
                    encoding="utf-8",
                )
            return student, answers
        except Exception:
            if debug_dir:
                (debug_dir / "exception.txt").write_text(traceback.format_exc(), encoding="utf-8")
            raise
