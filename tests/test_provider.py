"""Live provider test using the exact production GeminiProvider request builder."""
from __future__ import annotations

import json
from pathlib import Path

from core.ai.gemini_provider import GeminiProvider
from core.ai.response_parser import ResponseParser
from core.ai.retry import Retry
from core.models import Question


class CapturingParser(ResponseParser):
    """Captures Gemini's raw response while preserving production parsing."""

    raw_response: str = ""

    def parse(self, text: str):  # type: ignore[override]
        self.raw_response = text
        return super().parse(text)


def main() -> None:
    root = Path(__file__).parents[1]
    crop = root / "output" / "crops" / "135c97572a9bdfb6" / "Q1.png"
    parser = CapturingParser()
    provider = GeminiProvider("gemini-3.5-flash", parser, Retry(attempts=1))
    question = Question("Q1", "single_choice", 3, ["A", "B", "C", "D"], True)
    prompt = (
        "Return a JSON array with exactly one object containing question_id, "
        "selected_codes, answer_text, confidence, review_required, and "
        "raw_observations. The question_id is Q1 and allowed options are A, B, C, D."
    )
    provider.extract(prompt, {"Q1": crop}, [question])
    parsed = json.loads(parser.raw_response)
    assert isinstance(parsed, list) and parsed, "Gemini response is not a non-empty JSON array"
    print(parser.raw_response)


if __name__ == "__main__":
    main()
