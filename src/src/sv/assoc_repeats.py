"""Repeat expansion association testing."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict

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
    repeats = pd.read_csv(Path(paths["repeats"]))

    repeat_mean = repeats.groupby("sample_id")["repeat_count"].mean()

    merged = cohort.phenotypes.merge(cohort.covariates, on="sample_id")
    merged["repeat_mean"] = merged["sample_id"].map(repeat_mean).fillna(0)

    cov = merged[["sex", "PC1", "PC2", "PC3"]]
    cov = (cov - cov.mean()) / (cov.std() + 1e-8)

    design = sm.add_constant(pd.concat([cov, merged[["repeat_mean"]]], axis=1))

    quant_model = sm.OLS(merged["quant_trait"], design).fit()
    disease_model = sm.GLM(merged["disease_status"], design, family=sm.families.Binomial()).fit()

    out = pd.DataFrame(
        [
            {
                "trait": "quant_trait",
                "beta": quant_model.params["repeat_mean"],
                "se": quant_model.bse["repeat_mean"],
                "p_value": quant_model.pvalues["repeat_mean"],
            },
            {
                "trait": "disease_status",
                "beta": disease_model.params["repeat_mean"],
                "se": disease_model.bse["repeat_mean"],
                "p_value": disease_model.pvalues["repeat_mean"],
            },
        ]
    )

    results_path = Path(paths["sv"]["results"]).with_name("repeat_assoc.csv")
    results_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(results_path, index=False)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Repeat association")
    parser.add_argument("--config", type=Path, default=Path("config/config.yaml"))
    args = parser.parse_args()
    run(args.config)


if __name__ == "__main__":  # pragma: no cover
    main()
