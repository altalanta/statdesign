"""Mendelian randomization analyses."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
import yaml

from src.mr.harmonize import harmonize_sumstats
from src.utils import io
from src.utils.stats import MRResult, cochran_q, inverse_variance_weighted, mr_egger
from src.utils.viz import leave_one_out_plot, mr_forest_plot


def run(config_path: Path) -> pd.DataFrame:
    config = yaml.safe_load(config_path.read_text())
    paths: Dict[str, str] = config["paths"]

    exposure, outcome = io.load_sumstats(Path(paths["sumstats_exposure"]), Path(paths["sumstats_outcome"]))

    exposure_aligned, outcome_aligned = harmonize_sumstats(exposure, outcome)

    bx = exposure_aligned["beta_exposure"].to_numpy()
    by = outcome_aligned["beta_outcome"].to_numpy()
    sy = outcome_aligned["se_outcome"].to_numpy()

    ivw = inverse_variance_weighted(bx, by, sy)
    slope, intercept = mr_egger(bx, by, sy)
    q_stat = cochran_q(bx, by, sy)

    loo_estimates, loo_se = _leave_one_out(bx, by, sy)

    results = pd.DataFrame(
        [
            {"method": "IVW", "beta": ivw.beta, "se": ivw.se, "p_value": ivw.p_value},
            {"method": "MR-Egger slope", "beta": slope.beta, "se": slope.se, "p_value": slope.p_value},
            {"method": "MR-Egger intercept", "beta": intercept.beta, "se": intercept.se, "p_value": intercept.p_value},
            {"method": "Cochran_Q", "beta": q_stat, "se": np.nan, "p_value": np.nan},
        ]
    )

    out_dir = Path(paths["mr"]["plots_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    forest_path = out_dir / "forest.png"
    mr_forest_plot(by / bx, sy / bx, labels=exposure_aligned["snp"], out_path=forest_path, overall=(ivw.beta, ivw.se))
    leave_one_out_plot(loo_estimates, loo_se, exposure_aligned["snp"], out_dir / "leave_one_out.png")

    results_path = Path(paths["mr"]["results"])
    results_path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(results_path, index=False)
    return results


def _leave_one_out(beta_exposure: np.ndarray, beta_outcome: np.ndarray, se_outcome: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    estimates = []
    ses = []
    for i in range(len(beta_exposure)):
        mask = np.ones(len(beta_exposure), dtype=bool)
        mask[i] = False
        res = inverse_variance_weighted(beta_exposure[mask], beta_outcome[mask], se_outcome[mask])
        estimates.append(res.beta)
        ses.append(res.se)
    return np.asarray(estimates), np.asarray(ses)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Mendelian randomization")
    parser.add_argument("--config", type=Path, default=Path("config/config.yaml"))
    args = parser.parse_args()
    run(args.config)


if __name__ == "__main__":  # pragma: no cover
    main()
