"""Power and sample-size utilities."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Tuple

import numpy as np
from scipy.stats import norm

_Z = norm.ppf


def _z_alpha(alpha: float, two_sided: bool = True) -> float:
    a = alpha / 2 if two_sided else alpha
    return _Z(1 - a)


def power_one_prop(p: float, p0: float, n: int, alpha: float = 0.05, two_sided: bool = True) -> float:
    """Normal-approximation power for a one-sample proportion test."""
    if n <= 0:
        raise ValueError("n must be positive")
    se = math.sqrt(p0 * (1 - p0) / n)
    z = abs(p - p0) / se
    zcrit = _z_alpha(alpha, two_sided)
    return float(1 - norm.cdf(zcrit - z) + norm.cdf(-zcrit - z))


def n_one_prop(p: float, p0: float, alpha: float = 0.05, power: float = 0.8, two_sided: bool = True) -> int:
    delta = abs(p - p0)
    if delta == 0:
        raise ValueError("Effect size must be non-zero")
    z_alpha = _z_alpha(alpha, two_sided)
    z_beta = _Z(power)
    se = math.sqrt(p0 * (1 - p0))
    n = ((z_alpha + z_beta) * se / delta) ** 2
    return max(1, math.ceil(n))


def power_two_prop(
    p1: float,
    p2: float,
    n1: int,
    n2: int | None = None,
    alpha: float = 0.05,
    two_sided: bool = True,
) -> float:
    if n2 is None:
        n2 = n1
    if n1 <= 0 or n2 <= 0:
        raise ValueError("sample sizes must be positive")
    se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    delta = abs(p2 - p1)
    zcrit = _z_alpha(alpha, two_sided)
    z = delta / se
    return float(1 - norm.cdf(zcrit - z) + norm.cdf(-zcrit - z))


def n_two_prop(
    p1: float,
    p2: float,
    alpha: float = 0.05,
    power: float = 0.8,
    ratio: float = 1.0,
    two_sided: bool = True,
) -> Tuple[int, int]:
    if ratio <= 0:
        raise ValueError("ratio must be positive")
    delta = abs(p2 - p1)
    if delta == 0:
        raise ValueError("Effect size must be non-zero")
    z_alpha = _z_alpha(alpha, two_sided)
    z_beta = _Z(power)
    pbar = (p1 + p2) / 2
    qbar = 1 - pbar
    pooled_term = z_alpha * math.sqrt(2 * pbar * qbar * (1 + 1 / ratio))
    diff_term = z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2) / ratio)
    n1 = ((pooled_term + diff_term) ** 2) / (delta**2)
    n1 = max(1, math.ceil(n1))
    n2 = max(1, math.ceil(ratio * n1))
    return n1, n2


def power_one_mean(
    mu0: float,
    mu1: float,
    sd: float,
    n: int,
    alpha: float = 0.05,
    two_sided: bool = True,
) -> float:
    if n <= 0:
        raise ValueError("n must be positive")
    if sd <= 0:
        raise ValueError("sd must be positive")
    delta = abs(mu1 - mu0)
    se = sd / math.sqrt(n)
    zcrit = _z_alpha(alpha, two_sided)
    z = delta / se
    return float(1 - norm.cdf(zcrit - z) + norm.cdf(-zcrit - z))


def n_one_mean(
    mu0: float,
    mu1: float,
    sd: float,
    alpha: float = 0.05,
    power: float = 0.8,
    two_sided: bool = True,
) -> int:
    delta = abs(mu1 - mu0)
    if delta == 0:
        raise ValueError("Effect size must be non-zero")
    if sd <= 0:
        raise ValueError("sd must be positive")
    z_alpha = _z_alpha(alpha, two_sided)
    z_beta = _Z(power)
    n = ((z_alpha + z_beta) * sd / delta) ** 2
    return max(1, math.ceil(n))


def power_two_mean(
    mu1: float,
    mu2: float,
    sd1: float,
    sd2: float,
    n1: int,
    n2: int | None = None,
    alpha: float = 0.05,
    pooled: bool = True,
    two_sided: bool = True,
) -> float:
    if n2 is None:
        n2 = n1
    if min(n1, n2) <= 0:
        raise ValueError("sample sizes must be positive")
    if min(sd1, sd2) <= 0:
        raise ValueError("standard deviations must be positive")
    delta = abs(mu2 - mu1)
    if pooled:
        se = math.sqrt(((sd1**2) * (n1 - 1) + (sd2**2) * (n2 - 1)) / (n1 + n2 - 2)) * math.sqrt(1 / n1 + 1 / n2)
    else:
        se = math.sqrt(sd1**2 / n1 + sd2**2 / n2)
    zcrit = _z_alpha(alpha, two_sided)
    z = delta / se
    return float(1 - norm.cdf(zcrit - z) + norm.cdf(-zcrit - z))


def n_two_mean(
    mu1: float,
    mu2: float,
    sd1: float,
    sd2: float,
    alpha: float = 0.05,
    power: float = 0.8,
    ratio: float = 1.0,
    two_sided: bool = True,
) -> Tuple[int, int]:
    if ratio <= 0:
        raise ValueError("ratio must be positive")
    delta = abs(mu2 - mu1)
    if delta == 0:
        raise ValueError("Effect size must be non-zero")
    if min(sd1, sd2) <= 0:
        raise ValueError("standard deviations must be positive")
    z_alpha = _z_alpha(alpha, two_sided)
    z_beta = _Z(power)
    n1 = ((z_alpha + z_beta) ** 2 * (sd1**2 + sd2**2 / ratio)) / (delta**2)
    n1 = max(1, math.ceil(n1))
    n2 = max(1, math.ceil(ratio * n1))
    return n1, n2


def power_paired_t(mu_diff: float, sd_diff: float, n: int, alpha: float = 0.05, two_sided: bool = True) -> float:
    if n <= 0:
        raise ValueError("n must be positive")
    if sd_diff <= 0:
        raise ValueError("sd_diff must be positive")
    delta = abs(mu_diff)
    se = sd_diff / math.sqrt(n)
    zcrit = _z_alpha(alpha, two_sided)
    z = delta / se
    return float(1 - norm.cdf(zcrit - z) + norm.cdf(-zcrit - z))


def n_paired_t(mu_diff: float, sd_diff: float, alpha: float = 0.05, power: float = 0.8, two_sided: bool = True) -> int:
    delta = abs(mu_diff)
    if delta == 0:
        raise ValueError("Effect size must be non-zero")
    if sd_diff <= 0:
        raise ValueError("sd_diff must be positive")
    z_alpha = _z_alpha(alpha, two_sided)
    z_beta = _Z(power)
    n = ((z_alpha + z_beta) * sd_diff / delta) ** 2
    return max(1, math.ceil(n))


def n_anova_oneway(k: int, effect_f: float, alpha: float = 0.05, power: float = 0.8) -> int:
    if k < 2:
        raise ValueError("k must be >= 2")
    if effect_f <= 0:
        raise ValueError("effect size must be positive")
    z_alpha = _z_alpha(alpha, two_sided=False)
    z_beta = _Z(power)
    n = ((z_alpha + z_beta) ** 2) * (1 + effect_f**2) / (effect_f**2)
    return max(1, math.ceil(n))


def adjust_bonferroni(alpha: float, m: int) -> float:
    if m <= 0:
        raise ValueError("m must be positive")
    return alpha / m


def adjust_bh(alpha: float, m: int, k: int) -> float:
    if not (1 <= k <= m):
        raise ValueError("k must be between 1 and m")
    return alpha * k / m
