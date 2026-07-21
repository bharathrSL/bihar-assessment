from core.models import Answer, Question
from core.rules.rule_engine import RuleEngine
def test_single_choice_rejects_multiple_codes():
    question=Question("Q1","single_choice",1,["A","B"])
    assert "multiple choice for single-choice question" in RuleEngine().evaluate(Answer("Q1",["A","B"],confidence=.8),question)
