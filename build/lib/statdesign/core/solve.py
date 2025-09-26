"""Deterministic solvers for monotone power equations."""

from __future__ import annotations

import math
from typing import Callable

PowerFn = Callable[[int], float]


def solve_monotone_int(
    evaluator: PowerFn,
    target: float,
    lower: int = 2,
    upper: int | None = None,
    max_iterations: int = 64,
    max_value: int = 1_000_000,
) -> int:
    """Return the minimal integer n >= lower such that evaluator(n) >= target.

    The callable must be non-decreasing in n. The function expands the upper
    bracket exponentially until the target is exceeded or the configured
    maximum is hit, then performs integer bisection.
    """

    if not 0 < target < 1:
        raise ValueError("target power must be in (0, 1)")
    if lower < 1:
        raise ValueError("lower bound must be >= 1")

    if upper is None:
        upper = max(lower, 2)
        value = evaluator(upper)
        # Expand until we exceed target or hit max_value
        while value < target:
            if upper >= max_value:
                raise RuntimeError("Failed to bracket solution before reaching max sample size")
            upper = min(max_value, int(math.ceil(upper * 2)))
            value = evaluator(upper)
    else:
        value = evaluator(upper)

    low = lower
    high = upper

    while low < high:
        mid = (low + high) // 2
        if mid == high:
            break
        val = evaluator(mid)
        if val >= target:
            high = mid
        else:
            low = mid + 1

    return max(low, lower)
