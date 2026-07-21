"""Build a gold-standard JSONL dataset from reviewed corrections."""
from pathlib import Path
from core.learning.correction_store import CorrectionStore
class DatasetBuilder:
    def build(self, store: CorrectionStore, output: str | Path) -> int:
        rows=[]
        if store.path.exists(): rows=store.path.read_text(encoding="utf-8").splitlines()
        Path(output).write_text("\n".join(rows)+("\n" if rows else ""),encoding="utf-8")
        return len(rows)
