"""Sample size calculations for binomial proportions."""

from __future__ import annotations

import math
import warnings
from typing import Literal

from ..core import alloc, ncf, normal, solve

Tail = Literal["two-sided", "greater", "less"]
ZorT = Literal["z", "t"]
NIType = Literal["noninferiority", "equivalence"]

_MAX_EXACT = 200


def _validate_probability(value: float, name: str) -> None:
    if not 0 < value < 1:
        raise ValueError(f"{name} must be in (0, 1)")


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


def _check_normal_approximation_validity(p1: float, p2: float, n1: int, n2: int) -> None:
    """Check if normal approximation is appropriate and warn if not."""
    # Rule of thumb: np ≥ 5 and n(1-p) ≥ 5 for each group
    violations = []
    
    # Check group 1
    np1 = n1 * p1
    nq1 = n1 * (1 - p1)
    if np1 < 5:
        violations.append(f"n1*p1 = {np1:.1f} < 5")
    if nq1 < 5:
        violations.append(f"n1*(1-p1) = {nq1:.1f} < 5")
    
    # Check group 2  
    np2 = n2 * p2
    nq2 = n2 * (1 - p2)
    if np2 < 5:
        violations.append(f"n2*p2 = {np2:.1f} < 5")
    if nq2 < 5:
        violations.append(f"n2*(1-p2) = {nq2:.1f} < 5")
    
    if violations:
        warnings.warn(
            f"Normal approximation may be inaccurate: {', '.join(violations)}. "
            "Consider using exact=True or increasing sample size.",
            RuntimeWarning,
            stacklevel=3
        )


def _check_one_sample_normal_approximation(p: float, p0: float, n: int) -> None:
    """Check if normal approximation is appropriate for one-sample proportion test."""
    # For one-sample, check both observed and null proportions
    violations = []
    
    # Check under null hypothesis (more conservative)
    np0 = n * p0
    nq0 = n * (1 - p0)
    if np0 < 5:
        violations.append(f"n*p0 = {np0:.1f} < 5")
    if nq0 < 5:
        violations.append(f"n*(1-p0) = {nq0:.1f} < 5")
    
    # Also check under alternative (observed proportion)
    np = n * p
    nq = n * (1 - p)
    if np < 5:
        violations.append(f"n*p = {np:.1f} < 5")
    if nq < 5:
        violations.append(f"n*(1-p) = {nq:.1f} < 5")
    
    if violations:
        warnings.warn(
            f"Normal approximation may be inaccurate: {', '.join(violations)}. "
            "Consider using exact=True or increasing sample size.",
            RuntimeWarning,
            stacklevel=3
        )


def _binom_pmf_array(n: int, p: float) -> list[float]:
    q = 1.0 - p
    probs = [0.0] * (n + 1)
    prob = q**n
    probs[0] = prob
    for k in range(n):
        if prob == 0.0:
            break
        prob *= (n - k) / (k + 1) * (p / q)
        probs[k + 1] = prob
    return probs


def _binom_cdf_array(pmf: list[float]) -> list[float]:
    total = 0.0
    cdf: list[float] = []
    for prob in pmf:
        total += prob
        cdf.append(total)
    return cdf


def _binom_sf_array(pmf: list[float]) -> list[float]:
    total = 0.0
    sf = [0.0] * len(pmf)
    for idx in range(len(pmf) - 1, -1, -1):
        total += pmf[idx]
        sf[idx] = total
    return sf


def _critical_region_one_sided(n: int, p_null: float, alpha: float, tail: Tail) -> tuple[int, int]:
    pmf = _binom_pmf_array(n, p_null)
    cdf = _binom_cdf_array(pmf)
    sf = _binom_sf_array(pmf)
    if tail == "greater":
        for k in range(n + 1):
            if sf[k] <= alpha:
                return k, n
        return n + 1, n
    for k in range(n, -1, -1):
        if cdf[k] <= alpha:
            return 0, k
    return 0, -1


