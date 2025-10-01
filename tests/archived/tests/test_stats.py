from __future__ import annotations

import numpy as np

from src.utils import stats


def test_bh_monotonic():
    p = [0.001, 0.01, 0.05, 0.2]
    adj = stats.benjamini_hochberg(p)
    assert np.all(np.diff(adj) >= -1e-9)
    assert adj[0] <= adj[-1]


def test_ivw_simple():
    bx = np.array([0.2, 0.3, 0.4])
    by = np.array([0.1, 0.12, 0.15])
    se = np.array([0.05, 0.06, 0.04])
    result = stats.inverse_variance_weighted(bx, by, se)
    assert result.se > 0
    assert 0 < result.p_value <= 1


def test_mr_egger_shapes():
    bx = np.array([0.2, 0.3, 0.4, 0.5])
    by = np.array([0.12, 0.11, 0.13, 0.2])
    se = np.full_like(bx, 0.05)
    slope, intercept = stats.mr_egger(bx, by, se)
    assert isinstance(slope.beta, float)
    assert isinstance(intercept.se, float)
