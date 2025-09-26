"""One-way ANOVA sample size calculations.

The implementation uses the noncentral :math:`F` distribution when SciPy support
is activated via ``STATDESIGN_AUTO_SCIPY=1``. Otherwise it falls back to a
normal approximation on the noncentrality parameter, which is accurate for the
moderate-to-large sample sizes typically encountered in practice but can be
slightly conservative near the detection boundary.
"""

from __future__ import annotations

from collections.abc import Iterable

from ..core import alloc, ncf, solve


def _validate_inputs(k_groups: int, effect_f: float, alpha: float, power: float) -> None:
    if k_groups < 2:
        raise ValueError("k_groups must be at least 2")
    if effect_f <= 0:
        raise ValueError("effect_f must be positive")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0, 1)")
    if not 0 < power < 1:
        raise ValueError("power must be in (0, 1)")


def _normalize_allocation(k_groups: int, allocation: Iterable[float] | None) -> list[float]:
    if allocation is None:
        return [1.0] * k_groups
    weights = list(allocation)
    if len(weights) != k_groups:
        raise ValueError("allocation length must match k_groups")
    if any(w <= 0 for w in weights):
        raise ValueError("allocation weights must be positive")
    return weights


def n_anova(
    k_groups: int,
    effect_f: float,
    alpha: float = 0.05,
    power: float = 0.80,
    allocation: list[float] | None = None,
) -> int:
    """Return total sample size for one-way ANOVA detecting Cohen's ``f``.

    The returned total uses the exact noncentral :math:`F` distribution when
    SciPy is active and otherwise relies on a normal approximation for the
    noncentrality parameter. Setting ``STATDESIGN_AUTO_SCIPY=1`` in an
    environment with SciPy installed restores the exact path.
    """

    _validate_inputs(k_groups, effect_f, alpha, power)
    weights = _normalize_allocation(k_groups, allocation)

    def evaluator(total: int) -> float:
        total_i = max(total, k_groups * 2)
        group_sizes = alloc.allocate_by_weights(total_i, weights)
        if min(group_sizes) < 2:
            return 0.0
        n_total = sum(group_sizes)
        df_num = k_groups - 1
        df_den = n_total - k_groups
        if df_den <= 0:
            return 0.0
        n_harmonic = alloc.harmonic_mean(group_sizes)
        lambda_ = (n_harmonic * k_groups) * (effect_f ** 2)
        return ncf.power_noncentral_f(lambda_, df_num, df_den, alpha)

    lower = k_groups * 2
    n_total = solve.solve_monotone_int(evaluator, power, lower=lower)
    return max(n_total, lower)


__all__ = ["n_anova"]
