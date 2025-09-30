"""CNV association analysis."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
import statsmodels.api as sm
import yaml

from src.utils import io


def run(config_path: Path) -> pd.DataFrame:
    config = yaml.safe_load(config_path.read_text())
    paths: Dict[str, str] = config["paths"]
    cohort = io.load_cohort(
        Path(paths["genotype"]),
        Path(paths["snp_ids"]),
        Path(paths["covariates"]),
        Path(paths["phenotypes"]),
    )
    cnv = pd.read_csv(Path(paths["cnv_calls"]))

    burden = cnv.groupby("sample_id")["length"].sum()
    merged = cohort.phenotypes.merge(cohort.covariates, on="sample_id")
    merged["cnv_burden"] = merged["sample_id"].map(burden).fillna(0)

    cov = merged[["sex", "PC1", "PC2", "PC3"]].to_numpy()
    cov = (cov - cov.mean(axis=0)) / (cov.std(axis=0) + 1e-8)

    disease = merged["disease_status"].to_numpy()
    design = sm.add_constant(np.column_stack([cov, merged["cnv_burden"].to_numpy()]))
    model = sm.GLM(disease, design, family=sm.families.Binomial())
    res = model.fit(maxiter=50, disp=0)
    cnv_beta = res.params[-1]
    cnv_se = res.bse[-1]
    p_value = res.pvalues[-1]

    quant = merged["quant_trait"].to_numpy()
    model_lm = sm.OLS(quant, design)
    res_lm = model_lm.fit()
    beta_quant = res_lm.params[-1]
    se_quant = res_lm.bse[-1]
    p_quant = res_lm.pvalues[-1]

    out = pd.DataFrame(
        {
            "trait": ["disease_status", "quant_trait"],
            "beta": [cnv_beta, beta_quant],
            "se": [cnv_se, se_quant],
            "p_value": [p_value, p_quant],
        }
    )

    results_path = Path(paths["sv"]["results"]).with_name("cnv_assoc.csv")
    results_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(results_path, index=False)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="CNV association")
    parser.add_argument("--config", type=Path, default=Path("config/config.yaml"))
    args = parser.parse_args()
    run(args.config)


if __name__ == "__main__":  # pragma: no cover
    main()
