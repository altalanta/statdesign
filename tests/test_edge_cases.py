"""Edge case tests for statdesign functions."""

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from statdesign import alpha_adjust, n_mean, n_two_prop


class TestProportionEdgeCases:
    """Edge case tests for proportion calculations."""

    def test_identical_proportions(self):
        """Test behavior when p1 == p2 (no effect)."""
        with pytest.raises(ValueError, match="effect size"):
            n_two_prop(p1=0.5, p2=0.5, alpha=0.05, power=0.8)

    def test_extreme_proportions(self):
        """Test with very small and large proportions."""
        # Very small proportions
        n1, n2 = n_two_prop(p1=0.01, p2=0.02, alpha=0.05, power=0.8)
        assert n1 > 100  # Should require large samples
        assert n2 > 100

        # Very large proportions
        n1, n2 = n_two_prop(p1=0.98, p2=0.99, alpha=0.05, power=0.8)
        assert n1 > 100  # Should require large samples
        assert n2 > 100

    def test_extreme_power_requirements(self):
        """Test with very high power requirements."""
        n1, n2 = n_two_prop(p1=0.4, p2=0.5, alpha=0.05, power=0.99)
        n1_lower, n2_lower = n_two_prop(p1=0.4, p2=0.5, alpha=0.05, power=0.8)

        # Higher power should require larger samples
        assert n1 > n1_lower
        assert n2 > n2_lower

    def test_small_alpha(self):
        """Test with very small alpha (stricter significance)."""
        n1, n2 = n_two_prop(p1=0.4, p2=0.5, alpha=0.001, power=0.8)
        n1_larger, n2_larger = n_two_prop(p1=0.4, p2=0.5, alpha=0.05, power=0.8)

        # Smaller alpha should require larger samples
        assert n1 > n1_larger
        assert n2 > n2_larger

    @given(
        p1=st.floats(min_value=0.01, max_value=0.99),
        p2=st.floats(min_value=0.01, max_value=0.99),
        alpha=st.floats(min_value=0.001, max_value=0.1),
        power=st.floats(min_value=0.5, max_value=0.99),
        ratio=st.floats(min_value=0.1, max_value=5.0),
    )
    def test_two_prop_properties(self, p1, p2, alpha, power, ratio):
        """Property-based test for two-proportion calculations."""
        assume(abs(p1 - p2) > 0.01)  # Ensure meaningful effect size

        try:
            n1, n2 = n_two_prop(p1=p1, p2=p2, alpha=alpha, power=power, ratio=ratio)

            # Basic sanity checks
            assert n1 >= 1
            assert n2 >= 1
            assert isinstance(n1, int)
            assert isinstance(n2, int)

            # Check allocation ratio is approximately correct
            assert pytest.approx(n2 / n1, rel=0.1) == ratio

        except ValueError:
            # Some combinations may be invalid, that's OK
            pass


class TestMeansEdgeCases:
    """Edge case tests for means calculations."""

    def test_identical_means(self):
        """Test behavior when mu1 == mu2 (no effect)."""
        with pytest.raises(ValueError, match="effect size"):
            n_mean(mu1=0.0, mu2=0.0, sd=1.0, alpha=0.05, power=0.8)

    def test_very_small_effect_size(self):
        """Test with very small effect sizes."""
        n1, n2 = n_mean(mu1=0.0, mu2=0.01, sd=1.0, alpha=0.05, power=0.8, test="z")
        assert n1 > 1000  # Should require very large samples
        assert n2 > 1000

    def test_large_standard_deviation(self):
        """Test with large standard deviation."""
        n1_large_sd, n2_large_sd = n_mean(
            mu1=0.0, mu2=0.5, sd=10.0, alpha=0.05, power=0.8, test="z"
        )
        n1_small_sd, n2_small_sd = n_mean(mu1=0.0, mu2=0.5, sd=1.0, alpha=0.05, power=0.8, test="z")

        # Larger SD should require larger samples
        assert n1_large_sd > n1_small_sd
        assert n2_large_sd > n2_small_sd

    @given(
        mu1=st.floats(min_value=-10.0, max_value=10.0),
        mu2=st.floats(min_value=-10.0, max_value=10.0),
        sd=st.floats(min_value=0.1, max_value=10.0),
        alpha=st.floats(min_value=0.001, max_value=0.1),
        power=st.floats(min_value=0.5, max_value=0.99),
        ratio=st.floats(min_value=0.1, max_value=5.0),
    )
    def test_two_means_properties(self, mu1, mu2, sd, alpha, power, ratio):
        """Property-based test for two-means calculations."""
        assume(abs(mu1 - mu2) / sd > 0.01)  # Ensure meaningful effect size

        try:
            n1, n2 = n_mean(
                mu1=mu1, mu2=mu2, sd=sd, alpha=alpha, power=power, ratio=ratio, test="z"
            )

            # Basic sanity checks
            assert n1 >= 1
            assert n2 >= 1
            assert isinstance(n1, int)
            assert isinstance(n2, int)

            # Check allocation ratio is approximately correct
            assert pytest.approx(n2 / n1, rel=0.1) == ratio

        except ValueError:
            # Some combinations may be invalid, that's OK
            pass


