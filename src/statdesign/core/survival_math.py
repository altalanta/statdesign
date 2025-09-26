"""Survival power and sample size utilities."""

from __future__ import annotations

import math
from typing import Literal

from . import normal

Tail = Literal["two-sided", "greater", "less"]


def _validate_tail(tail: Tail) -> None:
    if tail not in {"two-sided", "greater", "less"}:
        raise ValueError(f"unsupported tail specification: {tail}")


def _z_alpha(alpha: float, tail: Tail) -> float:
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0, 1)")
    _validate_tail(tail)
    if tail == "two-sided":
        return normal.ppf(1.0 - alpha / 2.0)
    return normal.ppf(1.0 - alpha)


def _info(events: float, allocation: float, abs_log_hr: float) -> float:
    if events < 0:
        raise ValueError("events must be non-negative")
    if not 0 < allocation < 1:
        raise ValueError("allocation must be between 0 and 1")
    return events * allocation * (1.0 - allocation) * (abs_log_hr**2)


def required_events_logrank(
    hr: float,
    alpha: float,
    power: float,
    allocation: float,
    tail: Tail,
) -> float:
    if hr <= 0 or hr == 1.0:
        raise ValueError("hr must be positive and not equal to 1")
    if not 0 < power < 1:
        raise ValueError("power must be in (0, 1)")
    if not 0 < allocation < 1:
        raise ValueError("allocation must be in (0, 1)")
    _validate_tail(tail)
    if tail == "greater" and hr >= 1.0:
        raise ValueError("tail='greater' expects hr < 1")
    if tail == "less" and hr <= 1.0:
        raise ValueError("tail='less' expects hr > 1")

    z_alpha = _z_alpha(alpha, tail)
    z_beta = normal.ppf(power)
    abs_log = abs(math.log(hr))
    if abs_log == 0.0:
        raise ValueError("log hazard ratio must be non-zero")
    return ((z_alpha + z_beta) ** 2) / (abs_log**2 * allocation * (1.0 - allocation))


def required_events_cox(
    log_hr: float,
    var_x: float,
    alpha: float,
    power: float,
    tail: Tail,
) -> float:
    if log_hr == 0.0:
        raise ValueError("log_hr must be non-zero")
    if tail == "greater" and log_hr >= 0.0:
        raise ValueError("tail='greater' expects log_hr < 0")
    if tail == "less" and log_hr <= 0.0:
        raise ValueError("tail='less' expects log_hr > 0")
    if var_x <= 0:
        raise ValueError("var_x must be positive")
    if not 0 < power < 1:
        raise ValueError("power must be in (0, 1)")
    z_alpha = _z_alpha(alpha, tail)
    z_beta = normal.ppf(power)
    return ((z_alpha + z_beta) ** 2) * var_x / (log_hr**2)


def power_from_events(
    hr: float,
    events: float,
    allocation: float,
    alpha: float,
    tail: Tail,
) -> float:
    if events < 0:
        raise ValueError("events must be non-negative")
    if hr <= 0 or hr == 1.0:
        raise ValueError("hr must be positive and not equal to 1")
    if not 0 < allocation < 1:
        raise ValueError("allocation must be in (0, 1)")
    _validate_tail(tail)
    if tail == "greater" and hr >= 1.0:
        raise ValueError("tail='greater' expects hr < 1")
    if tail == "less" and hr <= 1.0:
        raise ValueError("tail='less' expects hr > 1")
    if events == 0:
        return 0.0

    abs_log = abs(math.log(hr))
    info = _info(events, allocation, abs_log)
    if info == 0.0:
        return 0.0
    sqrt_info = math.sqrt(info)
    z_alpha = _z_alpha(alpha, tail)
    mean = sqrt_info
    if tail == "two-sided":
        upper = normal.sf(z_alpha - mean)
        lower = normal.cdf(-z_alpha - mean)
        return float(upper + lower)
    return float(normal.cdf(sqrt_info - z_alpha))


__all__ = [
    "required_events_logrank",
    "required_events_cox",
    "power_from_events",
]
