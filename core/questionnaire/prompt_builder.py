"""Compose narrow, schema-driven AI prompts."""
from pathlib import Path
import yaml
from core.models import Question

class PromptBuilder:
    def __init__(self, prompts_path: str | Path):
        with Path(prompts_path).open(encoding="utf-8") as f: self.templates = yaml.safe_load(f)
    def build(self, questions: list[Question]) -> str:
        spec = [{"question_id": q.id, "type": q.type, "allowed_options": q.options} for q in questions]
        import json
        return f"{self.templates['system']}\n{self.templates['instruction']}\nQuestion contract: {json.dumps(spec, ensure_ascii=False)}"
