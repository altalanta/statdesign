from __future__ import annotations

import pandas as pd

from src.mr.harmonize import harmonize_sumstats


def test_harmonize_basic():
    exposure = pd.DataFrame(
        {
            "snp": ["rs1", "rs2"],
            "beta_exposure": [0.1, 0.2],
            "effect_allele": ["A", "C"],
            "other_allele": ["G", "T"],
        }
    )
    outcome = pd.DataFrame(
        {
            "snp": ["rs1", "rs2"],
            "beta_outcome": [0.05, -0.02],
            "se_outcome": [0.01, 0.02],
            "effect_allele": ["A", "T"],
            "other_allele": ["G", "C"],
        }
    )
    exp, out = harmonize_sumstats(exposure, outcome)
    assert (exp["snp"] == out["snp"]).all()
    assert out.loc[out["snp"] == "rs2", "beta_outcome"].iloc[0] == 0.02
