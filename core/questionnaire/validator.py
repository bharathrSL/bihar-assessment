"""Input and answer schema validation."""
from pathlib import Path
from core.models import Answer, Question

class Validator:
    @staticmethod
    def validate_pdf(path: Path) -> list[str]:
        errors = []
        if path.suffix.lower() != ".pdf": errors.append("Input is not a PDF")
        if not path.exists() or path.stat().st_size == 0: errors.append("PDF is empty or unavailable")
        return errors
    @staticmethod
    def validate_answer(answer: Answer, question: Question) -> list[str]:
        issues = []
        if answer.question_id != question.id: issues.append("question ID mismatch")
        if not 0 <= answer.confidence <= 1: issues.append("invalid confidence")
        if any(x not in question.options for x in answer.selected_codes): issues.append("invalid option")
        if question.type == "single_choice" and len(answer.selected_codes) > 1: issues.append("multiple choice for single-choice question")
        return issues
