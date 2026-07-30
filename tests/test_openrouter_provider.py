import base64

from core.ai.openrouter_provider import OpenRouterProvider
from core.ai.response_parser import ResponseParser
from core.ai.retry import Retry
from core.models import Question


class FakeClient:
    received = None
    active_token = "test-token"

    def __init__(self, **_kwargs):
        pass

    def generate_content(self, contents, max_retries):
        type(self).received = (contents, max_retries)
        return type("Response", (), {
            "text": '[{"question_id":"Q1","selected_codes":["A"],"answer_text":"","confidence":0.9,"review_required":false,"raw_observations":"clear mark"}]',
            "usage_metadata": type("Usage", (), {})(),
        })()


def test_openrouter_provider_encodes_crops_and_parses_response(monkeypatch, tmp_path):
    monkeypatch.setattr("core.ai.openrouter_provider.LLMClient", FakeClient)
    crop = tmp_path / "Q1.png"
    crop.write_bytes(b"image-bytes")
    provider = OpenRouterProvider("example/vision-model", ResponseParser(), Retry(attempts=1))

    answers = provider.extract("extract this", {"Q1": crop}, [Question("Q1", "single_choice", 1, ["A"], True)])

    assert answers[0].selected_codes == ["A"]
    contents, attempts = FakeClient.received
    assert contents[0] == "extract this"
    assert contents[1]["mime_type"] == "image/png"
    assert base64.b64decode(contents[1]["data"]) == b"image-bytes"
    assert attempts == 1
