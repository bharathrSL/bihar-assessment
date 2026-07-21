"""Typed domain objects used across the processing pipeline."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any

@dataclass(frozen=True)
class Question:
    id: str; type: str; page: int; options: list[str]; required: bool = False

@dataclass
class Answer:
    question_id: str; selected_codes: list[str] = field(default_factory=list)
    answer_text: str = ""; confidence: float = 0.0; review_required: bool = False
    raw_observations: str = ""; final_confidence: float = 0.0
    def to_dict(self) -> dict[str, Any]: return asdict(self)

@dataclass
class Record:
    record_id: str; pdf: str; answers: dict[str, Answer]; confidence: float
    review: bool; audit: list[str] = field(default_factory=list)
    def to_dict(self) -> dict[str, Any]:
        return {"record_id": self.record_id, "pdf": self.pdf, "confidence": self.confidence,
                "review": self.review, "audit": self.audit,
                "answers": {k: v.to_dict() for k, v in self.answers.items()}}
