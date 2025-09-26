"""Tests for allocation module."""

from __future__ import annotations

import math

import pytest

from statdesign.core import alloc


class TestValidateRatio:
    """Tests for validate_ratio function."""

    def test_valid_ratios(self) -> None:
        """Test validation passes for valid ratios."""
        # Should not raise exceptions
        alloc.validate_ratio(1.0)
        alloc.validate_ratio(0.5)
        alloc.validate_ratio(2.0)
        alloc.validate_ratio(0.1)
        alloc.validate_ratio(10.0)

    def test_invalid_ratio_zero(self) -> None:
        """Test validation fails for zero ratio."""
        with pytest.raises(ValueError, match="ratio must be positive"):
            alloc.validate_ratio(0.0)

    def test_invalid_ratio_negative(self) -> None:
        """Test validation fails for negative ratio."""
        with pytest.raises(ValueError, match="ratio must be positive"):
            alloc.validate_ratio(-1.0)


class TestGroupsFromN1:
    """Tests for groups_from_n1 function."""

    def test_equal_allocation(self) -> None:
        """Test equal allocation (ratio = 1.0)."""
        n1, n2 = alloc.groups_from_n1(n1=10, ratio=1.0)
        assert n1 == 10
        assert n2 == 10

    def test_unequal_allocation_larger_n2(self) -> None:
        """Test allocation with larger n2 (ratio > 1)."""
        n1, n2 = alloc.groups_from_n1(n1=10, ratio=2.0)
        assert n1 == 10
        assert n2 == 20

    def test_unequal_allocation_smaller_n2(self) -> None:
        """Test allocation with smaller n2 (ratio < 1)."""
        n1, n2 = alloc.groups_from_n1(n1=10, ratio=0.5)
        assert n1 == 10
        assert n2 == 5

    def test_fractional_ratio_ceiling(self) -> None:
        """Test fractional ratio uses ceiling for n2."""
        n1, n2 = alloc.groups_from_n1(n1=5, ratio=1.3)
        # n2 = ceil(5 * 1.3) = ceil(6.5) = 7
        assert n1 == 5
        assert n2 == 7

    def test_minimum_n2_enforced(self) -> None:
        """Test n2 is at least 1 even with small ratios."""
        n1, n2 = alloc.groups_from_n1(n1=1, ratio=0.1)
        assert n1 == 1
        assert n2 == 1  # max(1, ceil(1 * 0.1)) = max(1, 1) = 1

    def test_small_n1_small_ratio(self) -> None:
        """Test very small n1 with very small ratio."""
        n1, n2 = alloc.groups_from_n1(n1=2, ratio=0.3)
        # n2 = max(1, ceil(2 * 0.3)) = max(1, ceil(0.6)) = max(1, 1) = 1
        assert n1 == 2
        assert n2 == 1

    def test_large_ratio(self) -> None:
        """Test large allocation ratio."""
        n1, n2 = alloc.groups_from_n1(n1=3, ratio=10.0)
        assert n1 == 3
        assert n2 == 30

    def test_invalid_n1_zero(self) -> None:
        """Test validation fails for n1 = 0."""
        with pytest.raises(ValueError, match="n1 must be at least 1"):
            alloc.groups_from_n1(n1=0, ratio=1.0)

    def test_invalid_n1_negative(self) -> None:
        """Test validation fails for negative n1."""
        with pytest.raises(ValueError, match="n1 must be at least 1"):
            alloc.groups_from_n1(n1=-1, ratio=1.0)

    def test_invalid_ratio_zero(self) -> None:
        """Test validation fails for zero ratio."""
        with pytest.raises(ValueError, match="ratio must be positive"):
            alloc.groups_from_n1(n1=10, ratio=0.0)

    def test_invalid_ratio_negative(self) -> None:
        """Test validation fails for negative ratio."""
        with pytest.raises(ValueError, match="ratio must be positive"):
            alloc.groups_from_n1(n1=10, ratio=-1.0)


