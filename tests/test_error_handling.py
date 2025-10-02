"""Test error handling and edge cases."""

import pytest
from statdesign import n_mean, n_two_prop, n_anova, alpha_adjust


def test_invalid_alpha():
    """Test invalid alpha values."""
    with pytest.raises(ValueError, match="alpha must be in \\(0, 1\\)"):
        n_mean(mu1=5.0, mu2=5.5, sd=1.0, alpha=0.0, power=0.8)
    
    with pytest.raises(ValueError, match="alpha must be in \\(0, 1\\)"):
        n_mean(mu1=5.0, mu2=5.5, sd=1.0, alpha=1.0, power=0.8)


def test_invalid_power():
    """Test invalid power values."""
    with pytest.raises(ValueError, match="power must be in \\(0, 1\\)"):
        n_mean(mu1=5.0, mu2=5.5, sd=1.0, alpha=0.05, power=0.0)
    
    with pytest.raises(ValueError, match="power must be in \\(0, 1\\)"):
        n_mean(mu1=5.0, mu2=5.5, sd=1.0, alpha=0.05, power=1.0)


def test_invalid_sd():
    """Test invalid standard deviation."""
    with pytest.raises(ValueError, match="sd must be positive"):
        n_mean(mu1=5.0, mu2=5.5, sd=0.0, alpha=0.05, power=0.8)
    
    with pytest.raises(ValueError, match="sd must be positive"):
        n_mean(mu1=5.0, mu2=5.5, sd=-1.0, alpha=0.05, power=0.8)


def test_invalid_anova_groups():
    """Test invalid ANOVA group number."""
    with pytest.raises(ValueError, match="k_groups must be at least 2"):
        n_anova(k_groups=1, effect_f=0.25, alpha=0.05, power=0.8)


def test_invalid_anova_effect():
    """Test invalid ANOVA effect size."""
    with pytest.raises(ValueError, match="effect_f must be positive"):
        n_anova(k_groups=3, effect_f=0.0, alpha=0.05, power=0.8)
    
    with pytest.raises(ValueError, match="effect_f must be positive"):
        n_anova(k_groups=3, effect_f=-0.25, alpha=0.05, power=0.8)


def test_invalid_multiplicity_m():
    """Test invalid multiplicity parameter."""
    with pytest.raises(ValueError, match="m must be at least 1"):
        alpha_adjust(m=0, alpha=0.05)


def test_unsupported_tail():
    """Test unsupported tail specification."""
    with pytest.raises(ValueError, match="unsupported tail"):
        n_mean(mu1=5.0, mu2=5.5, sd=1.0, alpha=0.05, power=0.8, tail="invalid")


def test_unsupported_test():
    """Test unsupported test specification."""
    with pytest.raises(ValueError, match="test must be"):
        n_mean(mu1=5.0, mu2=5.5, sd=1.0, alpha=0.05, power=0.8, test="invalid")


def test_proportion_bounds():
    """Test proportion parameter bounds."""
    with pytest.raises(ValueError, match="must be in \\(0, 1\\)"):
        n_two_prop(p1=0.0, p2=0.5, alpha=0.05, power=0.8)
    
    with pytest.raises(ValueError, match="must be in \\(0, 1\\)"):
        n_two_prop(p1=0.5, p2=1.0, alpha=0.05, power=0.8)