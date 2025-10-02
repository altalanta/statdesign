"""Comprehensive tests for means module to increase coverage."""

import pytest
from statdesign.endpoints.means import n_mean, n_paired, n_one_sample_mean


def test_means_ni_margin_validation():
    """Test NI margin validation for means."""
    with pytest.raises(ValueError, match="ni_margin provided without ni_type"):
        n_mean(mu1=5.0, mu2=5.5, sd=1.0, alpha=0.05, power=0.8, ni_margin=0.1)
    
    with pytest.raises(ValueError, match="ni_type requires ni_margin"):
        n_mean(mu1=5.0, mu2=5.5, sd=1.0, alpha=0.05, power=0.8, ni_type="noninferiority")


def test_means_tail_validation():
    """Test tail validation for means NI/equivalence."""
    with pytest.raises(ValueError, match="equivalence.*two-sided"):
        n_mean(mu1=5.0, mu2=5.1, sd=1.0, alpha=0.05, power=0.8,
               ni_type="equivalence", ni_margin=0.2, tail="greater")
    
    with pytest.raises(ValueError, match="noninferiority.*one-sided"):
        n_mean(mu1=5.0, mu2=5.1, sd=1.0, alpha=0.05, power=0.8,
               ni_type="noninferiority", ni_margin=0.2, tail="two-sided")


def test_means_noninferiority():
    """Test noninferiority calculations for means."""
    # Greater direction
    n1, n2 = n_mean(mu1=5.0, mu2=5.1, sd=1.0, alpha=0.05, power=0.8,
                    ni_type="noninferiority", ni_margin=0.2, tail="greater")
    assert n1 > 0 and n2 > 0
    
    # Less direction
    n1, n2 = n_mean(mu1=5.1, mu2=5.0, sd=1.0, alpha=0.05, power=0.8,
                    ni_type="noninferiority", ni_margin=0.2, tail="less")
    assert n1 > 0 and n2 > 0


def test_means_equivalence():
    """Test equivalence calculations for means."""
    n1, n2 = n_mean(mu1=5.0, mu2=5.05, sd=1.0, alpha=0.05, power=0.8,
                    ni_type="equivalence", ni_margin=0.2, tail="two-sided")
    assert n1 > 0 and n2 > 0


def test_paired_ni_equivalence():
    """Test paired design with NI/equivalence."""
    # Noninferiority
    n = n_paired(delta=0.1, sd_diff=1.0, alpha=0.05, power=0.8,
                ni_type="noninferiority", ni_margin=0.2, tail="greater")
    assert n > 0
    
    # Equivalence
    n = n_paired(delta=0.05, sd_diff=1.0, alpha=0.05, power=0.8,
                ni_type="equivalence", ni_margin=0.2, tail="two-sided")
    assert n > 0


def test_one_sample_mean_ni_equivalence():
    """Test one-sample mean with NI/equivalence."""
    # Noninferiority
    n = n_one_sample_mean(delta=0.1, sd=1.0, alpha=0.05, power=0.8,
                         ni_type="noninferiority", ni_margin=0.2, tail="greater")
    assert n > 0
    
    # Equivalence  
    n = n_one_sample_mean(delta=0.05, sd=1.0, alpha=0.05, power=0.8,
                         ni_type="equivalence", ni_margin=0.2, tail="two-sided")
    assert n > 0


def test_means_different_tails():
    """Test means calculations with different tails."""
    # Greater
    n1, n2 = n_mean(mu1=5.0, mu2=5.5, sd=1.0, alpha=0.05, power=0.8, tail="greater")
    assert n1 > 0 and n2 > 0
    
    # Less  
    n1, n2 = n_mean(mu1=5.5, mu2=5.0, sd=1.0, alpha=0.05, power=0.8, tail="less")
    assert n1 > 0 and n2 > 0


def test_means_unequal_allocation():
    """Test unequal allocation for means."""
    n1, n2 = n_mean(mu1=5.0, mu2=5.5, sd=1.0, alpha=0.05, power=0.8, ratio=3.0)
    assert n2 == 3 * n1


def test_means_small_groups():
    """Test behavior with very small required groups."""
    # Should handle minimum group sizes appropriately
    n1, n2 = n_mean(mu1=5.0, mu2=10.0, sd=1.0, alpha=0.05, power=0.8, test="t")
    assert n1 >= 2 and n2 >= 2  # Minimum for t-test


def test_paired_validation():
    """Test paired design validation."""
    with pytest.raises(ValueError, match="sd_diff must be positive"):
        n_paired(delta=0.5, sd_diff=0.0, alpha=0.05, power=0.8)


def test_one_sample_validation():
    """Test one-sample validation."""
    with pytest.raises(ValueError, match="sd must be positive"):
        n_one_sample_mean(delta=0.5, sd=-1.0, alpha=0.05, power=0.8)
    
    with pytest.raises(ValueError, match="test must be"):
        n_one_sample_mean(delta=0.5, sd=1.0, alpha=0.05, power=0.8, test="invalid")