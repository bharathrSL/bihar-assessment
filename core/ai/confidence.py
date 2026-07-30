# """Fuse independent quality indicators into a reviewable confidence score."""
# class ConfidenceEngine:
#     def calculate(self, llm: float, checkbox: float, image: float, handwriting: float, rules_ok: bool) -> float:
#         visual=max(checkbox, handwriting)
#         return round(max(0.,min(1., .45*llm+.25*visual+.20*image+.10*(1. if rules_ok else 0.))),3)

class ConfidenceEngine:
    def calculate(
        self,
        llm: float,
        image: float,
        rules_ok: bool,
    ) -> float:

        score = (
            0.70 * llm +
            0.20 * image +
            0.10 * (1.0 if rules_ok else 0.0)
        )

        return round(max(0.0, min(1.0, score)), 3)