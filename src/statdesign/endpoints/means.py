"""Sample size calculations for mean-based designs.

When SciPy-backed distributions are unavailable (``STATDESIGN_AUTO_SCIPY`` unset),
``t``-based calculations transparently fall back to the normal approximation. The
approximation is accurate once degrees of freedom exceed the high single digits
but can be conservative for extremely small samples; users needing exact
noncentral ``t`` behaviour should opt into SciPy support.
"""

from __future__ import annotations

import math
from typing import Literal

from ..core import alloc, ncf, normal, solve

Tail = Literal["two-sided", "greater", "less"]
ZorT = Literal["z", "t"]
NIType = Literal["noninferiority", "equivalence"]


def _validate_common(alpha: float, power: float, tail: Tail) -> None:
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0, 1)")
    if not 0 < power < 1:
        raise ValueError("power must be in (0, 1)")
    if tail not in {"two-sided", "greater", "less"}:
        raise ValueError(f"unsupported tail: {tail}")


def _validate_margin(ni_margin: float | None, ni_type: NIType | None) -> None:
    if ni_type is None and ni_margin is not None:
        raise ValueError("ni_margin provided without ni_type")
    if ni_type is not None:
        if ni_margin is None:
            raise ValueError("ni_type requires ni_margin")
        if ni_margin <= 0:
            raise ValueError("ni_margin must be positive")


def _tost_bounds(
    alpha: float, margin: float, se: float, test: ZorT, df: float | None
) -> tuple[float, float]:
    if se <= 0:
        raise ValueError("standard error must be positive")
    if test == "t":
        if df is None:
            raise ValueError("df required for t-test")
        q = ncf.t_ppf(1.0 - alpha, df)
    elif test == "z":
        q = normal.ppf(1.0 - alpha)
    else:
        raise ValueError(f"unsupported test type: {test}")
    lower = q - margin / se
    upper = -q + margin / se
    if lower >= upper:
        # No chance to establish equivalence at this sample size
        return float("inf"), float("-inf")
    return lower, upper


def _power_location(
    effect: float, alpha: float, tail: Tail, test: ZorT, df: float | None
) -> float:
    if test == "t":
        if df is None:
            raise ValueError("df required for t distribution")
        return ncf.power_noncentral_t(effect, df, alpha, tail)
    if test == "z":
        return ncf.power_normal(effect, alpha, tail)
    raise ValueError(f"unsupported test: {test}")


def _power_equivalence(
    effect: float,
    se: float,
    alpha: float,
    test: ZorT,
    df: float | None,
    margin: float,
) -> float:
    if test == "t":
        if df is None:
            raise ValueError("df required for t distribution")
        lower, upper = _tost_bounds(alpha, margin, se, test, df)
        if lower >= upper:
            return 0.0
        return ncf.nct_cdf(upper, df, effect) - ncf.nct_cdf(lower, df, effect)
    if test == "z":
        lower, upper = _tost_bounds(alpha, margin, se, test, None)
        if lower >= upper:
            return 0.0
        return normal.cdf(upper - effect) - normal.cdf(lower - effect)
    raise ValueError(f"unsupported test: {test}")


def n_mean(
    mu1: float,
    mu2: float,
    sd: float,
    alpha: float = 0.05,
    power: float = 0.80,
    ratio: float = 1.0,
    test: ZorT = "t",
    tail: Tail = "two-sided",
    ni_margin: float | None = None,
    ni_type: NIType | None = None,
) -> tuple[int, int]:
    """Sample size for two independent means with common SD.

    When ``test='t'`` and SciPy support is not active (set
    ``STATDESIGN_AUTO_SCIPY=1`` to enable it), the solver falls back to the
    normal approximation with a small safety cushion to keep the result
    conservative. The approximation is accurate for moderate sample sizes but
    may over-estimate the required ``n`` slightly when degrees of freedom are
    extremely small.
    """

    _validate_common(alpha, power, tail)
    _validate_margin(ni_margin, ni_type)
    if sd <= 0:
        raise ValueError("sd must be positive")
    alloc.validate_ratio(ratio)
    if test not in {"t", "z"}:
        raise ValueError("test must be 't' or 'z'")
    if ni_type == "equivalence" and tail != "two-sided":
        raise ValueError("equivalence tests must use tail='two-sided'")
    if ni_type == "noninferiority" and tail == "two-sided":
        raise ValueError("noninferiority tests must specify one-sided tail")

    delta = mu2 - mu1

    def evaluator(n1: int) -> float:
        n1i = max(n1, 2 if test == "t" else 1)
        n1i, n2i = alloc.groups_from_n1(n1i, ratio)
        if test == "t" and (n1i < 2 or n2i < 2):
            return 0.0
        se = sd * math.sqrt(1.0 / n1i + 1.0 / n2i)
        df = n1i + n2i - 2 if test == "t" else None
        if ni_type is None:
            effect = delta / se
            return _power_location(effect, alpha, tail, test, df)
        if ni_type == "noninferiority":
            assert ni_margin is not None
            if tail == "greater":
                effect = (delta + ni_margin) / se
            else:  # tail == "less"
                effect = (delta - ni_margin) / se
            return _power_location(effect, alpha, tail, test, df)
        # equivalence
        assert ni_margin is not None
        effect = delta / se
        return _power_equivalence(effect, se, alpha, test, df, ni_margin)

    n1_final = solve.solve_monotone_int(evaluator, power, lower=2 if test == "t" else 1)
    n1_final, n2_final = alloc.groups_from_n1(n1_final, ratio)
    if test == "t":
        n1_final = max(n1_final, 2)
        n2_final = max(n2_final, 2)
        if not ncf.has_scipy():
            boost = 1
            while True:
                candidate = alloc.groups_from_n1(n1_final + boost, ratio)
                if candidate[0] > n1_final or candidate[1] > n2_final:
                    n1_final, n2_final = candidate
                    break
                boost += 1
    return n1_final, n2_final


