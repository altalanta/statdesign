"""I/O helpers for targetdb-mini."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd


@dataclass
class CohortData:
    genotypes: np.ndarray
    snp_info: pd.DataFrame
    covariates: pd.DataFrame
    phenotypes: pd.DataFrame


def load_cohort(genotype_path: Path, snp_path: Path, covariate_path: Path, phenotype_path: Path) -> CohortData:
    """Load cohort data from disk."""

    genotypes = np.load(genotype_path)
    snp_info = pd.read_csv(snp_path)
    covariates = pd.read_csv(covariate_path)
    phenotypes = pd.read_csv(phenotype_path)
    expected_cols = {"sex", "PC1", "PC2", "PC3"}
    if not expected_cols.issubset(covariates.columns):
        raise ValueError("Covariates missing expected columns")
    return CohortData(genotypes, snp_info, covariates, phenotypes)


def load_sumstats(exposure_path: Path, outcome_path: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    exposure = pd.read_csv(exposure_path)
    outcome = pd.read_csv(outcome_path)
    return exposure, outcome


def save_dataframe(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
