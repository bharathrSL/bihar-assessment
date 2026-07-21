from pathlib import Path
from core.questionnaire.schema_loader import SchemaLoader
ROOT=Path(__file__).parents[1]
def test_fixed_schema_has_exactly_34_questions():
    questions=SchemaLoader(ROOT/"config"/"questionnaire.json").load()
    assert len(questions)==34
    assert questions[0].id=="Q1" and questions[-1].id=="Q34"
