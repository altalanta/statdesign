from statdesign import api
from statdesign.multiplicity import bh_thresholds


def test_bonferroni() -> None:
    assert api.alpha_adjust(m=5, alpha=0.05, method="bonferroni") == 0.01


def test_bh_smallest_threshold() -> None:
    assert api.alpha_adjust(m=10, alpha=0.05, method="bh") == 0.005


def test_bh_thresholds_sequence() -> None:
    thresholds = bh_thresholds(4, alpha=0.04)
    assert thresholds == [0.01, 0.02, 0.03, 0.04]
