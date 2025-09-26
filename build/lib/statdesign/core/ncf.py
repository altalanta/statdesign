"""Distribution helpers with optional SciPy acceleration."""

from __future__ import annotations

import importlib
import math
import os
from types import ModuleType
from typing import Literal

from . import normal

Tail = Literal["two-sided", "greater", "less"]


def _chi2_ppf(prob: float, df: float) -> float:
    if df <= 0:
        raise ValueError("degrees of freedom must be positive")
    z = normal.ppf(prob)
    term = 1.0 - 2.0 / (9.0 * df) + z * math.sqrt(2.0 / (9.0 * df))
    return df * (term**3)


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
    if not has_scipy():
        return power_normal(delta, alpha, tail)
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
    if not has_scipy():
        return float(normal.cdf(x - delta))
    stats = _get_stats()
    return float(stats.nct(df, delta).cdf(x))


def power_noncentral_f(lambda_: float, df_num: float, df_den: float, alpha: float) -> float:
    if not has_scipy():
        if lambda_ <= 0.0:
            return 0.0
        crit_num = _chi2_ppf(1.0 - alpha, df_num)
        crit_den = _chi2_ppf(alpha, df_den)
        if crit_den <= 0.0:
            return 0.0
        crit = (df_den * crit_num) / (df_num * crit_den)
        mean = df_num + lambda_
        var = 2.0 * (df_num + 2.0 * lambda_)
        if var <= 0.0:
            return 0.0
        z = (mean - crit * df_num) / math.sqrt(var)
        return float(normal.sf(-z))
    stats = _get_stats()
    dist = stats.ncf(df_num, df_den, lambda_)
    crit = stats.f.ppf(1.0 - alpha, df_num, df_den)
    return float(dist.sf(crit))


def t_ppf(prob: float, df: float) -> float:
    if not has_scipy():
        return float(normal.ppf(prob))
    stats = _get_stats()
    return float(stats.t.ppf(prob, df))
