"""Durable storage of human corrections and associated crops."""
from pathlib import Path
from datetime import datetime, timezone
from core.utils import read_json, write_json
class CorrectionStore:
    def __init__(self, root: str | Path): self.root=Path(root); self.path=self.root/"corrections.jsonl"; self.root.mkdir(parents=True,exist_ok=True)
    def save(self, correction: dict) -> None:
        correction={**correction,"corrected_at":datetime.now(timezone.utc).isoformat()}
        with self.path.open("a",encoding="utf-8") as f: f.write(__import__("json").dumps(correction)+"\n")
    def retrieve(self, question_id: str, limit: int=3) -> list[dict]:
        if not self.path.exists(): return []
        rows=[__import__("json").loads(x) for x in self.path.read_text(encoding="utf-8").splitlines() if x]
        return [r for r in reversed(rows) if r.get("question_id")==question_id][:limit]