def n_paired(
    delta: float,
    sd_diff: float,
    alpha: float = 0.05,
    power: float = 0.80,
    tail: Tail = "two-sided",
    ni_margin: float | None = None,
    ni_type: NIType | None = None,
) -> int:
    """Paired design sample size based on mean differences.

    Falls back to the normal approximation when SciPy is unavailable while
    adding a minimal cushion so the result remains conservative; enable
    ``STATDESIGN_AUTO_SCIPY=1`` for exact noncentral ``t`` calculations.
    """

    _validate_common(alpha, power, tail)
    _validate_margin(ni_margin, ni_type)
    if sd_diff <= 0:
        raise ValueError("sd_diff must be positive")
    if ni_type == "equivalence" and tail != "two-sided":
        raise ValueError("equivalence requires two-sided tail")
    if ni_type == "noninferiority" and tail == "two-sided":
        raise ValueError("noninferiority requires one-sided tail")

    def evaluator(n: int) -> float:
        n_i = max(n, 2)
        se = sd_diff / math.sqrt(n_i)
        df = n_i - 1
        if ni_type is None:
            effect = delta / se
            return _power_location(effect, alpha, tail, "t", df)
        if ni_type == "noninferiority":
            assert ni_margin is not None
            if tail == "greater":
                effect = (delta + ni_margin) / se
            else:
                effect = (delta - ni_margin) / se
            return _power_location(effect, alpha, tail, "t", df)
        assert ni_margin is not None
        effect = delta / se
        return _power_equivalence(effect, se, alpha, "t", df, ni_margin)

    n_final = solve.solve_monotone_int(evaluator, power, lower=2)
    n_final = max(n_final, 2)
    if not ncf.has_scipy():
        n_final += 2
    return n_final


def n_one_sample_mean(
    delta: float,
    sd: float,
    alpha: float = 0.05,
    power: float = 0.80,
    tail: Tail = "two-sided",
    test: ZorT = "t",
    ni_margin: float | None = None,
    ni_type: NIType | None = None,
) -> int:
    """One-sample mean test sample size.

    When ``test='t'`` and SciPy is not enabled the solver reverts to the normal
    approximation and pads the result slightly so the fallback is conservative.
    The values are typically within a couple of observations of the exact
    solution once the sample size exceeds roughly ten observations.
    """

    _validate_common(alpha, power, tail)
    _validate_margin(ni_margin, ni_type)
    if sd <= 0:
        raise ValueError("sd must be positive")
    if test not in {"t", "z"}:
        raise ValueError("test must be 't' or 'z'")
    if ni_type == "equivalence" and tail != "two-sided":
        raise ValueError("equivalence requires two-sided tail")
    if ni_type == "noninferiority" and tail == "two-sided":
        raise ValueError("noninferiority requires one-sided tail")

    def evaluator(n: int) -> float:
        n_i = max(n, 2 if test == "t" else 1)
        se = sd / math.sqrt(n_i)
        df = n_i - 1 if test == "t" else None
        if ni_type is None:
            effect = delta / se
            return _power_location(effect, alpha, tail, test, df)
        if ni_type == "noninferiority":
            assert ni_margin is not None
            if tail == "greater":
                effect = (delta + ni_margin) / se
            else:
                effect = (delta - ni_margin) / se
            return _power_location(effect, alpha, tail, test, df)
        assert ni_margin is not None
        effect = delta / se
        return _power_equivalence(effect, se, alpha, test, df, ni_margin)

    lower = 2 if test == "t" else 1
    n_final = solve.solve_monotone_int(evaluator, power, lower=lower)
    n_final = max(n_final, lower)
    if test == "t" and not ncf.has_scipy():
        n_final += 2
    return n_final


__all__ = ["n_mean", "n_paired", "n_one_sample_mean"]
