"""Reproducible survival simulations for design verification."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

try:
    import numpy as np
except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency
    raise RuntimeError(
        "simulate_logrank_power requires numpy; install statdesign[full] or add numpy\n"
        "to your environment."
    ) from exc


from ..core import normal

Tail = Literal["two-sided", "greater", "less"]
EntryDistribution = Literal["uniform", "instant"]


@dataclass
class SurvivalDesign:
    n_exp: int
    n_ctrl: int
    accrual_years: float
    followup_years: float
    base_hazard_ctrl: float
    hr: float
    dropout_hazard: float = 0.0
    entry_distribution: EntryDistribution = "uniform"
    alpha: float = 0.05
    tail: Tail = "two-sided"


def _sample_entry(rng: np.random.Generator, design: SurvivalDesign, size: int) -> np.ndarray:
    if design.entry_distribution == "instant":
        return np.zeros(size)
    if design.accrual_years <= 0:
        raise ValueError("uniform entry requires accrual_years > 0")
    return rng.uniform(0.0, design.accrual_years, size=size)


def _sample_wait(rng: np.random.Generator, hazard: float, size: int) -> np.ndarray:
    if hazard == 0.0:
        return np.full(size, np.inf)
    return rng.exponential(1.0 / hazard, size=size)


def _simulate_arm(
    rng: np.random.Generator,
    n: int,
    hazard: float,
    design: SurvivalDesign,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    entry = _sample_entry(rng, design, n)
    study_end = design.accrual_years + design.followup_years
    follow_time = np.clip(study_end - entry, a_min=0.0, a_max=None)

    event_wait = _sample_wait(rng, hazard, n)
    dropout_wait = _sample_wait(rng, design.dropout_hazard, n)
    observed_wait = np.minimum(np.minimum(event_wait, dropout_wait), follow_time)
    event_indicator = (event_wait <= dropout_wait) & (event_wait <= follow_time)

    calendar_time = entry + observed_wait
    return calendar_time, event_indicator.astype(float), entry


def _logrank_stat(times: np.ndarray, events: np.ndarray, groups: np.ndarray) -> float:
    order = np.argsort(times)
    times_sorted = times[order]
    events_sorted = events[order]
    groups_sorted = groups[order]

    event_times = times_sorted[events_sorted == 1.0]
    if event_times.size == 0:
        return 0.0
    unique_times = np.unique(event_times)

    obs_minus_exp = 0.0
    var_sum = 0.0
    for t in unique_times:
        at_risk = times_sorted >= (t - 1e-12)
        n_total = at_risk.sum()
        if n_total <= 1:
            continue
        n_exp = np.count_nonzero(groups_sorted[at_risk])
        events_at_t = (np.abs(times_sorted - t) < 1e-12) & (events_sorted == 1.0)
        d_total = events_at_t.sum()
        if d_total == 0:
            continue
        d_exp = np.count_nonzero(groups_sorted[events_at_t])
        frac = n_exp / n_total
        expected = d_total * frac
        variance = d_total * frac * (1.0 - frac)
        variance *= (n_total - d_total) / (n_total - 1.0)
        obs_minus_exp += d_exp - expected
        var_sum += variance
    if var_sum <= 0:
        return 0.0
    return float(obs_minus_exp / math.sqrt(var_sum))


def _z_alpha(alpha: float, tail: Tail) -> float:
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0, 1)")
    if tail == "two-sided":
        return normal.ppf(1.0 - alpha / 2.0)
    if tail in {"greater", "less"}:
        return normal.ppf(1.0 - alpha)
    raise ValueError(f"unsupported tail: {tail}")


def _check_tail_hr(hr: float, tail: Tail) -> None:
    if tail == "greater" and hr >= 1.0:
        raise ValueError("tail='greater' expects hr < 1")
    if tail == "less" and hr <= 1.0:
        raise ValueError("tail='less' expects hr > 1")


def simulate_logrank_power(
    design: SurvivalDesign,
    reps: int = 2000,
    seed: int | None = 12345,
) -> float:
    """Monte Carlo estimate of log-rank power under exponential hazards."""

    if reps <= 0:
        raise ValueError("reps must be positive")
    if design.n_exp < 0 or design.n_ctrl < 0:
        raise ValueError("sample sizes must be non-negative")
    if design.base_hazard_ctrl <= 0:
        raise ValueError("base_hazard_ctrl must be positive")
    if design.hr <= 0 or design.hr == 1.0:
        raise ValueError("hr must be positive and not equal to 1")
    if design.dropout_hazard < 0:
        raise ValueError("dropout_hazard must be non-negative")
    if design.entry_distribution not in {"uniform", "instant"}:
        raise ValueError("entry_distribution must be 'uniform' or 'instant'")

    _check_tail_hr(design.hr, design.tail)

    rng = np.random.default_rng(seed)
    hazard_ctrl = design.base_hazard_ctrl
    hazard_exp = design.base_hazard_ctrl * design.hr
    z_crit = _z_alpha(design.alpha, design.tail)

    rejections = 0
    total = design.n_exp + design.n_ctrl
    if total == 0:
        return 0.0

    for _ in range(reps):
        times_exp, events_exp, _ = _simulate_arm(rng, design.n_exp, hazard_exp, design)
        times_ctrl, events_ctrl, _ = _simulate_arm(rng, design.n_ctrl, hazard_ctrl, design)

        times = np.concatenate([times_exp, times_ctrl])
        events = np.concatenate([events_exp, events_ctrl])
        groups = np.concatenate([np.ones(design.n_exp), np.zeros(design.n_ctrl)])

        z = _logrank_stat(times, events, groups)
        if design.tail == "two-sided":
            reject = abs(z) > z_crit
        elif design.tail == "greater":
            reject = z < -z_crit
        else:  # tail == "less"
            reject = z > z_crit
        rejections += int(reject)

    return rejections / reps


__all__ = ["SurvivalDesign", "simulate_logrank_power"]
