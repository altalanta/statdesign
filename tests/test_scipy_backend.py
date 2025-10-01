"""Tests for optional SciPy backend functionality."""

import os
from unittest.mock import patch

import pytest

from statdesign._scipy_backend import enable_scipy, has_scipy, require_scipy


class TestSciPyBackend:
    """Test SciPy backend import and error handling."""

    def test_has_scipy_with_env_var(self):
        """Test SciPy detection with environment variable."""
        with patch.dict(os.environ, {"STATDESIGN_AUTO_SCIPY": "1"}):
            # Reset import state
            import statdesign._scipy_backend

            statdesign._scipy_backend._IMPORT_ATTEMPTED = False
            statdesign._scipy_backend._SCIPY_STATS = None
            statdesign._scipy_backend._SCIPY_ERROR = None

            try:
                result = has_scipy()
                # Should be True if scipy is installed, False otherwise
                assert isinstance(result, bool)
            except ImportError:
                # If scipy is not installed, that's fine for testing
                pass

    def test_has_scipy_disabled(self):
        """Test SciPy is disabled when explicitly disabled."""
        with patch.dict(os.environ, {"STATDESIGN_DISABLE_SCIPY": "1"}):
            # Reset import state
            import statdesign._scipy_backend

            statdesign._scipy_backend._IMPORT_ATTEMPTED = False
            statdesign._scipy_backend._SCIPY_STATS = None
            statdesign._scipy_backend._SCIPY_ERROR = None

            assert not has_scipy()

    def test_require_scipy_with_missing_scipy(self):
        """Test require_scipy raises helpful error when SciPy is missing."""
        with patch.dict(os.environ, {}, clear=True):
            # Reset import state to simulate no scipy
            import statdesign._scipy_backend

            statdesign._scipy_backend._IMPORT_ATTEMPTED = False
            statdesign._scipy_backend._SCIPY_STATS = None
            statdesign._scipy_backend._SCIPY_ERROR = None

            with pytest.raises(RuntimeError) as exc_info:
                require_scipy("Test feature")

            error_msg = str(exc_info.value)
            assert "Test feature requires SciPy" in error_msg
            assert "pip install 'statdesign[scipy]'" in error_msg
            assert "STATDESIGN_AUTO_SCIPY=1" in error_msg

    def test_enable_scipy_explicit(self):
        """Test explicit SciPy enabling."""
        # This will either succeed or fail depending on environment
        result = enable_scipy()
        assert isinstance(result, bool)

    @pytest.mark.skipif(not has_scipy(), reason="SciPy not available")
    def test_require_scipy_with_available_scipy(self):
        """Test require_scipy returns scipy.stats when available."""
        with patch.dict(os.environ, {"STATDESIGN_AUTO_SCIPY": "1"}):
            # Enable scipy explicitly
            enable_scipy()

            stats = require_scipy("Test feature")
            assert hasattr(stats, "norm")  # Check it's scipy.stats
            assert hasattr(stats, "t")
            assert hasattr(stats, "f")

    def test_multiple_calls_cached(self):
        """Test that multiple calls to has_scipy are cached."""
        with patch.dict(os.environ, {}, clear=True):
            # Reset state
            import statdesign._scipy_backend

            statdesign._scipy_backend._IMPORT_ATTEMPTED = False
            statdesign._scipy_backend._SCIPY_STATS = None
            statdesign._scipy_backend._SCIPY_ERROR = None

            # First call
            result1 = has_scipy()

            # Second call should return same result without re-importing
            result2 = has_scipy()

            assert result1 == result2


@pytest.mark.skipif(has_scipy(), reason="SciPy is available")
class TestWithoutSciPy:
    """Tests for behavior when SciPy is not available."""

    def test_fallback_behavior(self):
        """Test that functions fall back gracefully without SciPy."""
        from statdesign.core.ncf import power_noncentral_t, power_normal

        # These should work without SciPy
        power1 = power_normal(0.5, 0.05, "two-sided")
        power2 = power_noncentral_t(0.5, 30, 0.05, "two-sided")

        assert 0 <= power1 <= 1
        assert 0 <= power2 <= 1
        # With large df, noncentral t should approximate normal
        assert abs(power1 - power2) < 0.01


@pytest.mark.skipif(not has_scipy(), reason="SciPy not available")
class TestWithSciPy:
    """Tests for behavior when SciPy is available."""

    def test_enhanced_behavior(self):
        """Test that functions use SciPy when available."""
        from statdesign.core.ncf import power_noncentral_f, power_noncentral_t

        # These should use SciPy for more accurate results
        power_t = power_noncentral_t(0.5, 10, 0.05, "two-sided")
        power_f = power_noncentral_f(5.0, 2, 20, 0.05)

        assert 0 <= power_t <= 1
        assert 0 <= power_f <= 1

        # Should be different from normal approximation for small df
        from statdesign.core.ncf import power_normal

        power_norm = power_normal(0.5, 0.05, "two-sided")
        assert abs(power_t - power_norm) > 0.001  # Should differ for small df
