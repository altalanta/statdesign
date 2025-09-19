from statdesign.power import (
    n_one_mean,
    n_one_prop,
    n_two_mean,
    n_two_prop,
    power_one_mean,
    power_one_prop,
    power_two_prop,
)


def test_two_prop_roundtrip():
    n1, n2 = n_two_prop(0.10, 0.14, alpha=0.05, power=0.8, ratio=1.0)
    assert n1 > 0 and n2 > 0
    pow_val = power_two_prop(0.10, 0.14, n1, n2, alpha=0.05)
    assert 0.75 <= pow_val <= 0.9


def test_one_mean_sensitivity():
    n_small = n_one_mean(0.0, 0.2, sd=1.0, alpha=0.05, power=0.8)
    n_large_effect = n_one_mean(0.0, 0.5, sd=1.0, alpha=0.05, power=0.8)
    assert n_large_effect < n_small
    pow_val = power_one_mean(0.0, 0.2, sd=1.0, n=n_small, alpha=0.05)
    assert pow_val >= 0.8


def test_one_prop_samplesize():
    n = n_one_prop(0.55, 0.5, alpha=0.05, power=0.8)
    assert n > 0
    pow_val = power_one_prop(0.55, 0.5, n)
    assert pow_val >= 0.75


def test_two_mean_ratio():
    n1, n2 = n_two_mean(0.0, 0.5, sd1=1.0, sd2=1.5, ratio=2.0)
    assert n1 > 0 and n2 == 2 * n1