class TestGroupsFromTotal:
    """Tests for groups_from_total function."""

    def test_equal_allocation(self) -> None:
        """Test equal allocation with even total."""
        n1, n2 = alloc.groups_from_total(total=20, ratio=1.0)
        assert n1 + n2 == 20
        assert n1 == 10
        assert n2 == 10

    def test_equal_allocation_odd_total(self) -> None:
        """Test equal allocation with odd total."""
        n1, n2 = alloc.groups_from_total(total=21, ratio=1.0)
        assert n1 + n2 == 21
        # One group gets the extra participant
        assert abs(n1 - n2) <= 1

    def test_unequal_allocation_2to1(self) -> None:
        """Test 2:1 allocation."""
        n1, n2 = alloc.groups_from_total(total=30, ratio=2.0)
        assert n1 + n2 == 30
        # Expected: share = 30/(1+2) = 10, so n1=10, n2=20
        assert n1 == 10
        assert n2 == 20

    def test_unequal_allocation_1to2(self) -> None:
        """Test 1:2 allocation."""
        n1, n2 = alloc.groups_from_total(total=30, ratio=0.5)
        assert n1 + n2 == 30
        # Expected: share = 30/(1+0.5) = 20, so n1=20, n2=10
        assert n1 == 20
        assert n2 == 10

    def test_small_total_minimum_enforced(self) -> None:
        """Test minimum group sizes are enforced."""
        n1, n2 = alloc.groups_from_total(total=2, ratio=1.0)
        assert n1 + n2 == 2
        assert n1 >= 1
        assert n2 >= 1
        assert n1 == 1
        assert n2 == 1

    def test_extreme_ratio_large(self) -> None:
        """Test extreme ratio favoring n2."""
        n1, n2 = alloc.groups_from_total(total=11, ratio=10.0)
        assert n1 + n2 == 11
        assert n1 >= 1
        assert n2 >= 1
        # share = 11/(1+10) = 1, so n1=1, n2=10
        assert n1 == 1
        assert n2 == 10

    def test_extreme_ratio_small(self) -> None:
        """Test extreme ratio favoring n1."""
        n1, n2 = alloc.groups_from_total(total=11, ratio=0.1)
        assert n1 + n2 == 11
        assert n1 >= 1
        assert n2 >= 1
        # share = 11/(1+0.1) = 10, so n1=10, n2=1
        assert n1 == 10
        assert n2 == 1

    def test_rounding_edge_case(self) -> None:
        """Test edge case where rounding might cause issues."""
        n1, n2 = alloc.groups_from_total(total=7, ratio=1.5)
        assert n1 + n2 == 7
        assert n1 >= 1
        assert n2 >= 1
        # share = 7/(1+1.5) = 2.8, round to 3, so n1=3, n2=4
        assert n1 == 3
        assert n2 == 4

    def test_invalid_total_too_small(self) -> None:
        """Test validation fails for total < 2."""
        with pytest.raises(ValueError, match="total sample size must be at least 2"):
            alloc.groups_from_total(total=1, ratio=1.0)

        with pytest.raises(ValueError, match="total sample size must be at least 2"):
            alloc.groups_from_total(total=0, ratio=1.0)

    def test_invalid_ratio_zero(self) -> None:
        """Test validation fails for zero ratio."""
        with pytest.raises(ValueError, match="ratio must be positive"):
            alloc.groups_from_total(total=10, ratio=0.0)

    def test_invalid_ratio_negative(self) -> None:
        """Test validation fails for negative ratio."""
        with pytest.raises(ValueError, match="ratio must be positive"):
            alloc.groups_from_total(total=10, ratio=-1.0)


