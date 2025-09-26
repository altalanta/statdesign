"""Allocation helpers for multi-group designs."""

from __future__ import annotations

import math
from collections.abc import Iterable


def validate_ratio(ratio: float) -> None:
    if ratio <= 0:
        raise ValueError("ratio must be positive")


def groups_from_n1(n1: int, ratio: float) -> tuple[int, int]:
    """Return integer group sizes (n1, n2) for ratio = n2 / n1."""

    if n1 < 1:
        raise ValueError("n1 must be at least 1")
    validate_ratio(ratio)
    n2 = max(1, int(math.ceil(n1 * ratio)))
    return n1, n2


def groups_from_total(total: int, ratio: float) -> tuple[int, int]:
    """Resolve total sample size into integer group sizes under ratio."""

    if total < 2:
        raise ValueError("total sample size must be at least 2")
    validate_ratio(ratio)
    share = total / (1.0 + ratio)
    n1 = max(1, int(round(share)))
    n2 = max(1, total - n1)
    if n1 + n2 != total:
        n2 = total - n1
    if n2 < 1:
        n2 = 1
        n1 = total - 1
    if n1 < 1:
        n1 = 1
        n2 = total - 1
    return n1, n2


def allocate_by_weights(total: int, weights: Iterable[float]) -> list[int]:
    """Allocate ``total`` observations according to relative ``weights``."""

    weights = list(weights)
    if not weights:
        raise ValueError("weights cannot be empty")
    if any(w <= 0 for w in weights):
        raise ValueError("weights must be positive")
    if total < len(weights):
        raise ValueError("total must be >= number of groups")

    weight_sum = float(sum(weights))
    raw = [total * (w / weight_sum) for w in weights]
    ints = [int(math.floor(x)) for x in raw]
    remainder = total - sum(ints)

    # distribute remaining units by descending fractional part
    fractions = sorted(
        enumerate([x - math.floor(x) for x in raw]),
        key=lambda pair: pair[1],
        reverse=True,
    )
    for idx, _ in fractions[:remainder]:
        ints[idx] += 1

    # ensure no zero-sized group
    for i, value in enumerate(ints):
        if value == 0:
            ints[i] = 1
    gap = total - sum(ints)
    if gap != 0:
        # add/subtract uniformly to fix rounding drift
        step = 1 if gap > 0 else -1
        idx = 0
        while gap != 0:
            ints[idx % len(ints)] += step
            if ints[idx % len(ints)] < 1:
                ints[idx % len(ints)] = 1
            gap -= step
            idx += 1
    return ints


def harmonic_mean(values: Iterable[float]) -> float:
    values = list(values)
    if not values:
        raise ValueError("values cannot be empty")
    if any(v <= 0 for v in values):
        raise ValueError("harmonic mean defined for positive values")
    return len(values) / sum(1.0 / v for v in values)
