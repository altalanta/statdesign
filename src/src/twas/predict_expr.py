"""Predict genetically regulated expression (GReX)."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
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
    eqtl = pd.read_csv(Path(paths["eqtl_weights"]))

    snp_to_idx = {
        row.snp_id: idx for idx, row in cohort.snp_info.reset_index().itertuples(index=False)
    }

    genes = sorted(eqtl["gene"].unique())
    expr = np.zeros((cohort.genotypes.shape[0], len(genes)), dtype=float)

    for j, gene in enumerate(genes):
        sub = eqtl[eqtl["gene"] == gene]
        indices = []
        weights = []
        for snp, weight in zip(sub["snp_id"], sub["weight"]):
            idx = snp_to_idx.get(snp)
            if idx is None:
                continue
            indices.append(idx)
            weights.append(weight)
        if not weights:
            continue
        g = cohort.genotypes[:, indices]
        expr[:, j] = g @ np.asarray(weights)

    grex = pd.DataFrame(expr, columns=genes)
    grex.insert(0, "sample_id", cohort.covariates["sample_id"])
    out_dir = Path(paths["twas"]["plots_dir"]).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    grex.to_csv(out_dir / "predicted_expression.csv", index=False)
    return grex


def main() -> None:
    parser = argparse.ArgumentParser(description="Predict GReX")
    parser.add_argument("--config", type=Path, default=Path("config/config.yaml"))
    args = parser.parse_args()
    run(args.config)


if __name__ == "__main__":  # pragma: no cover
    main()
