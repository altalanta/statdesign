from __future__ import annotations

import pytest

hypothesis = pytest.importorskip("hypothesis")

# Conditional imports after importorskip  # type: ignore  # pragma: no cover
if hypothesis:
    import hypothesis.strategies as st  # type: ignore  # pragma: no cover
    from hypothesis import assume, given, settings  # type: ignore  # pragma: no cover

    from statdesign import api
    from statdesign.core import ncf

_power = st.floats(min_value=0.51, max_value=0.93)
_ratio = st.floats(min_value=0.25, max_value=3.0)
_prop = st.floats(min_value=0.05, max_value=0.95)


@settings(deadline=None, max_examples=50)
@given(
    p1=_prop,
    delta=st.floats(min_value=0.05, max_value=0.4),
    power=_power,
    ratio=_ratio,
)
def test_two_prop_power_monotone(p1: float, delta: float, power: float, ratio: float) -> None:
    """Higher target power should never require fewer samples."""

    p2 = p1 - delta if p1 > 0.5 else p1 + delta
    assume(0.0 < p2 < 1.0)
    low_power = max(0.5, power)
    high_power = min(0.99, low_power + 0.05)
    n_low = api.n_two_prop(p1=p1, p2=p2, power=low_power, ratio=ratio)
    n_high = api.n_two_prop(p1=p1, p2=p2, power=high_power, ratio=ratio)
    assert n_high[0] >= n_low[0]
    assert n_high[1] >= n_low[1]


@settings(deadline=None, max_examples=30)
@given(
    delta=st.floats(min_value=0.1, max_value=1.0),
    sd=st.floats(min_value=0.2, max_value=3.0),
    power=_power,
)
def test_one_sample_mean_power_monotone(delta: float, sd: float, power: float) -> None:
    """Increasing target power for one-sample mean increases ``n``."""

    low_power = max(0.5, power)
    high_power = min(0.99, low_power + 0.1)
    n_low = api.n_one_sample_mean(delta=delta, sd=sd, power=low_power)
    n_high = api.n_one_sample_mean(delta=delta, sd=sd, power=high_power)
    assert n_high >= n_low


def test_t_fallback_conservative() -> None:
    """Normal-approximation fallback should be conservative compared to z-path."""

    if ncf.has_scipy():
        return  # SciPy path active; fallback exercised in dedicated tests
    result_t = api.n_mean(mu1=0.0, mu2=0.5, sd=1.0, test="t")
    result_z = api.n_mean(mu1=0.0, mu2=0.5, sd=1.0, test="z")
    # t-test fallback includes safety cushion, so should be >= z-test
    assert result_t[0] >= result_z[0]
    assert result_t[1] >= result_z[1]
    # Should be close (within a few observations)
    assert result_t[0] - result_z[0] <= 3
    assert result_t[1] - result_z[1] <= 3

    paired = api.n_paired(delta=0.4, sd_diff=1.2)
    assert isinstance(paired, int)
    assert paired >= 2