def _critical_region_two_sided(n: int, p_null: float, alpha: float) -> tuple[int, int]:
    pmf = _binom_pmf_array(n, p_null)
    cdf = _binom_cdf_array(pmf)
    sf = _binom_sf_array(pmf)
    lower_tail = alpha / 2.0
    upper_tail = alpha / 2.0
    low = -1
    for k in range(n + 1):
        if cdf[k] <= lower_tail:
            low = k
        else:
            break
    high = n + 1
    for k in range(n, -1, -1):
        if sf[k] <= upper_tail:
            high = k
        else:
            break
    return low, high


def _power_one_prop_exact(p: float, p_null: float, n: int, alpha: float, tail: Tail) -> float:
    if n > _MAX_EXACT:
        warnings.warn(
            "exact=True not feasible for n>200; falling back to normal approximation", 
            RuntimeWarning
        )
        # Fall back to normal approximation
        se = math.sqrt(p_null * (1.0 - p_null) / n)
        delta = p - p_null
        effect = delta / se
        return ncf.power_normal(effect, alpha, tail)
    
    pmf = _binom_pmf_array(n, p)
    if tail == "two-sided":
        low, high = _critical_region_two_sided(n, p_null, alpha)
        left = sum(pmf[: low + 1]) if low >= 0 else 0.0
        right = sum(pmf[high:]) if high <= n else 0.0
        return float(left + right)
    low, high = _critical_region_one_sided(n, p_null, alpha, tail)
    if tail == "greater":
        return float(sum(pmf[low:]))
    return float(sum(pmf[: high + 1]))


def _power_one_prop_equivalence_exact(
    p: float,
    p0: float,
    margin: float,
    n: int,
    alpha: float,
) -> float:
    if n > _MAX_EXACT:
        warnings.warn(
            "exact=True not feasible for n>200; falling back to normal approximation", 
            RuntimeWarning
        )
        # Fall back to normal approximation for equivalence
        se = math.sqrt(p0 * (1.0 - p0) / n)
        delta = p - p0
        return _equivalence_power(delta, se, alpha, margin)
    
    low_bound, _ = _critical_region_one_sided(n, p0 - margin, alpha, "greater")
    _, high_bound = _critical_region_one_sided(n, p0 + margin, alpha, "less")
    if low_bound > high_bound:
        return 0.0
    pmf = _binom_pmf_array(n, p)
    return float(sum(pmf[low_bound : high_bound + 1]))


def _hypergeom_prob(n1: int, n2: int, successes: int, x: int) -> float:
    if x < 0 or x > n1:
        return 0.0
    y = successes - x
    if y < 0 or y > n2:
        return 0.0
    numerator = math.comb(n1, x) * math.comb(n2, y)
    denominator = math.comb(n1 + n2, successes)
    return numerator / denominator


def _fisher_p_value(x1: int, n1: int, x2: int, n2: int, alternative: str) -> float:
    successes = x1 + x2
    x_min = max(0, successes - n2)
    x_max = min(n1, successes)
    probs = [_hypergeom_prob(n1, n2, successes, x) for x in range(x_min, x_max + 1)]
    observed = probs[x1 - x_min]
    if alternative == "two-sided":
        threshold = observed + 1e-12
        return float(sum(p for p in probs if p <= threshold))
    if alternative == "greater":
        idx = x1 - x_min
        return float(sum(probs[idx:]))
    idx = x1 - x_min
    return float(sum(probs[: idx + 1]))


def _power_two_prop_exact(
    p1: float,
    p2: float,
    n1: int,
    n2: int,
    alpha: float,
    tail: Tail,
) -> float:
    if n1 > _MAX_EXACT or n2 > _MAX_EXACT:
        warnings.warn(
            "exact=True not feasible for n>200; falling back to normal approximation", 
            RuntimeWarning
        )
        # Fall back to corrected normal approximation
        return _power_two_prop_corrected(p1, p2, n1, n2, alpha, tail)
    pmf1 = _binom_pmf_array(n1, p1)
    pmf2 = _binom_pmf_array(n2, p2)
    alternative = {"two-sided": "two-sided", "greater": "greater", "less": "less"}[tail]
    power = 0.0
    for x1, p_x1 in enumerate(pmf1):
        if p_x1 == 0.0:
            continue
        for x2, p_x2 in enumerate(pmf2):
            if p_x2 == 0.0:
                continue
            p_value = _fisher_p_value(x1, n1, x2, n2, alternative)
            if p_value <= alpha:
                power += p_x1 * p_x2
    return float(power)


