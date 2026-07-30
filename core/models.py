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
class StudentInfo:
    student_name: str = ""
    gender: str = ""
    school_name: str = ""
    school_udise: str = ""
    crc_name: str = ""
    crc_udise: str = ""
    block: str = ""
    district: str = ""
    grade: str = ""
    meena_manch_participation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
    
@dataclass
class Record:
    record_id: str
    pdf: str
    student: StudentInfo = field(default_factory=StudentInfo)
    answers: dict[str, Answer] = field(default_factory=dict)
    confidence: float = 0.0
    review: bool = False
    audit: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "pdf": self.pdf,
            "student": self.student.to_dict(),
            "confidence": self.confidence,
            "review": self.review,
            "audit": self.audit,
            "answers": {
                k: v.to_dict() for k, v in self.answers.items()
            }
        }
