"""Deterministic questionnaire rules; AI output never bypasses these checks."""
from core.models import Answer, Question
from core.questionnaire.validator import Validator
class RuleEngine:
    def evaluate(self, answer: Answer, question: Question) -> list[str]:
        issues=Validator.validate_answer(answer, question)
        if question.required and not answer.selected_codes and not answer.answer_text.strip(): issues.append("mandatory answer missing")
        if question.type == "multiple_choice" and not answer.selected_codes and answer.answer_text: issues.append("text supplied for coded question")
        return issues
