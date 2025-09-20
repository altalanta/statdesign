"""Distribution helpers with optional SciPy acceleration."""

from __future__ import annotations

import importlib
import os
from types import ModuleType
from typing import Literal

from . import normal

Tail = Literal["two-sided", "greater", "less"]

_STATS: ModuleType | None = None
_SCIPY_ERROR: Exception | None = None


def _maybe_import_scipy() -> None:
    global _STATS, _SCIPY_ERROR
    if _STATS is not None or _SCIPY_ERROR is not None:
        return
    if os.environ.get("STATDESIGN_AUTO_SCIPY", "0") != "1":
        return
    try:
        _STATS = importlib.import_module("scipy.stats")
    except Exception as exc:  # pragma: no cover - depends on user env
        _SCIPY_ERROR = exc


def has_scipy() -> bool:
    _maybe_import_scipy()
    return _STATS is not None


def _get_stats() -> ModuleType:
    _maybe_import_scipy()
    if _STATS is None:
        raise RuntimeError(
            "SciPy is required for this calculation. Set STATDESIGN_AUTO_SCIPY=1 "
            "in an environment with compatible SciPy to enable."
        )
    return _STATS


def power_normal(delta: float, alpha: float, tail: Tail) -> float:
    if tail == "two-sided":
        crit = normal.ppf(1.0 - alpha / 2.0)
        return normal.sf(crit - delta) + normal.cdf(-crit - delta)
    if tail == "greater":
        crit = normal.ppf(1.0 - alpha)
        return normal.sf(crit - delta)
    crit = normal.ppf(alpha)
    return normal.cdf(crit - delta)


def power_noncentral_t(delta: float, df: float, alpha: float, tail: Tail) -> float:
    stats = _get_stats()
    dist = stats.nct(df, delta)
    if tail == "two-sided":
        crit = stats.t.ppf(1.0 - alpha / 2.0, df)
        return float(dist.sf(crit) + dist.cdf(-crit))
    if tail == "greater":
        crit = stats.t.ppf(1.0 - alpha, df)
        return float(dist.sf(crit))
    crit = stats.t.ppf(alpha, df)
    return float(dist.cdf(crit))


def nct_cdf(x: float, df: float, delta: float) -> float:
    stats = _get_stats()
    return float(stats.nct(df, delta).cdf(x))


def power_noncentral_f(lambda_: float, df_num: float, df_den: float, alpha: float) -> float:
    stats = _get_stats()
    dist = stats.ncf(df_num, df_den, lambda_)
    crit = stats.f.ppf(1.0 - alpha, df_num, df_den)
    return float(dist.sf(crit))


def t_ppf(prob: float, df: float) -> float:
    stats = _get_stats()
    return float(stats.t.ppf(prob, df))
