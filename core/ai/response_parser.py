"""Validate Gemini's answer contract while tolerating harmless extra fields."""
import json
import re
import warnings
from core.models import Answer
class ResponseParser:
    REQUIRED={"question_id","selected_codes","answer_text","confidence","review_required","raw_observations"}
    def parse(self, text: str) -> list[Answer]:
        match=re.search(r"\[[\s\S]*\]", text)
        if not match: raise ValueError("AI response did not contain a JSON array")
        payload=json.loads(match.group())
        if not isinstance(payload,list): raise ValueError("AI response must be an array")
        answers=[]
        for item in payload:
            if not isinstance(item, dict):
                raise ValueError("Every AI response item must be an object")
            missing = self.REQUIRED - set(item)
            if missing:
                raise ValueError(f"AI response is missing required fields: {sorted(missing)}")
            extras = set(item) - self.REQUIRED
            if extras:
                warnings.warn(f"Ignoring unexpected Gemini response fields: {sorted(extras)}", RuntimeWarning)
            answers.append(Answer(item["question_id"], list(item["selected_codes"]), str(item["answer_text"]), float(item["confidence"]), bool(item["review_required"]), str(item["raw_observations"])))
        return answers
