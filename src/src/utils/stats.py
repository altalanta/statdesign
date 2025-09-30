"""Statistical helpers for targetdb-mini."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

import numpy as np


@dataclass
class MRResult:
    beta: float
    se: float
    p_value: float


def benjamini_hochberg(p_values: Iterable[float]) -> np.ndarray:
    """Compute Benjamini-Hochberg adjusted p-values."""

    p = np.asarray(list(p_values), dtype=float)
    n = len(p)
    order = np.argsort(p)
    ranked = p[order]
    adj = np.empty_like(ranked)
    cumulative = 0.0
    for i in range(n - 1, -1, -1):
        rank = i + 1
        val = ranked[i] * n / rank
        cumulative = min(cumulative if cumulative > 0 else val, val)
        adj[i] = min(cumulative, 1.0)
    adjusted = np.empty_like(adj)
    adjusted[order] = adj
    return adjusted


def genomic_inflation_lambda(chi2: Iterable[float]) -> float:
    """Estimate genomic inflation factor lambda GC."""

    chi2_arr = np.asarray(list(chi2), dtype=float)
    if chi2_arr.size == 0:
        return 1.0
    median_chi2 = np.median(chi2_arr)
    return median_chi2 / 0.456


def inverse_variance_weighted(beta_exposure: np.ndarray, beta_outcome: np.ndarray, se_outcome: np.ndarray) -> MRResult:
    """Perform inverse variance weighted Mendelian randomization."""

    w = 1.0 / (se_outcome**2)
    beta = np.sum(w * beta_outcome / beta_exposure) / np.sum(w)
    se = np.sqrt(1.0 / np.sum(w))
    z = beta / se
    p = 2 * (1 - _norm_cdf(abs(z)))
    return MRResult(beta=beta, se=se, p_value=p)


def mr_egger(beta_exposure: np.ndarray, beta_outcome: np.ndarray, se_outcome: np.ndarray) -> Tuple[MRResult, MRResult]:
    """Run MR-Egger regression returning slope and intercept results."""

    x = beta_exposure
    y = beta_outcome
    w = 1.0 / (se_outcome**2)
    X = np.column_stack([np.ones_like(x), x])
    beta_hat = _weighted_ls(X, y, w)
    cov_beta = np.linalg.inv(X.T @ (w[:, None] * X))
    slope = beta_hat[1]
    intercept = beta_hat[0]
    slope_se = np.sqrt(cov_beta[1, 1])
    intercept_se = np.sqrt(cov_beta[0, 0])
    slope_p = 2 * (1 - _norm_cdf(abs(slope / slope_se)))
    intercept_p = 2 * (1 - _norm_cdf(abs(intercept / intercept_se)))
    return (
        MRResult(beta=slope, se=slope_se, p_value=slope_p),
        MRResult(beta=intercept, se=intercept_se, p_value=intercept_p),
    )


def cochran_q(beta_exposure: np.ndarray, beta_outcome: np.ndarray, se_outcome: np.ndarray) -> float:
    """Compute Cochran's Q statistic for heterogeneity."""

    w = 1.0 / (se_outcome**2)
    ivw_beta = np.sum(w * beta_outcome / beta_exposure) / np.sum(w)
    fitted = ivw_beta * beta_exposure
    q = np.sum(w * (beta_outcome - fitted) ** 2)
    return float(q)


def ld_prune(corr_matrix: np.ndarray, threshold: float = 0.2) -> List[int]:
    """Simple LD pruning returning retained SNP indices."""

    n = corr_matrix.shape[0]
    keep: List[int] = []
    for idx in range(n):
        correlated = False
        for kept in keep:
            if abs(corr_matrix[idx, kept]) > threshold:
                correlated = True
                break
        if not correlated:
            keep.append(idx)
    return keep


def _weighted_ls(X: np.ndarray, y: np.ndarray, w: np.ndarray) -> np.ndarray:
    XtW = X.T * w
    beta = np.linalg.solve(XtW @ X, XtW @ y)
    return beta


def _norm_cdf(x: float) -> float:
    return 0.5 * (1 + np.math.erf(x / np.sqrt(2)))
