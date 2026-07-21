from core.ai.response_parser import ResponseParser
def test_parser_rejects_extra_fields():
    raw='[{"question_id":"Q1","selected_codes":[],"answer_text":"","confidence":0.5,"review_required":false,"raw_observations":"x","unexpected":1}]'
    try: ResponseParser().parse(raw)
    except ValueError: return
    assert False, "Unexpected response field must be rejected"
