"""Tests for design effects module."""

from __future__ import annotations

import math

import pytest

from statdesign.endpoints import design_effects


class TestDesignEffectClusterEqual:
    """Tests for design_effect_cluster_equal function."""

    def test_basic_calculation(self) -> None:
        """Test basic design effect calculation with equal cluster sizes."""
        # Basic formula: 1 + (m - 1) * icc
        result = design_effects.design_effect_cluster_equal(m=10.0, icc=0.05)
        expected = 1.0 + (10.0 - 1.0) * 0.05  # 1 + 9 * 0.05 = 1.45
        assert result == expected

    def test_no_clustering_effect(self) -> None:
        """Test when ICC is 0 (no clustering)."""
        result = design_effects.design_effect_cluster_equal(m=5.0, icc=0.0)
        assert result == 1.0

    def test_single_member_cluster(self) -> None:
        """Test with cluster size of 1."""
        result = design_effects.design_effect_cluster_equal(m=1.0, icc=0.3)
        assert result == 1.0  # 1 + (1-1) * 0.3 = 1

    def test_high_icc(self) -> None:
        """Test with high ICC near 1."""
        result = design_effects.design_effect_cluster_equal(m=5.0, icc=0.99)
        expected = 1.0 + (5.0 - 1.0) * 0.99  # 1 + 4 * 0.99 = 4.96
        assert result == expected

    def test_fractional_cluster_size(self) -> None:
        """Test with fractional cluster sizes."""
        result = design_effects.design_effect_cluster_equal(m=2.5, icc=0.2)
        expected = 1.0 + (2.5 - 1.0) * 0.2  # 1 + 1.5 * 0.2 = 1.3
        assert result == expected

    def test_invalid_m_zero(self) -> None:
        """Test validation: m must be positive."""
        with pytest.raises(ValueError, match="m must be positive"):
            design_effects.design_effect_cluster_equal(m=0.0, icc=0.1)

    def test_invalid_m_negative(self) -> None:
        """Test validation: m cannot be negative."""
        with pytest.raises(ValueError, match="m must be positive"):
            design_effects.design_effect_cluster_equal(m=-1.0, icc=0.1)

    def test_invalid_icc_negative(self) -> None:
        """Test validation: ICC cannot be negative."""
        with pytest.raises(ValueError, match="icc must be in \\[0, 1\\)"):
            design_effects.design_effect_cluster_equal(m=5.0, icc=-0.1)

    def test_invalid_icc_one_or_greater(self) -> None:
        """Test validation: ICC must be less than 1."""
        with pytest.raises(ValueError, match="icc must be in \\[0, 1\\)"):
            design_effects.design_effect_cluster_equal(m=5.0, icc=1.0)

        with pytest.raises(ValueError, match="icc must be in \\[0, 1\\)"):
            design_effects.design_effect_cluster_equal(m=5.0, icc=1.1)


