"""Performance benchmarks for core statdesign functions."""

import pytest

from statdesign import alpha_adjust, n_anova, n_mean, n_two_prop


class TestCoreBenchmarks:
    """Benchmark tests for core statistical functions."""

    @pytest.mark.benchmark(min_rounds=5, max_time=2.0, warmup=False)
    def test_benchmark_n_two_prop(self, benchmark):
        """Benchmark two-proportion sample size calculation."""
        result = benchmark(n_two_prop, p1=0.6, p2=0.5, alpha=0.05, power=0.8)
        assert isinstance(result, tuple)
        assert len(result) == 2

    @pytest.mark.benchmark(min_rounds=5, max_time=2.0, warmup=False)
    def test_benchmark_n_mean_z(self, benchmark):
        """Benchmark two-means sample size with z-test."""
        result = benchmark(n_mean, mu1=0.0, mu2=0.5, sd=1.0, alpha=0.05, power=0.8, test="z")
        assert isinstance(result, tuple)
        assert len(result) == 2

    @pytest.mark.benchmark(min_rounds=5, max_time=2.0, warmup=False)
    def test_benchmark_n_mean_t(self, benchmark):
        """Benchmark two-means sample size with t-test."""
        result = benchmark(n_mean, mu1=0.0, mu2=0.5, sd=1.0, alpha=0.05, power=0.8, test="t")
        assert isinstance(result, tuple)
        assert len(result) == 2

    @pytest.mark.benchmark(min_rounds=3, max_time=3.0, warmup=False)
    def test_benchmark_n_anova(self, benchmark):
        """Benchmark ANOVA sample size calculation."""
        # Note: This may require SciPy
        try:
            result = benchmark(n_anova, groups=4, cohen_f=0.25, alpha=0.05, power=0.8)
            assert isinstance(result, int)
            assert result > 0
        except RuntimeError as e:
            if "SciPy" in str(e):
                pytest.skip("SciPy not available for ANOVA calculation")
            else:
                raise

    @pytest.mark.benchmark(min_rounds=10, max_time=1.0, warmup=False)
    def test_benchmark_alpha_adjust_bonferroni(self, benchmark):
        """Benchmark Bonferroni correction."""
        result = benchmark(alpha_adjust, m=10, alpha=0.05, method="bonferroni")
        assert isinstance(result, float)
        assert 0 < result < 0.05

    @pytest.mark.benchmark(min_rounds=10, max_time=1.0, warmup=False)
    def test_benchmark_alpha_adjust_bh(self, benchmark):
        """Benchmark Benjamini-Hochberg correction."""
        result = benchmark(alpha_adjust, m=20, alpha=0.05, method="bh")
        assert isinstance(result, float)
        assert 0 < result < 0.05


class TestScalabilityBenchmarks:
    """Benchmark tests for function scalability."""

    @pytest.mark.benchmark(min_rounds=3, max_time=5.0, warmup=False)
    def test_benchmark_large_sample_proportions(self, benchmark):
        """Benchmark with large sample sizes for proportions."""
        # Test with proportions that would yield large sample sizes
        result = benchmark(n_two_prop, p1=0.501, p2=0.5, alpha=0.05, power=0.8)
        assert isinstance(result, tuple)
        assert all(n > 1000 for n in result)  # Should be large samples

    @pytest.mark.benchmark(min_rounds=3, max_time=5.0, warmup=False)
    def test_benchmark_small_effect_means(self, benchmark):
        """Benchmark with small effect sizes for means."""
        # Small effect size should require larger samples
        result = benchmark(n_mean, mu1=0.0, mu2=0.1, sd=1.0, alpha=0.05, power=0.8, test="z")
        assert isinstance(result, tuple)
        assert all(n > 100 for n in result)

    @pytest.mark.benchmark(min_rounds=2, max_time=10.0, warmup=False)
    def test_benchmark_many_groups_anova(self, benchmark):
        """Benchmark ANOVA with many groups."""
        try:
            result = benchmark(n_anova, groups=10, cohen_f=0.15, alpha=0.05, power=0.8)
            assert isinstance(result, int)
            assert result > 10  # Should need reasonable sample per group
        except RuntimeError as e:
            if "SciPy" in str(e):
                pytest.skip("SciPy not available for ANOVA calculation")
            else:
                raise


# Optional: only run benchmarks if pytest-benchmark is available
def pytest_configure(config):
    """Configure benchmark markers."""
    config.addinivalue_line("markers", "benchmark: mark test as a performance benchmark")
