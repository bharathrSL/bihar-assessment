"""Image quality metrics used for review assignment."""
import cv2
import numpy as np
class ImageQuality:
    def score(self, image: np.ndarray) -> float:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
        sharp = min(cv2.Laplacian(gray, cv2.CV_64F).var() / 500.0, 1.0)
        contrast = min(float(gray.std()) / 64.0, 1.0)
        exposure = 1.0 - min(abs(float(gray.mean()) - 170) / 170, 1.0)
        return round(max(0.0, .45 * sharp + .35 * contrast + .20 * exposure), 3)
