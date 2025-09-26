"""statdesign: deterministic power and sample size calculations."""

from __future__ import annotations

from importlib import metadata as _metadata

try:
    __version__ = _metadata.version("statdesign")
except _metadata.PackageNotFoundError:  # pragma: no cover - during local dev
    __version__ = "0.0.0"

from .api import (  # noqa: E402 - re-export public API
    EntryDistribution,
    NIType,
    Tail,
    ZorT,
    alpha_adjust,
    bh_thresholds,
    design_effect_cluster_equal,
    design_effect_cluster_unequal,
    design_effect_repeated_cs,
    events_to_n_exponential,
    inflate_n_by_de,
    n_anova,
    n_mean,
    n_one_sample_mean,
    n_one_sample_prop,
    n_paired,
    n_two_prop,
    power_logrank_from_n,
    required_events_cox,
    required_events_logrank,
)

__all__ = [
    "__version__",
    "EntryDistribution",
    "Tail",
    "ZorT",
    "NIType",
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

