"""Test exact binomial graceful degradation."""

import warnings
import pytest
from statdesign.endpoints.proportions import n_two_prop, n_one_sample_prop


def test_exact_fallback_large_n():
    """Test exact=True falls back gracefully for large n."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        # Parameters chosen to require large n
        n1, n2 = n_two_prop(p1=0.51, p2=0.49, alpha=0.001, power=0.9, exact=True)
        
        # Should emit warning about fallback
        warning_messages = [str(warning.message) for warning in w]
        assert any("falling back to normal approximation" in msg for msg in warning_messages)
        
        # Should still return reasonable results
        assert n1 > 200
        assert n2 > 200
        assert n1 == n2


def test_exact_fallback_one_sample():
    """Test one-sample exact fallback."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        # Parameters to force large n
        n = n_one_sample_prop(p=0.51, p0=0.49, alpha=0.001, power=0.9, exact=True)
        
        warning_messages = [str(warning.message) for warning in w]
        assert any("falling back to normal approximation" in msg for msg in warning_messages)
        assert n > 200


def test_exact_small_n_no_warning():
    """Test that small n exact calculations don't emit warnings."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        # Parameters that should require small n
        n = n_one_sample_prop(p=0.8, p0=0.5, alpha=0.05, power=0.8, exact=True)
        
        # Should not emit warnings for feasible exact calculations
        warning_messages = [str(warning.message) for warning in w]
        fallback_warnings = [msg for msg in warning_messages if "falling back" in msg]
        assert len(fallback_warnings) == 0
        assert n <= 200