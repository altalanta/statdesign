"""statdesign: deterministic power and sample size calculations."""

from __future__ import annotations

from .api import (
    NIType,
    Tail,
    ZorT,
    alpha_adjust,
    bh_thresholds,
    n_anova,
    n_mean,
    n_one_sample_mean,
    n_one_sample_prop,
    n_paired,
    n_two_prop,
)

__all__ = [
    "__version__",
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

__version__ = "0.3.0"
