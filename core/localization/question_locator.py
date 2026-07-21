"""Locate configured answer regions after page alignment."""
import numpy as np
from core.localization.booklet_layout import BookletLayout
class QuestionLocator:
    def __init__(self, layout: BookletLayout): self.layout = layout
    def locate(self, image: np.ndarray, page: int, question_id: str) -> tuple[int, int, int, int]:
        return self.layout.pixels(page, question_id, image.shape[1], image.shape[0])