class TestMultiplicityEdgeCases:
    """Edge case tests for multiple testing corrections."""

    def test_single_test(self):
        """Test with m=1 (single test, no correction needed)."""
        result = alpha_adjust(m=1, alpha=0.05, method="bonferroni")
        assert result == 0.05  # Should be unchanged

        result = alpha_adjust(m=1, alpha=0.05, method="bh")
        assert result == 0.05  # Should be unchanged

    def test_large_number_of_tests(self):
        """Test with very large number of tests."""
        result_bonf = alpha_adjust(m=10000, alpha=0.05, method="bonferroni")
        result_bh = alpha_adjust(m=10000, alpha=0.05, method="bh")

        assert result_bonf < result_bh  # BH should be less conservative
        assert result_bonf > 0  # Should still be positive
        assert result_bonf < 0.05  # Should be smaller than original alpha

    @given(
        m=st.integers(min_value=1, max_value=1000), alpha=st.floats(min_value=0.001, max_value=0.1)
    )
    def test_alpha_adjust_properties(self, m, alpha):
        """Property-based test for alpha adjustment."""
        result_bonf = alpha_adjust(m=m, alpha=alpha, method="bonferroni")
        result_bh = alpha_adjust(m=m, alpha=alpha, method="bh")

        # Basic properties
        assert 0 < result_bonf <= alpha
        assert 0 < result_bh <= alpha

        # BH should be less conservative than Bonferroni
        if m > 1:
            assert result_bh >= result_bonf
        else:
            assert result_bh == result_bonf == alpha


class TestInputValidation:
    """Test input validation and error messages."""

    def test_negative_proportions(self):
        """Test that negative proportions raise appropriate errors."""
        with pytest.raises(ValueError, match="between 0 and 1"):
            n_two_prop(p1=-0.1, p2=0.5, alpha=0.05, power=0.8)

    def test_proportions_above_one(self):
        """Test that proportions > 1 raise appropriate errors."""
        with pytest.raises(ValueError, match="between 0 and 1"):
            n_two_prop(p1=0.5, p2=1.1, alpha=0.05, power=0.8)

    def test_negative_power(self):
        """Test that negative power raises appropriate errors."""
        with pytest.raises(ValueError, match="between 0 and 1"):
            n_two_prop(p1=0.4, p2=0.5, alpha=0.05, power=-0.1)

    def test_alpha_above_one(self):
        """Test that alpha > 1 raises appropriate errors."""
        with pytest.raises(ValueError, match="between 0 and 1"):
            n_two_prop(p1=0.4, p2=0.5, alpha=1.1, power=0.8)

    def test_zero_standard_deviation(self):
        """Test that zero SD raises appropriate errors."""
        with pytest.raises(ValueError, match="positive"):
            n_mean(mu1=0.0, mu2=0.5, sd=0.0, alpha=0.05, power=0.8)

    def test_negative_ratio(self):
        """Test that negative allocation ratio raises appropriate errors."""
        with pytest.raises(ValueError, match="positive"):
            n_two_prop(p1=0.4, p2=0.5, alpha=0.05, power=0.8, ratio=-1.0)
