"""Multiple-testing adjustments."""

from __future__ import annotations

from typing import Literal

Method = Literal["bonferroni", "bh"]


def _validate_inputs(m: int, alpha: float) -> None:
    if m < 1:
        raise ValueError("m must be at least 1")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0, 1)")


def alpha_adjust(m: int, alpha: float = 0.05, method: Method = "bonferroni") -> float:
    """Return adjusted per-comparison alpha.

    For Bonferroni, this is the familiar ``alpha / m``. For Benjamini–Hochberg
    (BH), the function returns the smallest critical value (``alpha / m``); use
    :func:`bh_thresholds` to obtain the full sequence used in the step-up
    procedure.
    """

    _validate_inputs(m, alpha)
    if method == "bonferroni":
        return alpha / m
    if method == "bh":
        return alpha / m
    raise ValueError("method must be 'bonferroni' or 'bh'")


def bh_thresholds(m: int, alpha: float = 0.05) -> list[float]:
    """Return the BH step-up critical values ``alpha * i / m`` for ``i=1..m``."""

    _validate_inputs(m, alpha)
    return [alpha * (i + 1) / m for i in range(m)]
