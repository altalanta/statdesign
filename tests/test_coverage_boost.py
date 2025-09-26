"""Strategic tests to boost coverage for key modules."""

from __future__ import annotations

import pytest

from statdesign import api
from statdesign.core import ncf, normal, solve
from statdesign.endpoints import anova, means, proportions
from statdesign import multiplicity


class TestAPIEdgeCases:
    """Test edge cases in the main API functions."""

    def test_survival_api_functions(self) -> None:
        """Test survival-related API functions."""
        # Test events_to_n_exponential
        result = api.events_to_n_exponential(
            events_required=50.0,
            accrual_years=2.0,
            followup_years=1.0,
            base_hazard_ctrl=0.1,
            hr=0.7,
        )
        assert len(result) == 3
        assert all(isinstance(x, int) for x in result)

        # Test power_logrank_from_n
        power = api.power_logrank_from_n(
            hr=0.8,
            n_exp=100,
            n_ctrl=100,
            accrual_years=2.0,
            followup_years=1.0,
            base_hazard_ctrl=0.1,
        )
        assert 0 < power < 1

        # Test required_events_logrank
        events = api.required_events_logrank(hr=0.7, alpha=0.05, power=0.8)
        assert events > 0

        # Test required_events_cox
        events_cox = api.required_events_cox(log_hr=-0.3, var_x=0.25)
        assert events_cox > 0


class TestNormalModule:
    """Test normal distribution utilities."""

    def test_normal_ppf_edge_cases(self) -> None:
        """Test normal percent point function edge cases."""
        # Test values close to 0 and 1
        result_low = normal.ppf(0.001)
        assert result_low < -3

        result_high = normal.ppf(0.999)
        assert result_high > 3

        # Test middle values
        result_mid = normal.ppf(0.5)
        assert abs(result_mid) < 0.01

    def test_normal_cdf_edge_cases(self) -> None:
        """Test normal cumulative distribution function."""
        # Test extreme values
        result_low = normal.cdf(-5)
        assert result_low < 0.001

        result_high = normal.cdf(5)
        assert result_high > 0.999

        # Test around zero
        result_zero = normal.cdf(0)
        assert abs(result_zero - 0.5) < 0.01


class TestNCFModule:
    """Test noncentral distribution utilities."""

    def test_power_normal_edge_cases(self) -> None:
        """Test normal power calculations."""
        # Test different tails
        power_two = ncf.power_normal(2.0, 0.05, "two-sided")
        power_greater = ncf.power_normal(2.0, 0.05, "greater")
        power_less = ncf.power_normal(-2.0, 0.05, "less")

        assert 0 < power_two < 1
        assert 0 < power_greater < 1
        assert 0 < power_less < 1

    def test_chi2_ppf_fallback(self) -> None:
        """Test chi-square percent point function fallback."""
        # Test the normal approximation for chi-square
        result = ncf._chi2_ppf(0.95, 10)
        assert result > 0

        # Test edge case
        with pytest.raises(ValueError):
            ncf._chi2_ppf(0.95, 0)


class TestSolveModule:
    """Test solver utilities."""

    def test_solve_monotone_int_edge_cases(self) -> None:
        """Test integer solver edge cases."""
        # Simple increasing function
        def simple_func(n: int) -> float:
            return n / 100.0

        result = solve.solve_monotone_int(simple_func, 0.5, lower=1)
        assert result >= 50

        # Test with function that starts high
        def high_func(n: int) -> float:
            return 0.9 if n >= 2 else 0.1

        result_high = solve.solve_monotone_int(high_func, 0.8, lower=1)
        assert result_high == 2

    def test_solve_validation(self) -> None:
        """Test solver input validation."""
        def dummy_func(n: int) -> float:
            return 0.5

        # Test invalid targets
        with pytest.raises(ValueError):
            solve.solve_monotone_int(dummy_func, 0.0)

        with pytest.raises(ValueError):
            solve.solve_monotone_int(dummy_func, 1.0)

        # Test invalid lower bound
        with pytest.raises(ValueError):
            solve.solve_monotone_int(dummy_func, 0.5, lower=0)


class TestMultiplicityModule:
    """Test multiple testing adjustments."""

    def test_alpha_adjust_edge_cases(self) -> None:
        """Test alpha adjustment edge cases."""
        # Test with m=1 (no adjustment needed)
        result = multiplicity.alpha_adjust(m=1, alpha=0.05)
        assert result == 0.05

        # Test BH method
        result_bh = multiplicity.alpha_adjust(m=10, alpha=0.05, method="bh")
        assert 0 < result_bh <= 0.05

    def test_bh_thresholds_edge_cases(self) -> None:
        """Test Benjamini-Hochberg thresholds."""
        # Test with small m
        thresholds = multiplicity.bh_thresholds(m=2, alpha=0.10)
        assert len(thresholds) == 2
        assert thresholds[0] < thresholds[1]

        # Test with larger m
        thresholds_large = multiplicity.bh_thresholds(m=20, alpha=0.05)
        assert len(thresholds_large) == 20
        assert thresholds_large[0] < thresholds_large[-1]


