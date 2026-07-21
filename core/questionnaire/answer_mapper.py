"""Map structured answers to Excel-safe cell values."""
from core.models import Answer

class AnswerMapper:
    @staticmethod
    def value(answer: Answer) -> str:
        return "; ".join(answer.selected_codes) if answer.selected_codes else answer.answer_text.strip()
