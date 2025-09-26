"""Accrual and dropout utilities for exponential survival models."""

from __future__ import annotations

import math
from typing import Literal

EntryDistribution = Literal["uniform", "instant"]


def _validate_inputs(
    lambda_event: float,
    lambda_dropout: float,
    accrual_years: float,
    followup_years: float,
    entry_distribution: EntryDistribution,
) -> None:
    if lambda_event < 0:
        raise ValueError("event hazard must be non-negative")
    if lambda_dropout < 0:
        raise ValueError("dropout hazard must be non-negative")
    if accrual_years < 0:
        raise ValueError("accrual_years must be non-negative")
    if followup_years < 0:
        raise ValueError("followup_years must be non-negative")
    if entry_distribution not in {"uniform", "instant"}:
        raise ValueError("entry_distribution must be 'uniform' or 'instant'")
    if entry_distribution == "uniform" and accrual_years <= 0:
        raise ValueError("uniform entry requires accrual_years > 0")


def event_probability_uniform(
    lambda_event: float,
    lambda_dropout: float,
    accrual_years: float,
    followup_years: float,
) -> float:
    if lambda_event == 0.0:
        return 0.0
    lambda_total = lambda_event + lambda_dropout
    if lambda_total == 0.0:
        return 0.0
    total_time = accrual_years + followup_years
    exp_T = math.exp(-lambda_total * total_time)
    exp_F = math.exp(-lambda_total * followup_years)
    term = accrual_years + (exp_T - exp_F) / lambda_total
    return (lambda_event / (lambda_total * accrual_years)) * term


def event_probability_instant(
    lambda_event: float,
    lambda_dropout: float,
    total_follow_years: float,
) -> float:
    if lambda_event == 0.0:
        return 0.0
    lambda_total = lambda_event + lambda_dropout
    if lambda_total == 0.0:
        return 0.0
    return (lambda_event / lambda_total) * (1.0 - math.exp(-lambda_total * total_follow_years))


def event_prob_exponential(
    lambda_event: float,
    lambda_dropout: float,
    accrual_years: float,
    followup_years: float,
    entry_distribution: EntryDistribution,
) -> float:
    _validate_inputs(
        lambda_event, lambda_dropout, accrual_years, followup_years, entry_distribution
    )
    if entry_distribution == "instant":
        total_follow = accrual_years + followup_years
        return event_probability_instant(lambda_event, lambda_dropout, total_follow)
    return event_probability_uniform(lambda_event, lambda_dropout, accrual_years, followup_years)


__all__ = ["event_prob_exponential"]
