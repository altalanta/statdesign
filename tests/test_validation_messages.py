"""Test validation error message consistency."""

import pytest
from statdesign.endpoints.proportions import _validate_probability


def test_probability_validation_message():
    """Test that probability validation uses canonical phrasing."""
    with pytest.raises(ValueError) as exc_info:
        _validate_probability(1.2, "alpha")
    assert "must be in (0, 1)" in str(exc_info.value)
    assert "alpha" in str(exc_info.value)


def test_probability_validation_message_zero():
    """Test validation at boundary values."""
    with pytest.raises(ValueError) as exc_info:
        _validate_probability(0.0, "p")
    assert "must be in (0, 1)" in str(exc_info.value)


def test_probability_validation_message_one():
    """Test validation at upper boundary."""
    with pytest.raises(ValueError) as exc_info:
        _validate_probability(1.0, "p")
    assert "must be in (0, 1)" in str(exc_info.value)


def test_probability_validation_passes():
    """Test that valid probabilities pass validation."""
    # Should not raise
    _validate_probability(0.5, "p")
    _validate_probability(0.001, "p")
    _validate_probability(0.999, "p")