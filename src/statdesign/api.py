"""Public API for statdesign."""

from __future__ import annotations

from typing import Literal, Optional, Tuple

from .endpoints.anova import n_anova as _n_anova
from .endpoints.means import (
    n_mean as _n_mean,
)
from .endpoints.means import (
    n_one_sample_mean as _n_one_sample_mean,
)
from .endpoints.means import (
    n_paired as _n_paired,
)
from .endpoints.proportions import (
    n_one_sample_prop as _n_one_sample_prop,
)
from .endpoints.proportions import (
    n_two_prop as _n_two_prop,
)
from .multiplicity import alpha_adjust as _alpha_adjust
from .multiplicity import bh_thresholds as _bh_thresholds

Tail = Literal["two-sided", "greater", "less"]
ZorT = Literal["z", "t"]
NIType = Literal["noninferiority", "equivalence"]


def n_two_prop(
    p1: float,
    p2: float,
    alpha: float = 0.05,
    power: float = 0.80,
    ratio: float = 1.0,
    test: ZorT = "z",
    tail: Tail = "two-sided",
    ni_margin: Optional[float] = None,
    ni_type: Optional[NIType] = None,
    exact: bool = False,
) -> Tuple[int, int]:
    """Return (n1, n2) for two-proportion comparison.

    Parameters mirror :func:`statdesign.endpoints.proportions.n_two_prop`.
    """

    return _n_two_prop(
        p1=p1,
        p2=p2,
        alpha=alpha,
        power=power,
        ratio=ratio,
        test=test,
        tail=tail,
        ni_margin=ni_margin,
        ni_type=ni_type,
        exact=exact,
    )


def n_mean(
    mu1: float,
    mu2: float,
    sd: float,
    alpha: float = 0.05,
    power: float = 0.80,
    ratio: float = 1.0,
    test: ZorT = "t",
    tail: Tail = "two-sided",
    ni_margin: Optional[float] = None,
    ni_type: Optional[NIType] = None,
) -> Tuple[int, int]:
    """Two-sample mean comparison with optional NI/equivalence."""

    return _n_mean(
        mu1=mu1,
        mu2=mu2,
        sd=sd,
        alpha=alpha,
        power=power,
        ratio=ratio,
        test=test,
        tail=tail,
        ni_margin=ni_margin,
        ni_type=ni_type,
    )


def n_paired(
    delta: float,
    sd_diff: float,
    alpha: float = 0.05,
    power: float = 0.80,
    tail: Tail = "two-sided",
    ni_margin: Optional[float] = None,
    ni_type: Optional[NIType] = None,
) -> int:
    """Paired t design for mean differences."""

    return _n_paired(
        delta=delta,
        sd_diff=sd_diff,
        alpha=alpha,
        power=power,
        tail=tail,
        ni_margin=ni_margin,
        ni_type=ni_type,
    )


def n_one_sample_mean(
    delta: float,
    sd: float,
    alpha: float = 0.05,
    power: float = 0.80,
    tail: Tail = "two-sided",
    test: ZorT = "t",
    ni_margin: Optional[float] = None,
    ni_type: Optional[NIType] = None,
) -> int:
    """Sample size for a one-sample mean test."""

    return _n_one_sample_mean(
        delta=delta,
        sd=sd,
        alpha=alpha,
        power=power,
        tail=tail,
        test=test,
        ni_margin=ni_margin,
        ni_type=ni_type,
    )


def n_one_sample_prop(
    p: float,
    p0: float,
    alpha: float = 0.05,
    power: float = 0.80,
    tail: Tail = "two-sided",
    exact: bool = False,
    ni_margin: Optional[float] = None,
    ni_type: Optional[NIType] = None,
) -> int:
    """Sample size for a one-sample binomial test."""

    return _n_one_sample_prop(
        p=p,
        p0=p0,
        alpha=alpha,
        power=power,
        tail=tail,
        exact=exact,
        ni_margin=ni_margin,
        ni_type=ni_type,
    )


def n_anova(
    k_groups: int,
    effect_f: float,
    alpha: float = 0.05,
    power: float = 0.80,
    allocation: Optional[list[float]] = None,
) -> int:
    """One-way ANOVA detecting Cohen's ``f`` with optional allocation weights."""

    return _n_anova(
        k_groups=k_groups,
        effect_f=effect_f,
        alpha=alpha,
        power=power,
        allocation=allocation,
    )


def alpha_adjust(
    m: int, alpha: float = 0.05, method: Literal["bonferroni", "bh"] = "bonferroni"
) -> float:
    """Return per-comparison alpha for Bonferroni or BH adjustments."""

    return _alpha_adjust(m=m, alpha=alpha, method=method)


def bh_thresholds(m: int, alpha: float = 0.05) -> list[float]:
    """Return BH step-up critical values ``alpha * i / m``."""

    return _bh_thresholds(m=m, alpha=alpha)


__all__ = [
    "Tail",
    "ZorT",
    "NIType",
    "n_two_prop",
    "n_mean",
    "n_paired",
    "n_one_sample_mean",
    "n_one_sample_prop",
    "n_anova",
    "alpha_adjust",
    "bh_thresholds",
]
