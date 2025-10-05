"""Harmonize exposure and outcome summary statistics for MR."""

from __future__ import annotations

from typing import Tuple

import pandas as pd


def harmonize_sumstats(
    exposure: pd.DataFrame, outcome: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Align alleles between exposure and outcome datasets."""

    outcome = outcome.copy()
    exposure = exposure.copy()

    common = set(exposure["snp"]).intersection(outcome["snp"])
    exposure = exposure[exposure["snp"].isin(common)].reset_index(drop=True)
    outcome = outcome[outcome["snp"].isin(common)].reset_index(drop=True)

    outcome = outcome.set_index("snp").loc[exposure["snp"]].reset_index()

    palindromic = {
        frozenset({"A", "T"}),
        frozenset({"C", "G"}),
    }

    if {"effect_allele", "other_allele"}.issubset(exposure.columns) and {
        "effect_allele",
        "other_allele",
    }.issubset(outcome.columns):
        aligned_beta = []
        aligned_se = []
        for _, exp_row, out_row in zip(
            range(len(exposure)), exposure.itertuples(), outcome.itertuples()
        ):
            exp_effect = getattr(exp_row, "effect_allele", None)
            out_effect = getattr(out_row, "effect_allele", None)
            if exp_effect == out_effect:
                aligned_beta.append(out_row.beta_outcome)
                aligned_se.append(out_row.se_outcome)
            elif getattr(out_row, "other_allele", None) == exp_effect:
                aligned_beta.append(-out_row.beta_outcome)
                aligned_se.append(out_row.se_outcome)
            elif frozenset({exp_effect, out_effect}) in palindromic:
                aligned_beta.append(out_row.beta_outcome)
                aligned_se.append(out_row.se_outcome)
            else:
                aligned_beta.append(out_row.beta_outcome)
                aligned_se.append(out_row.se_outcome)
        outcome["beta_outcome"] = aligned_beta
        outcome["se_outcome"] = aligned_se

    return exposure, outcome
