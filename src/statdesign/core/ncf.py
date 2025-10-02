"""Distribution helpers with optional SciPy acceleration."""

from __future__ import annotations

import math
from typing import Literal

from .._scipy_backend import has_scipy, require_scipy
from . import normal

Tail = Literal["two-sided", "greater", "less"]


def _chi2_ppf(prob: float, df: float) -> float:
    """Chi-squared percent point function using Wilson-Hilferty approximation."""
    if df <= 0:
        raise ValueError("degrees of freedom must be positive")
    z = normal.ppf(prob)
    term = 1.0 - 2.0 / (9.0 * df) + z * math.sqrt(2.0 / (9.0 * df))
    return df * (term**3)


def _get_stats():
    """Get scipy.stats module, raising helpful error if not available."""
    return require_scipy("Noncentral distributions")


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
        # Add numerical stability guards
        if df_num <= 0 or df_den <= 0 or lambda_ < 0:
            raise ValueError("ncf: invalid degrees of freedom or noncentrality parameter")
        if lambda_ <= 0.0:
            return 0.0
        crit_num = _chi2_ppf(1.0 - alpha, df_num)
        crit_den = _chi2_ppf(alpha, df_den)
        if crit_den <= 0.0:
            return 0.0
        crit = (df_den * crit_num) / (df_num * crit_den)
        mean = df_num + lambda_
        # Ensure variance is positive for numerical stability
        var = max(2.0 * (df_num + 2.0 * lambda_), 1e-12)
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
