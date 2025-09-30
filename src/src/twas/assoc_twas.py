"""TWAS association tests between predicted expression and traits."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
import yaml
from scipy import stats

from src.utils import io
from src.utils.viz import volcano_plot


def run(config_path: Path) -> pd.DataFrame:
    """Run simple TWAS by regressing predicted expression on traits."""

    config = yaml.safe_load(config_path.read_text())
    paths: Dict[str, str] = config["paths"]

    pred_path = Path(paths["twas"]["plots_dir"]).parent / "predicted_expression.csv"
    grex = pd.read_csv(pred_path)

    phenotypes = io.load_cohort(
        Path(paths["genotype"]),
        Path(paths["snp_ids"]),
        Path(paths["covariates"]),
        Path(paths["phenotypes"]),
    ).phenotypes

    merged = pd.merge(grex, phenotypes, on="sample_id")

    results = []
    traits = ["quant_trait", "disease_status"]
    for gene in [col for col in grex.columns if col != "sample_id"]:
        expr = merged[gene].to_numpy()
        expr = (expr - expr.mean()) / (expr.std() + 1e-8)
        for trait in traits:
            y = merged[trait].to_numpy()
            if trait == "disease_status":
                slope, intercept, r, p, _ = stats.linregress(expr, y)
            else:
                slope, intercept, r, p, _ = stats.linregress(expr, y)
            results.append({
                "gene": gene,
                "trait": trait,
                "beta": slope,
                "p_value": p,
                "r": r,
            })

    df = pd.DataFrame(results)
    out_path = Path(paths["twas"]["results"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)

    for trait, trait_df in df.groupby("trait"):
        volcano_plot(
            trait_df["beta"],
            trait_df["p_value"],
            trait_df["gene"],
            Path(paths["twas"]["plots_dir"]) / f"volcano_{trait}.png",
        )

    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Run TWAS associations")
    parser.add_argument("--config", type=Path, default=Path("config/config.yaml"))
    args = parser.parse_args()
    run(args.config)


if __name__ == "__main__":  # pragma: no cover
    main()
