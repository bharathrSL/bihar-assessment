"""Split a two-page booklet scan into its two logical pages."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class SpreadPages:
    left_page: int
    left: np.ndarray
    right_page: int
    right: np.ndarray


class SpreadSplitter:
    """Crop a photographed two-page spread at its central binding gutter."""

    def __init__(self, gutter_fraction: float = 0.018) -> None:
        if not 0 <= gutter_fraction < 0.1:
            raise ValueError("gutter_fraction must be between 0 and 0.1")
        self.gutter_fraction = gutter_fraction

    def split(self, image: np.ndarray, left_page: int, right_page: int) -> SpreadPages:
        _, width = image.shape[:2]
        centre = width // 2
        gutter = max(2, int(width * self.gutter_fraction / 2))
        left = image[:, : centre - gutter]
        right = image[:, centre + gutter :]
        if not left.size or not right.size:
            raise ValueError("Could not split a spread into two non-empty pages")
        return SpreadPages(left_page, left, right_page, right)