class TestMeansEdgeCases:
    """Test means module edge cases."""

    def test_means_validation_errors(self) -> None:
        """Test input validation in means module."""
        # Test invalid alpha
        with pytest.raises(ValueError):
            means.n_mean(mu1=0, mu2=1, sd=1, alpha=0)

        with pytest.raises(ValueError):
            means.n_mean(mu1=0, mu2=1, sd=1, alpha=1)

        # Test invalid power
        with pytest.raises(ValueError):
            means.n_mean(mu1=0, mu2=1, sd=1, power=0)

        with pytest.raises(ValueError):
            means.n_mean(mu1=0, mu2=1, sd=1, power=1)

        # Test invalid sd
        with pytest.raises(ValueError):
            means.n_mean(mu1=0, mu2=1, sd=0)

        # Test invalid test type
        with pytest.raises(ValueError):
            means.n_mean(mu1=0, mu2=1, sd=1, test="invalid")

    def test_means_ni_validation(self) -> None:
        """Test non-inferiority validation."""
        # Test equivalence with wrong tail
        with pytest.raises(ValueError):
            means.n_mean(mu1=0, mu2=1, sd=1, ni_type="equivalence", tail="greater")

        # Test non-inferiority with wrong tail
        with pytest.raises(ValueError):
            means.n_mean(mu1=0, mu2=1, sd=1, ni_type="noninferiority", tail="two-sided")

        # Test margin without type
        with pytest.raises(ValueError):
            means.n_mean(mu1=0, mu2=1, sd=1, ni_margin=0.5)

        # Test type without margin
        with pytest.raises(ValueError):
            means.n_mean(mu1=0, mu2=1, sd=1, ni_type="noninferiority")


class TestProportionsEdgeCases:
    """Test proportions module edge cases."""

    def test_proportions_validation_errors(self) -> None:
        """Test input validation in proportions module."""
        # Test invalid proportions
        with pytest.raises(ValueError):
            proportions.n_two_prop(p1=-0.1, p2=0.5)

        with pytest.raises(ValueError):
            proportions.n_two_prop(p1=1.1, p2=0.5)

        # Test invalid alpha
        with pytest.raises(ValueError):
            proportions.n_two_prop(p1=0.6, p2=0.5, alpha=0)

        # Test invalid power
        with pytest.raises(ValueError):
            proportions.n_two_prop(p1=0.6, p2=0.5, power=1)

        # Test invalid ratio
        with pytest.raises(ValueError):
            proportions.n_two_prop(p1=0.6, p2=0.5, ratio=0)

    def test_proportions_ni_validation(self) -> None:
        """Test non-inferiority validation in proportions."""
        # Test margin without type
        with pytest.raises(ValueError):
            proportions.n_two_prop(p1=0.6, p2=0.5, ni_margin=0.1)

        # Test type without margin
        with pytest.raises(ValueError):
            proportions.n_two_prop(p1=0.6, p2=0.5, ni_type="noninferiority")


class TestANOVAEdgeCases:
    """Test ANOVA module edge cases."""

    def test_anova_validation_errors(self) -> None:
        """Test input validation in ANOVA module."""
        # Test invalid k_groups
        with pytest.raises(ValueError):
            anova.n_anova(k_groups=1, effect_f=0.25)

        # Test invalid effect_f
        with pytest.raises(ValueError):
            anova.n_anova(k_groups=3, effect_f=0)

        # Test invalid alpha
        with pytest.raises(ValueError):
            anova.n_anova(k_groups=3, effect_f=0.25, alpha=0)

        # Test invalid power
        with pytest.raises(ValueError):
            anova.n_anova(k_groups=3, effect_f=0.25, power=1)

    def test_anova_allocation_validation(self) -> None:
        """Test allocation validation in ANOVA."""
        # Test wrong length allocation
        with pytest.raises(ValueError):
            anova.n_anova(k_groups=3, effect_f=0.25, allocation=[1, 2])  # should be 3 weights

        # Test negative weights
        with pytest.raises(ValueError):
            anova.n_anova(k_groups=3, effect_f=0.25, allocation=[1, -1, 2])

        # Test zero weights
        with pytest.raises(ValueError):
            anova.n_anova(k_groups=3, effect_f=0.25, allocation=[1, 0, 2])