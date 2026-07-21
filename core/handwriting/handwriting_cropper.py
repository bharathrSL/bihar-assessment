"""Upscale handwriting answer crops for AI inspection."""
import cv2
import numpy as np
class HandwritingCropper:
    def prepare(self, crop: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY) if crop.ndim == 3 else crop
        return cv2.resize(cv2.createCLAHE(2.0, (8,8)).apply(gray), None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
