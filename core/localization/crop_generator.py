"""Persist safe question crops without relying on absolute scanner pixels."""
from pathlib import Path
import cv2
import numpy as np
from core.localization.question_locator import QuestionLocator
class CropGenerator:
    def __init__(self, locator: QuestionLocator, root: str | Path): self.locator, self.root = locator, Path(root)
    def crop(self, image: np.ndarray, page: int, question_id: str, record_id: str) -> tuple[np.ndarray, Path]:
        x, y, w, h = self.locator.locate(image, page, question_id); crop = image[y:y+h, x:x+w]
        path = self.root / record_id / f"{question_id}.png"; path.parent.mkdir(parents=True, exist_ok=True)
        if crop.size == 0: raise ValueError(f"Empty crop for {question_id}")
        cv2.imwrite(str(path), crop); return crop, path
