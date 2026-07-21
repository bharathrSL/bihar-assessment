"""Suppress scanner speckles while retaining pen strokes."""
import cv2
import numpy as np
class NoiseRemover:
    def remove(self, image: np.ndarray) -> np.ndarray:
        return cv2.fastNlMeansDenoising(image, None, 8, 7, 21)