def _power_score(delta: float, se: float, alpha: float, tail: Tail) -> float:
    effect = delta / se
    return ncf.power_normal(effect, alpha, tail)


def _equivalence_power(delta: float, se: float, alpha: float, margin: float) -> float:
    effect = delta / se
    q = normal.ppf(1.0 - alpha)
    lower = q - margin / se
    upper = -q + margin / se
    if lower >= upper:
        return 0.0
    return normal.cdf(upper - effect) - normal.cdf(lower - effect)


def _z_alpha(alpha: float, two_sided: bool) -> float:
    """Get critical z-value for alpha level."""
    a = alpha / 2.0 if two_sided else alpha
    return normal.ppf(1.0 - a)


def _z_beta(power: float) -> float:
    """Get z-value for power (1-beta)."""
    beta = 1.0 - power
    return normal.ppf(1.0 - beta)


def _round_up_even(x: float) -> int:
    """Round up to nearest integer, preserving library's rounding policy."""
    return int(math.ceil(x))


def _power_two_prop_corrected(
    p1: float, p2: float, n1: int, n2: int, alpha: float, tail: Tail
) -> float:
    """Two-proportion power using Fleiss method (matches G*Power/pwr)."""
    # Fleiss method used by G*Power and R's pwr package
    # Equal n assumed for this path; unequal handled elsewhere
    
    if n1 != n2:
        # Fall back to original method for unequal allocation
        total = n1 + n2
        pooled = (p1 * n1 + p2 * n2) / total
        se = math.sqrt(pooled * (1.0 - pooled) * (1.0 / n1 + 1.0 / n2))
        delta = p1 - p2
        effect = delta / se
        return ncf.power_normal(effect, alpha, tail)
    
    # Equal allocation: Fleiss method
    n = n1
    
    # Pooled proportion under H0: p1 = p2
    p_pooled = (p1 + p2) / 2.0
    
    # Standard errors
    se_null = math.sqrt(2.0 * p_pooled * (1.0 - p_pooled) / n)  # Under H0
    se_alt = math.sqrt((p1 * (1.0 - p1) + p2 * (1.0 - p2)) / n)  # Under H1
    
    delta = p1 - p2
    
    if tail == "two-sided":
        z_alpha = normal.ppf(1.0 - alpha / 2.0)
        # Critical region boundary
        crit = z_alpha * se_null
        # Power under H1
        z_effect = abs(delta) / se_alt
        power = normal.sf((crit - abs(delta)) / se_alt) + normal.cdf((-crit - abs(delta)) / se_alt)
    elif tail == "greater":
        z_alpha = normal.ppf(1.0 - alpha)
        crit = z_alpha * se_null
        z_effect = delta / se_alt
        power = normal.sf((crit - delta) / se_alt)
    else:  # "less"
        z_alpha = normal.ppf(alpha)
        crit = z_alpha * se_null
        z_effect = delta / se_alt
        power = normal.cdf((crit - delta) / se_alt)
    
    return float(power)


