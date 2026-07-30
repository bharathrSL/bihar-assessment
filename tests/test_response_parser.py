import pytest

from core.ai.response_parser import ResponseParser


def test_parser_ignores_extra_fields_with_warning():
    raw='[{"question_id":"Q1","selected_codes":[],"answer_text":"","confidence":0.5,"review_required":false,"raw_observations":"x","unexpected":1}]'
    with pytest.warns(RuntimeWarning, match="Ignoring unexpected LLM response fields"):
        answers = ResponseParser().parse(raw)
    assert answers[0].question_id == "Q1"
