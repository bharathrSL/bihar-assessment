"""Align a logical page to its stored master-page reference."""
import cv2
import numpy as np


class PageAligner:
    """Use ECC affine registration, with translation-only fallback."""

    def align(self, image: np.ndarray, reference: np.ndarray | None = None) -> np.ndarray:
        if reference is None:
            return image
        if reference.shape[:2] != image.shape[:2]:
            reference = cv2.resize(reference, (image.shape[1], image.shape[0]))
        a = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
        b = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY) if reference.ndim == 3 else reference
        a = cv2.GaussianBlur(a, (5, 5), 0)
        b = cv2.GaussianBlur(b, (5, 5), 0)
        matrix = np.eye(2, 3, dtype=np.float32)
        try:
            _, matrix = cv2.findTransformECC(np.float32(b) / 255.0, np.float32(a) / 255.0, matrix, cv2.MOTION_AFFINE, (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 80, 1e-5))
            return cv2.warpAffine(image, matrix, (image.shape[1], image.shape[0]), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
        except cv2.error:
            (dx, dy), _ = cv2.phaseCorrelate(np.float32(a), np.float32(b))
            fallback = np.float32([[1, 0, dx], [0, 1, dy]])
            return cv2.warpAffine(image, fallback, (image.shape[1], image.shape[0]), borderMode=cv2.BORDER_REPLICATE)
