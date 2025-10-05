"""Utilities to generate deterministic synthetic datasets for targetdb-mini."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd


def _make_dirs(paths: Dict[str, Path]) -> None:
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)


def generate_all(seed: int = 42) -> None:
    """Generate all synthetic data assets required for the demo repo."""

    rng = np.random.default_rng(seed)
    base_paths = {
        "genotype": Path("data/genotypes.npy"),
        "snp_ids": Path("data/snp_ids.csv"),
        "covariates": Path("data/covariates.csv"),
        "phenotypes": Path("data/phenotypes.csv"),
        "eqtl": Path("data/eqtl_weights.csv"),
        "pqtl": Path("data/pqtl_weights.csv"),
        "sumstats_exp": Path("data/sumstats_exposure.csv"),
        "sumstats_out": Path("data/sumstats_outcome.csv"),
        "cnv": Path("data/cnv_calls.csv"),
        "repeats": Path("data/repeats.csv"),
        "gnomad": Path("data/gnomad_lof_flags.csv"),
    }
    _make_dirs(base_paths)

    n_samples = 1_000
    n_snps = 5_000

    maf = rng.uniform(0.05, 0.5, size=n_snps)
    genotypes = rng.binomial(2, maf, size=(n_samples, n_snps)).astype(np.int8)
    np.save(base_paths["genotype"], genotypes)

    snp_ids = pd.DataFrame(
        {
            "snp_id": [f"rs{i:06d}" for i in range(1, n_snps + 1)],
            "maf": maf,
            "chrom": rng.integers(1, 23, size=n_snps),
            "position": rng.integers(1, 5_000_000, size=n_snps),
        }
    )
    snp_ids.to_csv(base_paths["snp_ids"], index=False)

    covariates = pd.DataFrame(
        {
            "sample_id": [f"IID{i:04d}" for i in range(n_samples)],
            "sex": rng.integers(0, 2, size=n_samples),
            "PC1": rng.normal(0, 1, n_samples),
            "PC2": rng.normal(0, 1, n_samples),
            "PC3": rng.normal(0, 1, n_samples),
        }
    )
    covariates.to_csv(base_paths["covariates"], index=False)

    causal_snps = np.array([10, 25, 40])  # zero-based indices
    beta_quant = np.array([0.8, -0.6, 0.5])
    beta_logit = np.array([0.9, -0.7, 0.5])

    g_causal = genotypes[:, causal_snps]
    cov_matrix = covariates[["sex", "PC1", "PC2", "PC3"]].to_numpy()

    noise_q = rng.normal(0, 1.0, size=n_samples)
    quant_trait = g_causal @ beta_quant + 0.3 * cov_matrix[:, 1] - 0.2 * cov_matrix[:, 2] + noise_q

    logits = (
        g_causal @ beta_logit
        + 0.4 * cov_matrix[:, 0]
        + 0.2 * cov_matrix[:, 1]
        + rng.normal(0, 0.5, size=n_samples)
    )
    prob = 1 / (1 + np.exp(-logits))
    binary_trait = rng.binomial(1, prob)

    phenotypes = covariates[["sample_id"]].copy()
    phenotypes["disease_status"] = binary_trait
    phenotypes["quant_trait"] = quant_trait
    phenotypes.to_csv(base_paths["phenotypes"], index=False)

    genes = [f"GENE{i:04d}" for i in range(1, 301)]
    eqtl_rows = []
    pqtl_rows = []
    for gene in genes:
        snp_indices = rng.choice(n_snps, size=3, replace=False)
        weights = rng.normal(0, 0.2, size=3)
        for idx, w in zip(snp_indices, weights):
            eqtl_rows.append(
                {
                    "gene": gene,
                    "snp_id": snp_ids.loc[idx, "snp_id"],
                    "weight": w,
                }
            )
            pqtl_rows.append(
                {
                    "protein": gene.replace("GENE", "PROT"),
                    "snp_id": snp_ids.loc[idx, "snp_id"],
                    "weight": w + rng.normal(0, 0.05),
                }
            )
    pd.DataFrame(eqtl_rows).to_csv(base_paths["eqtl"], index=False)
    pd.DataFrame(pqtl_rows).to_csv(base_paths["pqtl"], index=False)

    instruments = snp_ids.sample(n=10, random_state=seed).copy()
    instruments["beta_exposure"] = rng.normal(0.1, 0.02, size=len(instruments))
    instruments["se_exposure"] = rng.uniform(0.01, 0.05, size=len(instruments))
    instruments.loc[instruments.index[-1], "beta_exposure"] = 0.005
    instruments.loc[instruments.index[-1], "se_exposure"] = 0.2
    instruments.rename(columns={"snp_id": "snp"}).to_csv(base_paths["sumstats_exp"], index=False)

    outcome = instruments.copy()
    outcome["beta_outcome"] = outcome["beta_exposure"] * 0.6 + rng.normal(
        0, 0.02, size=len(outcome)
    )
    outcome["se_outcome"] = rng.uniform(0.015, 0.06, size=len(outcome))
    outcome.rename(columns={"snp_id": "snp"}).to_csv(base_paths["sumstats_out"], index=False)

    cnv_sample = rng.choice(covariates["sample_id"], size=80, replace=False)
    cnv_start = rng.integers(1, 5_000_000, size=80)
    cnv_length = rng.integers(10_000, 200_000, size=80)
    cnv_df = pd.DataFrame(
        {
            "sample_id": cnv_sample,
            "start": cnv_start,
            "end": cnv_start + cnv_length,
        }
    )
    cnv_df["type"] = rng.choice(["DEL", "DUP"], size=80)
    cnv_df["length"] = cnv_length
    cnv_df.to_csv(base_paths["cnv"], index=False)

    repeats = pd.DataFrame(
        {
            "sample_id": rng.choice(covariates["sample_id"], size=120, replace=True),
            "locus": rng.choice(["STR1", "STR2", "STR3"], size=120),
            "repeat_count": rng.integers(10, 80, size=120),
        }
    )
    repeats.to_csv(base_paths["repeats"], index=False)

    gnomad = pd.DataFrame(
        {
            "gene": genes,
            "is_pLoF": rng.binomial(1, 0.1, size=len(genes)),
            "is_pGoF": rng.binomial(1, 0.05, size=len(genes)),
            "constraint_z": rng.normal(0, 1.5, size=len(genes)),
        }
    )
    gnomad.to_csv(base_paths["gnomad"], index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic data")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    generate_all(args.seed)


if __name__ == "__main__":
    main()
