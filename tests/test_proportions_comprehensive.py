"""Comprehensive tests for proportions module to increase coverage."""

import pytest
import warnings
from statdesign.endpoints.proportions import (
    n_two_prop, n_one_sample_prop, 
    _validate_probability, _validate_common, _validate_margin
)


def test_ni_margin_validation():
    """Test NI margin validation."""
    with pytest.raises(ValueError, match="ni_margin provided without ni_type"):
        n_two_prop(0.6, 0.8, alpha=0.05, power=0.8, ni_margin=0.1)
    
    with pytest.raises(ValueError, match="ni_type requires ni_margin"):
        n_two_prop(0.6, 0.8, alpha=0.05, power=0.8, ni_type="noninferiority")
    
    with pytest.raises(ValueError, match="ni_margin must be positive"):
        n_two_prop(0.6, 0.8, alpha=0.05, power=0.8, ni_type="noninferiority", ni_margin=0.0)


def test_ni_equivalence_tail_validation():
    """Test NI/equivalence tail validation."""
    with pytest.raises(ValueError, match="equivalence requires.*two-sided"):
        n_two_prop(0.6, 0.8, alpha=0.05, power=0.8, 
                  ni_type="equivalence", ni_margin=0.1, tail="greater")
    
    with pytest.raises(ValueError, match="noninferiority requires.*one-sided"):
        n_two_prop(0.6, 0.8, alpha=0.05, power=0.8,
                  ni_type="noninferiority", ni_margin=0.1, tail="two-sided")


def test_exact_with_ni_not_supported():
    """Test that exact=True with NI/equivalence is not supported."""
    with pytest.raises(NotImplementedError, match="exact=True with NI/equivalence"):
        n_two_prop(0.6, 0.8, alpha=0.05, power=0.8,
                  exact=True, ni_type="noninferiority", ni_margin=0.1, tail="greater")


def test_one_sample_exact():
    """Test one-sample exact calculation."""
    n = n_one_sample_prop(p=0.7, p0=0.5, alpha=0.05, power=0.8, exact=True)
    assert isinstance(n, int)
    assert n > 0


def test_one_sample_ni():
    """Test one-sample noninferiority."""
    # Test greater direction
    n = n_one_sample_prop(p=0.7, p0=0.5, alpha=0.05, power=0.8,
                         ni_type="noninferiority", ni_margin=0.1, tail="greater")
    assert isinstance(n, int)
    assert n > 0
    
    # Test less direction  
    n = n_one_sample_prop(p=0.4, p0=0.5, alpha=0.05, power=0.8,
                         ni_type="noninferiority", ni_margin=0.1, tail="less")
    assert isinstance(n, int)
    assert n > 0


def test_one_sample_equivalence():
    """Test one-sample equivalence."""
    n = n_one_sample_prop(p=0.52, p0=0.5, alpha=0.05, power=0.8,
                         ni_type="equivalence", ni_margin=0.1, tail="two-sided")
    assert isinstance(n, int)
    assert n > 0


def test_exact_vs_normal():
    """Test exact vs normal approximation."""
    # Small effect should give large n, testing both paths
    n_exact = n_one_sample_prop(p=0.52, p0=0.5, alpha=0.05, power=0.8, exact=True)
    n_normal = n_one_sample_prop(p=0.52, p0=0.5, alpha=0.05, power=0.8, exact=False)
    
    # Both should be reasonable
    assert n_exact > 0
    assert n_normal > 0


def test_two_prop_different_tails():
    """Test two-proportion with different tail options."""
    # Less tail (testing p1 < p2)
    n1, n2 = n_two_prop(p1=0.5, p2=0.7, alpha=0.05, power=0.8, tail="less")
    assert n1 > 0 and n2 > 0
    
    # Greater tail (testing p1 > p2)
    n1, n2 = n_two_prop(p1=0.7, p2=0.5, alpha=0.05, power=0.8, tail="greater") 
    assert n1 > 0 and n2 > 0


def test_unequal_allocation():
    """Test unequal allocation in two-proportion test."""
    n1, n2 = n_two_prop(p1=0.6, p2=0.8, alpha=0.05, power=0.8, ratio=2.0)
    assert n2 == 2 * n1


def test_validate_common_function():
    """Test the _validate_common function directly."""
    # Should not raise
    _validate_common(alpha=0.05, power=0.8, tail="two-sided")
    
    # Should raise for unsupported tail
    with pytest.raises(ValueError, match="unsupported tail"):
        _validate_common(alpha=0.05, power=0.8, tail="invalid")


def test_validate_margin_function():
    """Test the _validate_margin function directly."""
    # Should not raise
    _validate_margin(ni_margin=None, ni_type=None)
    _validate_margin(ni_margin=0.1, ni_type="noninferiority")
    
    # Should raise
    with pytest.raises(ValueError):
        _validate_margin(ni_margin=0.1, ni_type=None)


def test_proportion_edge_cases():
    """Test proportion calculations at edge cases."""
    # Very small difference
    n1, n2 = n_two_prop(p1=0.499, p2=0.501, alpha=0.05, power=0.8)
    assert n1 > 1000  # Should require large sample
    
    # Larger difference  
    n1_big, n2_big = n_two_prop(p1=0.3, p2=0.7, alpha=0.05, power=0.8)
    assert n1_big < n1  # Should require smaller sample