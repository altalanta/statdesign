"""Public API for statdesign."""

from __future__ import annotations

from typing import Literal

from .endpoints.anova import n_anova as _n_anova
from .endpoints.design_effects import (
    design_effect_cluster_equal as _design_effect_cluster_equal,
)
from .endpoints.design_effects import (
    design_effect_cluster_unequal as _design_effect_cluster_unequal,
)
from .endpoints.design_effects import (
    design_effect_repeated_cs as _design_effect_repeated_cs,
)
from .endpoints.design_effects import (
    inflate_n_by_de as _inflate_n_by_de,
)
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
from .endpoints.survival import (
    events_to_n_exponential as _events_to_n_exponential,
)
from .endpoints.survival import (
    power_logrank_from_n as _power_logrank_from_n,
)
from .endpoints.survival import (
    required_events_cox as _required_events_cox,
)
from .endpoints.survival import (
    required_events_logrank as _required_events_logrank,
)
from .multiplicity import alpha_adjust as _alpha_adjust
from .multiplicity import bh_thresholds as _bh_thresholds

Tail = Literal["two-sided", "greater", "less"]
ZorT = Literal["z", "t"]
NIType = Literal["noninferiority", "equivalence"]
EntryDistribution = Literal["uniform", "instant"]


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
    ni_margin: float | None = None,
    ni_type: NIType | None = None,
) -> tuple[int, int]:
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
    ni_margin: float | None = None,
    ni_type: NIType | None = None,
) -> int:
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
    ni_margin: float | None = None,
    ni_type: NIType | None = None,
) -> int:
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
    ni_margin: float | None = None,
    ni_type: NIType | None = None,
) -> int:
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
    allocation: list[float] | None = None,
) -> int:
    return _n_anova(
        k_groups=k_groups,
        effect_f=effect_f,
        alpha=alpha,
        power=power,
        allocation=allocation,
    )


def required_events_logrank(
    hr: float,
    alpha: float = 0.05,
    power: float = 0.80,
    allocation: float = 0.5,
    tail: Tail = "two-sided",
) -> float:
    return _required_events_logrank(
        hr=hr,
        alpha=alpha,
        power=power,
        allocation=allocation,
        tail=tail,
    )


def required_events_cox(
    log_hr: float,
    var_x: float,
    alpha: float = 0.05,
    power: float = 0.80,
    tail: Tail = "two-sided",
) -> float:
    return _required_events_cox(
        log_hr=log_hr,
        var_x=var_x,
        alpha=alpha,
        power=power,
        tail=tail,
    )


def events_to_n_exponential(
    events_required: float,
    accrual_years: float,
    followup_years: float,
    base_hazard_ctrl: float,
    hr: float,
    allocation: float = 0.5,
    dropout_hazard: float = 0.0,
    entry_distribution: EntryDistribution = "uniform",
) -> tuple[int, int, int]:
    return _events_to_n_exponential(
        events_required=events_required,
        accrual_years=accrual_years,
        followup_years=followup_years,
        base_hazard_ctrl=base_hazard_ctrl,
        hr=hr,
        allocation=allocation,
        dropout_hazard=dropout_hazard,
        entry_distribution=entry_distribution,
    )


def power_logrank_from_n(
    hr: float,
    n_exp: int,
    n_ctrl: int,
    accrual_years: float,
    followup_years: float,
    base_hazard_ctrl: float,
    dropout_hazard: float = 0.0,
    entry_distribution: EntryDistribution = "uniform",
    alpha: float = 0.05,
    tail: Tail = "two-sided",
) -> float:
    return _power_logrank_from_n(
        hr=hr,
        n_exp=n_exp,
        n_ctrl=n_ctrl,
        accrual_years=accrual_years,
        followup_years=followup_years,
        base_hazard_ctrl=base_hazard_ctrl,
        dropout_hazard=dropout_hazard,
        entry_distribution=entry_distribution,
        alpha=alpha,
        tail=tail,
    )


def design_effect_cluster_equal(m: float, icc: float) -> float:
    return _design_effect_cluster_equal(m=m, icc=icc)


def design_effect_cluster_unequal(mbar: float, icc: float, cv: float) -> float:
    return _design_effect_cluster_unequal(mbar=mbar, icc=icc, cv=cv)


def design_effect_repeated_cs(k: int, icc: float) -> float:
    return _design_effect_repeated_cs(k=k, icc=icc)


def inflate_n_by_de(n_individuals: int, de: float) -> int:
    return _inflate_n_by_de(n_individuals=n_individuals, de=de)


def alpha_adjust(
    m: int, alpha: float = 0.05, method: Literal["bonferroni", "bh"] = "bonferroni"
) -> float:
    return _alpha_adjust(m=m, alpha=alpha, method=method)


def bh_thresholds(m: int, alpha: float = 0.05) -> list[float]:
    return _bh_thresholds(m=m, alpha=alpha)


__all__ = [
    "Tail",
    "ZorT",
    "NIType",
    "EntryDistribution",
    "n_two_prop",
    "n_mean",
    "n_paired",
    "n_one_sample_mean",
    "n_one_sample_prop",
    "n_anova",
    "required_events_logrank",
    "required_events_cox",
    "events_to_n_exponential",
    "power_logrank_from_n",
    "design_effect_cluster_equal",
    "design_effect_cluster_unequal",
    "design_effect_repeated_cs",
    "inflate_n_by_de",
    "alpha_adjust",
    "bh_thresholds",
]
