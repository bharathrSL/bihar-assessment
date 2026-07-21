"""Classify checkbox marks and generate selected option codes."""
from core.checkbox.checkbox_detector import Mark
class CheckboxClassifier:
    def classify(self, marks: list[Mark], options: list[str]) -> tuple[list[str], float, str]:
        selected=[options[m.index] for m in marks if m.label == "checked" and m.index < len(options)]
        certainty=sum(m.certainty for m in marks)/len(marks) if marks else 0.0
        observation = "no checkbox contours" if not marks else f"{len(selected)} marked; patterns include tick/cross/circle/scribble when fill is ambiguous"
        return selected, certainty, observation
