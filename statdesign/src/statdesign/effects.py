"""Effect size helpers."""

from __future__ import annotations

import numpy as np


def cohens_d(mu1: float, mu2: float, sd_pooled: float) -> float:
    """Compute Cohen's d for two means."""
    if sd_pooled <= 0:
        raise ValueError("sd_pooled must be positive")
    return (mu2 - mu1) / sd_pooled


def h_proportions(p1: float, p2: float) -> float:
    """Cohen's h for two proportions."""
    if not (0 <= p1 <= 1 and 0 <= p2 <= 1):
        raise ValueError("proportions must be between 0 and 1")
    return 2 * np.arcsin(np.sqrt(p2)) - 2 * np.arcsin(np.sqrt(p1))
