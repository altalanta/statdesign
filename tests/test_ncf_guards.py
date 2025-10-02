"""Test noncentral F stability guards."""

import pytest
from statdesign.core.ncf import power_noncentral_f


def test_ncf_invalid_degrees_freedom():
    """Test ncf rejects invalid degrees of freedom."""
    with pytest.raises(ValueError, match="invalid degrees of freedom"):
        power_noncentral_f(lambda_=1.0, df_num=-1, df_den=10, alpha=0.05)
    
    with pytest.raises(ValueError, match="invalid degrees of freedom"):
        power_noncentral_f(lambda_=1.0, df_num=10, df_den=0, alpha=0.05)


def test_ncf_invalid_noncentrality():
    """Test ncf rejects negative noncentrality parameter."""
    with pytest.raises(ValueError, match="noncentrality"):
        power_noncentral_f(lambda_=-1.0, df_num=3, df_den=10, alpha=0.05)


def test_ncf_zero_noncentrality():
    """Test ncf handles zero noncentrality correctly."""
    power = power_noncentral_f(lambda_=0.0, df_num=3, df_den=10, alpha=0.05)
    assert power == 0.0


def test_ncf_valid_parameters():
    """Test ncf works with valid parameters."""
    power = power_noncentral_f(lambda_=2.0, df_num=3, df_den=10, alpha=0.05)
    assert 0.0 < power < 1.0


def test_ncf_extreme_noncentrality():
    """Test ncf handles extreme noncentrality parameters."""
    # Very large lambda should give power close to 1
    power = power_noncentral_f(lambda_=100.0, df_num=3, df_den=10, alpha=0.05)
    assert 0.9 < power <= 1.0
    
    # Small but positive lambda
    power = power_noncentral_f(lambda_=0.01, df_num=3, df_den=10, alpha=0.05)
    assert 0.0 <= power < 0.2