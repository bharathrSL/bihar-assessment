"""Fixed-layout configuration and normalized coordinate conversion."""
from pathlib import Path
from core.utils import read_json
class BookletLayout:
    def __init__(self, path: str | Path): self.data = read_json(path)
    def region(self, page: int, question_id: str) -> tuple[float, float, float, float]:
        return tuple(self.data.get("pages", {}).get(str(page), {}).get("regions", {}).get(question_id, self.data["default_region"]))
    def pixels(self, page: int, question_id: str, width: int, height: int) -> tuple[int, int, int, int]:
        x, y, w, h = self.region(page, question_id)
        return int(x * width), int(y * height), int(w * width), int(h * height)
