"""Deskew scans using foreground-line orientation."""
import cv2
import numpy as np
class Deskewer:
    def correct(self, image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
        coords = np.column_stack(np.where(gray < 180))
        if len(coords) < 50: return image
        angle = cv2.minAreaRect(coords[:, ::-1].astype(np.float32))[-1]
        angle = -(90 + angle) if angle < -45 else -angle
        h, w = image.shape[:2]
        return cv2.warpAffine(image, cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1), (w, h), borderMode=cv2.BORDER_REPLICATE)
