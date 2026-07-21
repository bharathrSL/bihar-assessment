"""Load and validate the sole supported questionnaire schema."""
from pathlib import Path
from typing import List

from core.models import Question
from core.utils import read_json


class SchemaLoader:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self) -> List[Question]:
        data = read_json(self.path)

        questions_data = data.get("questions", [])
        if len(questions_data) != 34:
            raise ValueError("Schema must define exactly 34 questions")

        # Ensure page_count matches highest page referenced by questions
        highest_page = max(int(q.get("page", 0)) for q in questions_data) if questions_data else 0
        if data.get("page_count") != highest_page:
            raise ValueError("page_count must match the highest configured question page")

        questions = [
            Question(
                q["id"],
                q["type"],
                int(q["page"]),
                q.get("options", []),
                q.get("required", False),
            )
            for q in questions_data
        ]

        if [q.id for q in questions] != [f"Q{i}" for i in range(1, 35)]:
            raise ValueError("Question IDs must be sequential Q1..Q34")

        return questions
