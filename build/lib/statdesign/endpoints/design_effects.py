"""Design effect utilities for clustered and repeated measures designs."""

from __future__ import annotations

import math


def _validate_positive(value: float, name: str) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def design_effect_cluster_equal(m: float, icc: float) -> float:
    """Return design effect for equal cluster sizes."""

    _validate_positive(m, "m")
    if not 0 <= icc < 1:
        raise ValueError("icc must be in [0, 1)")
    return 1.0 + (m - 1.0) * icc


def design_effect_cluster_unequal(mbar: float, icc: float, cv: float) -> float:
    """Return design effect for unequal cluster sizes."""

    _validate_positive(mbar, "mbar")
    if not 0 <= icc < 1:
        raise ValueError("icc must be in [0, 1)")
    if cv < 0:
        raise ValueError("cv must be non-negative")
    return 1.0 + icc * (mbar - 1.0 + cv**2)


def design_effect_repeated_cs(k: int, icc: float) -> float:
    """Variance inflation under compound symmetry for repeated measures."""

    if k < 1:
        raise ValueError("k must be at least 1")
    if not 0 <= icc < 1:
        raise ValueError("icc must be in [0, 1)")
    return 1.0 + (k - 1.0) * icc


def inflate_n_by_de(n_individuals: int, de: float) -> int:
    """Inflate an individual-level sample size by a design effect."""

    if n_individuals < 0:
        raise ValueError("n_individuals must be non-negative")
    if de <= 0:
        raise ValueError("de must be positive")
    return int(math.ceil(n_individuals * de))


__all__ = [
    "design_effect_cluster_equal",
    "design_effect_cluster_unequal",
    "design_effect_repeated_cs",
    "inflate_n_by_de",
]