class TestAllocateByWeights:
    """Tests for allocate_by_weights function."""

    def test_equal_weights(self) -> None:
        """Test allocation with equal weights."""
        result = alloc.allocate_by_weights(total=12, weights=[1, 1, 1])
        assert sum(result) == 12
        assert len(result) == 3
        assert all(x == 4 for x in result)

    def test_unequal_weights(self) -> None:
        """Test allocation with unequal weights."""
        result = alloc.allocate_by_weights(total=10, weights=[1, 2, 3])
        assert sum(result) == 10
        assert len(result) == 3
        # Expected proportions: 1/6, 2/6, 3/6 of 10 = 1.67, 3.33, 5.0
        # Should be approximately [2, 3, 5]
        expected_approx = [2, 3, 5]
        for actual, expected in zip(result, expected_approx):
            assert abs(actual - expected) <= 1

    def test_weights_with_remainder(self) -> None:
        """Test allocation when total doesn't divide evenly."""
        result = alloc.allocate_by_weights(total=11, weights=[1, 1, 1])
        assert sum(result) == 11
        assert len(result) == 3
        # Should be close to [3.67, 3.67, 3.67] -> some get 4, some get 3
        assert all(x in [3, 4] for x in result)
        assert result.count(4) == 2  # 2 groups get the extra

    def test_large_weight_difference(self) -> None:
        """Test allocation with very different weights."""
        result = alloc.allocate_by_weights(total=20, weights=[1, 10])
        assert sum(result) == 20
        assert len(result) == 2
        # Expected: 1/11 * 20 ≈ 1.8, 10/11 * 20 ≈ 18.2
        # Should be approximately [2, 18]
        assert result[0] >= 1
        assert result[1] >= 1
        assert abs(result[0] - 2) <= 1
        assert abs(result[1] - 18) <= 1

    def test_minimum_group_size_enforced(self) -> None:
        """Test that all groups get at least 1 participant."""
        result = alloc.allocate_by_weights(total=5, weights=[1, 1, 1, 1, 1])
        assert sum(result) == 5
        assert len(result) == 5
        assert all(x >= 1 for x in result)
        assert all(x == 1 for x in result)

    def test_more_groups_than_total(self) -> None:
        """Test edge case with more groups than total observations."""
        with pytest.raises(ValueError, match="total must be >= number of groups"):
            alloc.allocate_by_weights(total=3, weights=[1, 1, 1, 1])

    def test_exact_total_equals_groups(self) -> None:
        """Test when total equals number of groups."""
        result = alloc.allocate_by_weights(total=3, weights=[1, 1, 1])
        assert sum(result) == 3
        assert all(x == 1 for x in result)

    def test_single_group(self) -> None:
        """Test allocation with single group."""
        result = alloc.allocate_by_weights(total=10, weights=[5])
        assert result == [10]

    def test_fractional_weights(self) -> None:
        """Test allocation with fractional weights."""
        result = alloc.allocate_by_weights(total=12, weights=[0.5, 1.5, 2.0])
        assert sum(result) == 12
        assert len(result) == 3
        # Proportions: 0.5/4, 1.5/4, 2.0/4 = 0.125, 0.375, 0.5
        # Of 12: 1.5, 4.5, 6.0 -> approximately [2, 4, 6]
        expected_approx = [2, 4, 6]
        for actual, expected in zip(result, expected_approx):
            assert abs(actual - expected) <= 1

    def test_empty_weights(self) -> None:
        """Test validation fails for empty weights."""
        with pytest.raises(ValueError, match="weights cannot be empty"):
            alloc.allocate_by_weights(total=10, weights=[])

    def test_zero_weight(self) -> None:
        """Test validation fails for zero weight."""
        with pytest.raises(ValueError, match="weights must be positive"):
            alloc.allocate_by_weights(total=10, weights=[1, 0, 2])

    def test_negative_weight(self) -> None:
        """Test validation fails for negative weight."""
        with pytest.raises(ValueError, match="weights must be positive"):
            alloc.allocate_by_weights(total=10, weights=[1, -1, 2])