def n_one_sample_prop(
    p: float,
    p0: float,
    alpha: float = 0.05,
    power: float = 0.80,
    tail: Tail = "two-sided",
    exact: bool = False,
    ni_margin: float | None = None,
    ni_type: NIType | None = None,
) -> int:
    """Sample size for a single proportion test."""

    _validate_probability(p, "p")
    _validate_probability(p0, "p0")
    _validate_common(alpha, power, tail)
    _validate_margin(ni_margin, ni_type)
    if ni_type == "equivalence" and tail != "two-sided":
        raise ValueError("equivalence requires tail='two-sided'")
    if ni_type == "noninferiority" and tail == "two-sided":
        raise ValueError("noninferiority requires a one-sided tail")

    def evaluator(n: int) -> float:
        n_i = max(n, 2)
        se_null = math.sqrt(p0 * (1.0 - p0) / n_i)
        if exact:
            if ni_type is None:
                return _power_one_prop_exact(p, p0, n_i, alpha, tail)
            if ni_type == "noninferiority":
                assert ni_margin is not None
                null_prop = p0 - ni_margin if tail == "greater" else p0 + ni_margin
                return _power_one_prop_exact(p, null_prop, n_i, alpha, tail)
            assert ni_margin is not None
            return _power_one_prop_equivalence_exact(p, p0, ni_margin, n_i, alpha)
        delta = p - p0
        if ni_type is None:
            return _power_score(delta, se_null, alpha, tail)
        assert ni_margin is not None
        if ni_type == "noninferiority":
            shift = ni_margin if tail == "greater" else -ni_margin
            return _power_score(delta + shift, se_null, alpha, tail)
        return _equivalence_power(delta, se_null, alpha, ni_margin)

    n_final = solve.solve_monotone_int(evaluator, power, lower=2)
    
    # Add warning for dubious normal approximation if not using exact method
    if not exact:
        _check_one_sample_normal_approximation(p, p0, n_final)
    
    return max(n_final, 2)


def n_two_prop(
    p1: float,
    p2: float,
    alpha: float = 0.05,
    power: float = 0.80,
    ratio: float = 1.0,
    test: ZorT = "z",
    tail: Tail = "two-sided",
    ni_margin: float | None = None,
    ni_type: NIType | None = None,
    exact: bool = False,
) -> tuple[int, int]:
    """Two-sample proportion comparison sample sizes."""

    _validate_probability(p1, "p1")
    _validate_probability(p2, "p2")
    _validate_common(alpha, power, tail)
    _validate_margin(ni_margin, ni_type)
    alloc.validate_ratio(ratio)
    if test not in {"z", "t"}:
        raise ValueError("test must be 'z' or 't'")
    if ni_type == "equivalence" and tail != "two-sided":
        raise ValueError("equivalence requires tail='two-sided'")
    if ni_type == "noninferiority" and tail == "two-sided":
        raise ValueError("noninferiority requires one-sided tail")
    if exact and ni_type is not None:
        raise NotImplementedError(
            "exact=True with NI/equivalence is not supported; use normal approximation"
        )

    def evaluator(n1: int) -> float:
        n1i = max(n1, 2)
        n1i, n2i = alloc.groups_from_n1(n1i, ratio)
        if exact:
            return _power_two_prop_exact(p1, p2, n1i, n2i, alpha, tail)
        
        if ni_type is None:
            # Use corrected H0/H1 variance calculation
            return _power_two_prop_corrected(p1, p2, n1i, n2i, alpha, tail)
        
        # For NI/equivalence, use original pooled calculation for compatibility
        total = n1i + n2i
        pooled = (p1 * n1i + p2 * n2i) / total
        se = math.sqrt(pooled * (1.0 - pooled) * (1.0 / n1i + 1.0 / n2i))
        delta = p1 - p2
        assert ni_margin is not None
        if ni_type == "noninferiority":
            shift = ni_margin if tail == "greater" else -ni_margin
            return _power_score(delta + shift, se, alpha, tail)
        return _equivalence_power(delta, se, alpha, ni_margin)

    n1_final = solve.solve_monotone_int(evaluator, power, lower=2)
    n1_final, n2_final = alloc.groups_from_n1(n1_final, ratio)
    
    # Add warnings for dubious normal approximation if not using exact method
    if not exact:
        _check_normal_approximation_validity(p1, p2, n1_final, n2_final)
    
    return max(n1_final, 2), max(n2_final, 2)
