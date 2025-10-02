"""Test API functions to increase coverage."""

import pytest
from statdesign import (
    n_mean, n_paired, n_one_sample_mean, 
    n_two_prop, n_one_sample_prop,
    n_anova, alpha_adjust, bh_thresholds
)


def test_n_mean_basic():
    """Test basic two-sample mean calculation."""
    n1, n2 = n_mean(mu1=5.0, mu2=5.5, sd=1.0, alpha=0.05, power=0.8)
    assert isinstance(n1, int)
    assert isinstance(n2, int)
    assert n1 > 0
    assert n2 > 0


def test_n_paired_basic():
    """Test paired sample calculation."""
    n = n_paired(delta=0.5, sd_diff=1.0, alpha=0.05, power=0.8)
    assert isinstance(n, int)
    assert n > 0


def test_n_one_sample_mean_basic():
    """Test one-sample mean calculation."""
    n = n_one_sample_mean(delta=0.5, sd=1.0, alpha=0.05, power=0.8)
    assert isinstance(n, int)
    assert n > 0


def test_n_anova_basic():
    """Test ANOVA sample size calculation."""
    n = n_anova(k_groups=3, effect_f=0.25, alpha=0.05, power=0.8)
    assert isinstance(n, int)
    assert n > 0


def test_alpha_adjust_bonferroni():
    """Test Bonferroni correction."""
    adjusted = alpha_adjust(m=5, alpha=0.05, method="bonferroni")
    assert adjusted == 0.01
    
    
def test_alpha_adjust_bh():
    """Test Benjamini-Hochberg correction."""
    adjusted = alpha_adjust(m=5, alpha=0.05, method="bh")
    assert adjusted == 0.01


def test_bh_thresholds():
    """Test BH threshold calculation."""
    thresholds = bh_thresholds(m=3, alpha=0.05)
    expected = [0.05 * 1 / 3, 0.05 * 2 / 3, 0.05 * 3 / 3]
    assert len(thresholds) == 3
    for i, (actual, exp) in enumerate(zip(thresholds, expected)):
        assert abs(actual - exp) < 1e-10


def test_n_one_sample_prop_basic():
    """Test one-sample proportion calculation."""
    n = n_one_sample_prop(p=0.6, p0=0.5, alpha=0.05, power=0.8)
    assert isinstance(n, int)
    assert n > 0


def test_ratio_allocation():
    """Test unequal allocation."""
    n1, n2 = n_mean(mu1=5.0, mu2=5.5, sd=1.0, alpha=0.05, power=0.8, ratio=2.0)
    assert n2 == 2 * n1  # 2:1 allocation


def test_z_vs_t_test():
    """Test z vs t test options."""
    n1_t, n2_t = n_mean(mu1=5.0, mu2=5.5, sd=1.0, alpha=0.05, power=0.8, test="t")
    n1_z, n2_z = n_mean(mu1=5.0, mu2=5.5, sd=1.0, alpha=0.05, power=0.8, test="z")
    # t-test should require slightly more samples
    assert n1_t >= n1_z
    assert n2_t >= n2_z