class TestHarmonicMean:
    """Tests for harmonic_mean function."""

    def test_equal_values(self) -> None:
        """Test harmonic mean of equal values."""
        result = alloc.harmonic_mean([5, 5, 5, 5])
        assert result == 5.0

    def test_simple_case(self) -> None:
        """Test simple harmonic mean calculation."""
        # Harmonic mean of [2, 4] = 2 / (1/2 + 1/4) = 2 / (0.75) = 8/3 ≈ 2.67
        result = alloc.harmonic_mean([2, 4])
        expected = 2 / (1/2 + 1/4)
        assert abs(result - expected) < 1e-10

    def test_three_values(self) -> None:
        """Test harmonic mean of three values."""
        # Harmonic mean of [1, 2, 3] = 3 / (1/1 + 1/2 + 1/3) = 3 / (1 + 0.5 + 0.333...) ≈ 1.636
        result = alloc.harmonic_mean([1, 2, 3])
        expected = 3 / (1 + 0.5 + 1/3)
        assert abs(result - expected) < 1e-10

    def test_single_value(self) -> None:
        """Test harmonic mean of single value."""
        result = alloc.harmonic_mean([7.5])
        assert result == 7.5

    def test_large_values(self) -> None:
        """Test harmonic mean with large values."""
        result = alloc.harmonic_mean([100, 200, 300])
        # Harmonic mean should be less than arithmetic mean
        arith_mean = sum([100, 200, 300]) / 3
        assert result < arith_mean
        assert result > 0

    def test_small_values(self) -> None:
        """Test harmonic mean with small values."""
        result = alloc.harmonic_mean([0.1, 0.2, 0.3])
        expected = 3 / (1/0.1 + 1/0.2 + 1/0.3)
        assert abs(result - expected) < 1e-10

    def test_extreme_difference(self) -> None:
        """Test harmonic mean with very different values."""
        # Harmonic mean should be dominated by smaller values
        result = alloc.harmonic_mean([1, 1000])
        # Should be much closer to 1 than to 1000
        assert result < 10
        assert result > 1

    def test_fractional_values(self) -> None:
        """Test harmonic mean with fractional values."""
        result = alloc.harmonic_mean([1.5, 2.5, 3.5])
        expected = 3 / (1/1.5 + 1/2.5 + 1/3.5)
        assert abs(result - expected) < 1e-10

    def test_empty_values(self) -> None:
        """Test validation fails for empty values."""
        with pytest.raises(ValueError, match="values cannot be empty"):
            alloc.harmonic_mean([])

    def test_zero_value(self) -> None:
        """Test validation fails for zero value."""
        with pytest.raises(ValueError, match="harmonic mean defined for positive values"):
            alloc.harmonic_mean([1, 0, 3])

    def test_negative_value(self) -> None:
        """Test validation fails for negative value."""
        with pytest.raises(ValueError, match="harmonic mean defined for positive values"):
            alloc.harmonic_mean([1, -2, 3])


class TestIntegration:
    """Integration tests combining multiple allocation functions."""

    def test_allocation_consistency(self) -> None:
        """Test consistency between groups_from_n1 and groups_from_total."""
        # Start with n1 and ratio
        n1_orig = 15
        ratio = 1.5
        n1_result, n2_result = alloc.groups_from_n1(n1_orig, ratio)
        total = n1_result + n2_result
        
        # Convert back using groups_from_total
        n1_back, n2_back = alloc.groups_from_total(total, ratio)
        
        # Should be reasonably close to original
        assert abs(n1_back - n1_result) <= 1
        assert abs(n2_back - n2_result) <= 1
        assert n1_back + n2_back == total

    def test_weighted_allocation_vs_ratio(self) -> None:
        """Test allocate_by_weights matches ratio-based allocation."""
        total = 30
        ratio = 2.0  # n2 = 2 * n1
        
        # Using ratio method
        n1_ratio, n2_ratio = alloc.groups_from_total(total, ratio)
        
        # Using weights method (weight2 = 2 * weight1)
        weights_result = alloc.allocate_by_weights(total, [1, 2])
        
        # Should be close
        assert abs(weights_result[0] - n1_ratio) <= 1
        assert abs(weights_result[1] - n2_ratio) <= 1

    def test_harmonic_mean_with_allocation(self) -> None:
        """Test harmonic mean calculation with allocated group sizes."""
        # Allocate 60 participants to 4 groups with different weights
        weights = [1, 2, 3, 4]
        group_sizes = alloc.allocate_by_weights(60, weights)
        
        # Calculate harmonic mean
        h_mean = alloc.harmonic_mean(group_sizes)
        
        # Harmonic mean should be less than arithmetic mean
        arith_mean = sum(group_sizes) / len(group_sizes)
        assert h_mean < arith_mean
        
        # Should be positive and less than arithmetic mean
        assert h_mean > 0
        assert h_mean < arith_mean

    def test_edge_case_workflow(self) -> None:
        """Test edge case workflow with minimal allocations."""
        # Minimal case: 2 participants, equal allocation
        n1, n2 = alloc.groups_from_total(2, 1.0)
        assert n1 == 1
        assert n2 == 1
        
        # Harmonic mean of [1, 1]
        h_mean = alloc.harmonic_mean([n1, n2])
        assert h_mean == 1.0
        
        # Allocate by weights should give same result
        weights_result = alloc.allocate_by_weights(2, [1, 1])
        assert weights_result == [1, 1]