class TestDesignEffectClusterUnequal:
    """Tests for design_effect_cluster_unequal function."""

    def test_basic_calculation(self) -> None:
        """Test basic design effect calculation with unequal cluster sizes."""
        # Formula: 1 + icc * (mbar - 1 + cv^2)
        result = design_effects.design_effect_cluster_unequal(mbar=10.0, icc=0.05, cv=0.3)
        expected = 1.0 + 0.05 * (10.0 - 1.0 + 0.3**2)  # 1 + 0.05 * (9 + 0.09) = 1 + 0.05 * 9.09
        assert result == expected

    def test_no_clustering_effect(self) -> None:
        """Test when ICC is 0."""
        result = design_effects.design_effect_cluster_unequal(mbar=5.0, icc=0.0, cv=0.5)
        assert result == 1.0

    def test_no_variability(self) -> None:
        """Test when CV is 0 (equal sizes) - should match equal cluster formula."""
        mbar = 8.0
        icc = 0.1
        result_unequal = design_effects.design_effect_cluster_unequal(mbar=mbar, icc=icc, cv=0.0)
        result_equal = design_effects.design_effect_cluster_equal(m=mbar, icc=icc)
        assert result_unequal == result_equal

    def test_high_variability(self) -> None:
        """Test with high coefficient of variation."""
        result = design_effects.design_effect_cluster_unequal(mbar=5.0, icc=0.2, cv=2.0)
        expected = 1.0 + 0.2 * (5.0 - 1.0 + 2.0**2)  # 1 + 0.2 * (4 + 4) = 1 + 0.2 * 8 = 2.6
        assert result == expected

    def test_invalid_mbar_zero(self) -> None:
        """Test validation: mbar must be positive."""
        with pytest.raises(ValueError, match="mbar must be positive"):
            design_effects.design_effect_cluster_unequal(mbar=0.0, icc=0.1, cv=0.3)

    def test_invalid_mbar_negative(self) -> None:
        """Test validation: mbar cannot be negative."""
        with pytest.raises(ValueError, match="mbar must be positive"):
            design_effects.design_effect_cluster_unequal(mbar=-1.0, icc=0.1, cv=0.3)

    def test_invalid_icc_negative(self) -> None:
        """Test validation: ICC cannot be negative."""
        with pytest.raises(ValueError, match="icc must be in \\[0, 1\\)"):
            design_effects.design_effect_cluster_unequal(mbar=5.0, icc=-0.1, cv=0.3)

    def test_invalid_icc_one_or_greater(self) -> None:
        """Test validation: ICC must be less than 1."""
        with pytest.raises(ValueError, match="icc must be in \\[0, 1\\)"):
            design_effects.design_effect_cluster_unequal(mbar=5.0, icc=1.0, cv=0.3)

    def test_invalid_cv_negative(self) -> None:
        """Test validation: CV cannot be negative."""
        with pytest.raises(ValueError, match="cv must be non-negative"):
            design_effects.design_effect_cluster_unequal(mbar=5.0, icc=0.1, cv=-0.1)


class TestDesignEffectRepeatedCS:
    """Tests for design_effect_repeated_cs function."""

    def test_basic_calculation(self) -> None:
        """Test basic design effect calculation for repeated measures."""
        # Formula: 1 + (k - 1) * icc
        result = design_effects.design_effect_repeated_cs(k=4, icc=0.3)
        expected = 1.0 + (4 - 1) * 0.3  # 1 + 3 * 0.3 = 1.9
        assert result == expected

    def test_single_observation(self) -> None:
        """Test with k=1 (single observation)."""
        result = design_effects.design_effect_repeated_cs(k=1, icc=0.5)
        assert result == 1.0

    def test_no_correlation(self) -> None:
        """Test when ICC is 0 (no correlation)."""
        result = design_effects.design_effect_repeated_cs(k=5, icc=0.0)
        assert result == 1.0

    def test_high_correlation(self) -> None:
        """Test with high ICC near 1."""
        result = design_effects.design_effect_repeated_cs(k=3, icc=0.95)
        expected = 1.0 + (3 - 1) * 0.95  # 1 + 2 * 0.95 = 2.9
        assert result == expected

    def test_many_observations(self) -> None:
        """Test with many repeated observations."""
        result = design_effects.design_effect_repeated_cs(k=20, icc=0.1)
        expected = 1.0 + (20 - 1) * 0.1  # 1 + 19 * 0.1 = 2.9
        assert result == expected

    def test_invalid_k_zero(self) -> None:
        """Test validation: k must be at least 1."""
        with pytest.raises(ValueError, match="k must be at least 1"):
            design_effects.design_effect_repeated_cs(k=0, icc=0.1)

    def test_invalid_k_negative(self) -> None:
        """Test validation: k cannot be negative."""
        with pytest.raises(ValueError, match="k must be at least 1"):
            design_effects.design_effect_repeated_cs(k=-1, icc=0.1)

    def test_invalid_icc_negative(self) -> None:
        """Test validation: ICC cannot be negative."""
        with pytest.raises(ValueError, match="icc must be in \\[0, 1\\)"):
            design_effects.design_effect_repeated_cs(k=3, icc=-0.1)

    def test_invalid_icc_one_or_greater(self) -> None:
        """Test validation: ICC must be less than 1."""
        with pytest.raises(ValueError, match="icc must be in \\[0, 1\\)"):
            design_effects.design_effect_repeated_cs(k=3, icc=1.0)


