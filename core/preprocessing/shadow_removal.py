"""Remove slow-varying illumination/shadows."""
import cv2
import numpy as np
class ShadowRemover:
    def remove(self, image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
        bg = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, np.ones((31, 31), np.uint8))
        return cv2.normalize(cv2.divide(gray, bg, scale=255), None, 0, 255, cv2.NORM_MINMAX)
