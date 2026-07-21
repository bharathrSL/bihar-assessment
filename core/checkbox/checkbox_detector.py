"""Find and score filled checkbox candidates in a question crop."""
from dataclasses import dataclass
import cv2
import numpy as np
@dataclass
class Mark: index: int; fill_ratio: float; certainty: float; label: str
class CheckboxDetector:
    def detect(self, image: np.ndarray, expected: int) -> list[Mark]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
        binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        boxes = sorted([cv2.boundingRect(c) for c in contours if 8 <= cv2.boundingRect(c)[2] <= 80 and 8 <= cv2.boundingRect(c)[3] <= 80], key=lambda b:b[0])[:expected]
        marks=[]
        for i, (x,y,w,h) in enumerate(boxes):
            inner=binary[y+max(2,h//5):y+h-max(2,h//5),x+max(2,w//5):x+w-max(2,w//5)]
            ratio=float((inner>0).mean()) if inner.size else 0.0
            label = "checked" if ratio>.20 else "empty"
            marks.append(Mark(i, ratio, min(1,abs(ratio-.20)/.20), label))
        return marks