class TestInflateNByDE:
    """Tests for inflate_n_by_de function."""

    def test_basic_inflation(self) -> None:
        """Test basic sample size inflation."""
        result = design_effects.inflate_n_by_de(n_individuals=100, de=1.5)
        expected = math.ceil(100 * 1.5)  # ceil(150) = 150
        assert result == expected

    def test_no_inflation(self) -> None:
        """Test when design effect is 1 (no inflation)."""
        result = design_effects.inflate_n_by_de(n_individuals=50, de=1.0)
        assert result == 50

    def test_fractional_inflation(self) -> None:
        """Test inflation that requires ceiling."""
        result = design_effects.inflate_n_by_de(n_individuals=10, de=1.25)
        expected = math.ceil(10 * 1.25)  # ceil(12.5) = 13
        assert result == expected

    def test_small_inflation(self) -> None:
        """Test small design effect."""
        result = design_effects.inflate_n_by_de(n_individuals=100, de=1.01)
        expected = math.ceil(100 * 1.01)  # ceil(101) = 101
        assert result == expected

    def test_large_inflation(self) -> None:
        """Test large design effect."""
        result = design_effects.inflate_n_by_de(n_individuals=20, de=5.0)
        expected = math.ceil(20 * 5.0)  # ceil(100) = 100
        assert result == expected

    def test_zero_individuals(self) -> None:
        """Test with zero individuals."""
        result = design_effects.inflate_n_by_de(n_individuals=0, de=2.0)
        assert result == 0

    def test_exact_multiplication(self) -> None:
        """Test when multiplication gives exact integer."""
        result = design_effects.inflate_n_by_de(n_individuals=25, de=2.0)
        expected = math.ceil(25 * 2.0)  # ceil(50.0) = 50
        assert result == expected

    def test_invalid_n_negative(self) -> None:
        """Test validation: n_individuals cannot be negative."""
        with pytest.raises(ValueError, match="n_individuals must be non-negative"):
            design_effects.inflate_n_by_de(n_individuals=-1, de=1.5)

    def test_invalid_de_zero(self) -> None:
        """Test validation: design effect must be positive."""
        with pytest.raises(ValueError, match="de must be positive"):
            design_effects.inflate_n_by_de(n_individuals=10, de=0.0)

    def test_invalid_de_negative(self) -> None:
        """Test validation: design effect cannot be negative."""
        with pytest.raises(ValueError, match="de must be positive"):
            design_effects.inflate_n_by_de(n_individuals=10, de=-1.0)


class TestIntegration:
    """Integration tests combining multiple design effect functions."""

    def test_cluster_workflow(self) -> None:
        """Test typical workflow for cluster randomized trial design."""
        # Calculate individual-level sample size (would normally come from power calculation)
        n_individual = 200
        
        # Calculate design effect for equal clusters
        m = 15  # cluster size
        icc = 0.05
        de = design_effects.design_effect_cluster_equal(m=m, icc=icc)
        
        # Inflate sample size
        n_total = design_effects.inflate_n_by_de(n_individual, de)
        
        # Verify calculation
        expected_de = 1.0 + (15 - 1) * 0.05  # 1.7
        expected_n = math.ceil(200 * expected_de)  # ceil(340) = 340
        
        assert de == expected_de
        assert n_total == expected_n

    def test_unequal_cluster_workflow(self) -> None:
        """Test workflow for unequal cluster sizes."""
        n_individual = 150
        mbar = 12.0
        icc = 0.08
        cv = 0.4
        
        de = design_effects.design_effect_cluster_unequal(mbar=mbar, icc=icc, cv=cv)
        n_total = design_effects.inflate_n_by_de(n_individual, de)
        
        # Verify the unequal clusters give larger DE than equal clusters
        de_equal = design_effects.design_effect_cluster_equal(m=mbar, icc=icc)
        assert de > de_equal
        
        # Should be positive inflation
        assert n_total > n_individual

    def test_repeated_measures_workflow(self) -> None:
        """Test workflow for repeated measures design."""
        n_individual = 80
        k = 6  # number of repeated measures
        icc = 0.4
        
        de = design_effects.design_effect_repeated_cs(k=k, icc=icc)
        n_total = design_effects.inflate_n_by_de(n_individual, de)
        
        # With high ICC and many measurements, should have substantial inflation
        assert de > 2.0  # Should be > 1 + (6-1)*0.4 = 3.0
        assert n_total > 2 * n_individual