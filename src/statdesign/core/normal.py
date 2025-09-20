"""Normal distribution helpers without external dependencies."""

from __future__ import annotations

from statistics import NormalDist

_NORMAL = NormalDist()


def ppf(p: float) -> float:
    return float(_NORMAL.inv_cdf(p))


def cdf(x: float) -> float:
    return float(_NORMAL.cdf(x))


def sf(x: float) -> float:
    return float(1.0 - _NORMAL.cdf(x))
