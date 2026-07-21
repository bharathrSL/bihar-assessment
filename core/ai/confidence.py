"""Fuse independent quality indicators into a reviewable confidence score."""
class ConfidenceEngine:
    def calculate(self, gemini: float, checkbox: float, image: float, handwriting: float, rules_ok: bool) -> float:
        visual=max(checkbox, handwriting)
        return round(max(0.,min(1., .45*gemini+.25*visual+.20*image+.10*(1. if rules_ok else 0.))),3)
