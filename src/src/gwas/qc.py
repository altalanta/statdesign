"""Quality control utilities for GWAS analyses."""

from __future__ import annotations

import numpy as np

from src.utils.stats import genomic_inflation_lambda


def call_rate(genotypes: np.ndarray) -> np.ndarray:
    """Compute call rate per SNP (non-missing proportion)."""

    total = genotypes.shape[0]
    missing = np.sum(genotypes < 0, axis=0)
    return 1 - missing / total


def minor_allele_frequency(genotypes: np.ndarray) -> np.ndarray:
    """Estimate minor allele frequency per SNP."""

    geno = genotypes.copy().astype(float)
    geno[geno < 0] = np.nan
    allele_sum = np.nansum(geno, axis=0)
    n_called = np.sum(~np.isnan(geno), axis=0)
    maf = allele_sum / (2 * n_called)
    return np.minimum(maf, 1 - maf)


def hardy_weinberg_p(genotypes: np.ndarray) -> np.ndarray:
    """Exact test approximation for Hardy-Weinberg equilibrium."""

    counts = []
    for snp in genotypes.T:
        snp = snp[snp >= 0]
        obs_hom_ref = np.sum(snp == 0)
        obs_het = np.sum(snp == 1)
        obs_hom_alt = np.sum(snp == 2)
        n = obs_hom_ref + obs_het + obs_hom_alt
        if n == 0:
            counts.append(1.0)
            continue
        p = (2 * obs_hom_alt + obs_het) / (2 * n)
        expected = np.array(
            [
                (1 - p) ** 2 * n,
                2 * p * (1 - p) * n,
                p**2 * n,
            ]
        )
        observed = np.array([obs_hom_ref, obs_het, obs_hom_alt])
        chi2 = np.sum((observed - expected) ** 2 / (expected + 1e-8))
        p_val = 1 - _chi2_cdf(chi2, 1)
        counts.append(p_val)
    return np.asarray(counts)


def qc_filter(
    genotypes: np.ndarray,
    call_rate_threshold: float = 0.95,
    maf_threshold: float = 0.01,
    hwe_threshold: float = 1e-6,
) -> np.ndarray:
    """Return boolean mask of SNPs passing QC."""

    cr = call_rate(genotypes)
    maf = minor_allele_frequency(genotypes)
    hwe = hardy_weinberg_p(genotypes)
    return (cr >= call_rate_threshold) & (maf >= maf_threshold) & (hwe >= hwe_threshold)


def lambda_gc(p_values: np.ndarray) -> float:
    """Compute genomic control lambda from p-values."""

    chi2 = _chi2_from_p(p_values)
    return genomic_inflation_lambda(chi2)


def _chi2_from_p(p_values: np.ndarray) -> np.ndarray:
    return -2 * np.log(np.clip(p_values, 1e-300, 1.0))


def _chi2_cdf(x: float, df: int) -> float:
    from math import erf

    if df != 1:
        raise NotImplementedError("Only df=1 implemented")
    return erf(np.sqrt(x / 2))
