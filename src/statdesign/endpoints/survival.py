"""Survival analysis sample size and power endpoints."""

from __future__ import annotations

import math
from typing import Literal

from ..core import accrual, survival_math

Tail = Literal["two-sided", "greater", "less"]
EntryDistribution = Literal["uniform", "instant"]


def _validate_allocation(allocation: float) -> None:
    if not 0 < allocation < 1:
        raise ValueError("allocation must be in (0, 1)")


def required_events_logrank(
    hr: float,
    alpha: float = 0.05,
    power: float = 0.80,
    allocation: float = 0.5,
    tail: Tail = "two-sided",
) -> float:
    """Return required total number of events for a log-rank test."""

    _validate_allocation(allocation)
    return survival_math.required_events_logrank(
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
    """Return required total events for a Cox proportional hazards test."""

    return survival_math.required_events_cox(
        log_hr=log_hr,
        var_x=var_x,
        alpha=alpha,
        power=power,
        tail=tail,
    )


def _event_probability(
    hazard: float,
    dropout_hazard: float,
    accrual_years: float,
    followup_years: float,
    entry_distribution: EntryDistribution,
) -> float:
    return accrual.event_prob_exponential(
        lambda_event=hazard,
        lambda_dropout=dropout_hazard,
        accrual_years=accrual_years,
        followup_years=followup_years,
        entry_distribution=entry_distribution,
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
    """Convert required events to sample size under exponential hazards."""

    if events_required < 0:
        raise ValueError("events_required must be non-negative")
    if events_required == 0:
        return 0, 0, 0
    if base_hazard_ctrl <= 0:
        raise ValueError("base_hazard_ctrl must be positive")
    if hr <= 0:
        raise ValueError("hr must be positive")
    if dropout_hazard < 0:
        raise ValueError("dropout_hazard must be non-negative")
    _validate_allocation(allocation)
    hazard_ctrl = base_hazard_ctrl
    hazard_exp = base_hazard_ctrl * hr

    p_event_exp = _event_probability(
        hazard_exp, dropout_hazard, accrual_years, followup_years, entry_distribution
    )
    p_event_ctrl = _event_probability(
        hazard_ctrl, dropout_hazard, accrual_years, followup_years, entry_distribution
    )

    if p_event_exp < 0 or p_event_ctrl < 0:
        raise ValueError("computed event probability negative; check inputs")
    total_event_prob = allocation * p_event_exp + (1.0 - allocation) * p_event_ctrl
    if total_event_prob <= 0:
        raise ValueError("event probability is zero; cannot determine sample size")

    n_total = int(math.ceil(events_required / total_event_prob))
    n_exp = int(math.ceil(allocation * n_total))
    n_ctrl = n_total - n_exp
    if n_ctrl < 0:
        n_ctrl = 0
    return n_total, n_exp, n_ctrl


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
    """Compute log-rank power implied by a design."""

    if n_exp < 0 or n_ctrl < 0:
        raise ValueError("sample sizes must be non-negative")
    total = n_exp + n_ctrl
    if total == 0:
        return 0.0
    if base_hazard_ctrl <= 0:
        raise ValueError("base_hazard_ctrl must be positive")
    if hr <= 0 or hr == 1.0:
        raise ValueError("hr must be positive and not equal to 1")
    if dropout_hazard < 0:
        raise ValueError("dropout_hazard must be non-negative")

    hazard_ctrl = base_hazard_ctrl
    hazard_exp = base_hazard_ctrl * hr

    p_event_exp = _event_probability(
        hazard_exp, dropout_hazard, accrual_years, followup_years, entry_distribution
    )
    p_event_ctrl = _event_probability(
        hazard_ctrl, dropout_hazard, accrual_years, followup_years, entry_distribution
    )
    events = n_exp * p_event_exp + n_ctrl * p_event_ctrl
    allocation = n_exp / total if total else 0.5
    return survival_math.power_from_events(hr, events, allocation, alpha, tail)


__all__ = [
    "required_events_logrank",
    "required_events_cox",
    "events_to_n_exponential",
    "power_logrank_from_n",
]
