"""Two-step ridge GWAS workflow."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
import statsmodels.api as sm
import yaml
from scipy import stats
from sklearn.linear_model import Ridge

from src.gwas import qc
from src.utils import io
from src.utils.stats import benjamini_hochberg
from src.utils.viz import manhattan_plot, qq_plot


def run(config_path: Path) -> pd.DataFrame:
    config = yaml.safe_load(config_path.read_text())
    paths: Dict[str, str] = config["paths"]

    cohort = io.load_cohort(
        Path(paths["genotype"]),
        Path(paths["snp_ids"]),
        Path(paths["covariates"]),
        Path(paths["phenotypes"]),
    )

    genotype = cohort.genotypes
    qc_mask = qc.qc_filter(genotype)
    genotype = genotype[:, qc_mask]
    snp_info = cohort.snp_info.loc[qc_mask].reset_index(drop=True)

    phenos = cohort.phenotypes
    cov = cohort.covariates[["sex", "PC1", "PC2", "PC3"]].to_numpy()
    cov = (cov - cov.mean(axis=0)) / cov.std(axis=0)

    quant_trait = phenos["quant_trait"].to_numpy()
    ridge = Ridge(alpha=1.0)
    ridge.fit(genotype, quant_trait)
    pgs = ridge.predict(genotype)
    cov_aug = np.column_stack([cov, pgs])

    gwas_quant = _linear_scan(genotype, quant_trait, cov_aug)
    gwas_quant["trait"] = "quant_trait"

    disease = phenos["disease_status"].to_numpy()
    gwas_binary = _logistic_scan(genotype, disease, cov_aug)
    gwas_binary["trait"] = "disease_status"

    results = pd.concat([gwas_quant, gwas_binary], ignore_index=True)
    results = pd.merge(results, snp_info, left_on="snp_index", right_index=True)
    results["p_adj"] = benjamini_hochberg(results["p_value"].to_numpy())

    out_path = Path(paths["gwas"]["results"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(out_path, index=False)

    for trait, group in results.groupby("trait"):
        manhattan_plot(
            group,
            chrom_col="chrom",
            pos_col="position",
            p_col="p_value",
            out_path=Path(paths["gwas"]["plots_dir"]) / f"manhattan_{trait}.png",
        )
        qq_plot(
            group["p_value"].to_numpy(),
            out_path=Path(paths["gwas"]["plots_dir"]) / f"qq_{trait}.png",
        )
    return results


def _linear_scan(geno: np.ndarray, trait: np.ndarray, cov: np.ndarray) -> pd.DataFrame:
    n_snps = geno.shape[1]
    design = np.column_stack([np.ones(len(trait)), cov])
    beta_cov = np.linalg.lstsq(design, trait, rcond=None)[0]
    trait_resid = trait - design @ beta_cov

    rows = []
    for idx in range(n_snps):
        snp = geno[:, idx].astype(float)
        snp_design = np.linalg.lstsq(design, snp, rcond=None)[0]
        snp_resid = snp - design @ snp_design
        denom = np.sum(snp_resid**2)
        if denom == 0:
            continue
        beta = np.dot(snp_resid, trait_resid) / denom
        resid = trait_resid - beta * snp_resid
        dof = len(trait) - design.shape[1] - 1
        sigma2 = np.sum(resid**2) / dof
        se = np.sqrt(sigma2 / denom)
        z = beta / se
        p_val = 2 * (1 - stats.norm.cdf(abs(z)))
        rows.append(
            {
                "snp_index": idx,
                "beta": beta,
                "se": se,
                "p_value": p_val,
            }
        )
    return pd.DataFrame(rows)


def _logistic_scan(geno: np.ndarray, trait: np.ndarray, cov: np.ndarray) -> pd.DataFrame:
    rows = []
    base = sm.add_constant(cov)
    for idx in range(geno.shape[1]):
        X = np.column_stack([base, geno[:, idx]])
        try:
            model = sm.GLM(trait, X, family=sm.families.Binomial())
            res = model.fit(maxiter=50, disp=0)
            beta = res.params[-1]
            se = res.bse[-1]
            z = beta / se
            p_val = 2 * (1 - stats.norm.cdf(abs(z)))
        except Exception:  # pragma: no cover - convergence fallback
            beta = np.nan
            se = np.nan
            p_val = 1.0
        rows.append(
            {
                "snp_index": idx,
                "beta": beta,
                "se": se,
                "p_value": p_val,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ridge GWAS pipeline")
    parser.add_argument("--config", type=Path, default=Path("config/config.yaml"))
    args = parser.parse_args()
    run(args.config)


if __name__ == "__main__":  # pragma: no cover
    main()
