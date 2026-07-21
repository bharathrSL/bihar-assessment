"""Estimate readability from sharpness, contrast and ink coverage."""
import cv2
import numpy as np
class HandwritingQuality:
    def score(self, image: np.ndarray) -> float:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
        sharp=min(cv2.Laplacian(gray, cv2.CV_64F).var()/400,1)
        ink=min(float((gray < 180).mean())/.08,1)
        return round(.65*sharp+.35*ink,3)
