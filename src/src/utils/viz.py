"""Plotting utilities using matplotlib."""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def manhattan_plot(df: pd.DataFrame, chrom_col: str, pos_col: str, p_col: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df = df.copy()
    df["-log10p"] = -np.log10(df[p_col].clip(lower=1e-300))
    df.sort_values([chrom_col, pos_col], inplace=True)
    df["ind"] = range(len(df))
    fig, ax = plt.subplots(figsize=(10, 4))
    colors = ["#1f77b4", "#ff7f0e"]
    for chrom, group in df.groupby(chrom_col):
        ax.scatter(group["ind"], group["-log10p"], s=6, color=colors[int(chrom) % 2], label=f"chr{chrom}")
    ax.axhline(-np.log10(5e-8), color="red", linestyle="--", linewidth=1)
    ax.set_xlabel("Genomic position")
    ax.set_ylabel("-log10 p-value")
    ax.set_title("Manhattan plot")
    ax.set_ylim(0, df["-log10p"].max() + 1)
    ax.legend(fontsize=6, ncol=6, frameon=False)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def qq_plot(p_values: Sequence[float], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    p_sorted = np.sort(np.clip(p_values, 1e-300, 1.0))
    exp = -np.log10(np.linspace(1 / (len(p_sorted) + 1), 1, len(p_sorted)))
    obs = -np.log10(p_sorted)
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.scatter(exp, obs, s=8)
    ax.plot([0, exp.max()], [0, exp.max()], color="grey", linestyle="--", linewidth=1)
    ax.set_xlabel("Expected -log10 p")
    ax.set_ylabel("Observed -log10 p")
    ax.set_title("QQ plot")
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def volcano_plot(effect: Sequence[float], p_values: Sequence[float], gene_names: Sequence[str], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    effect = np.asarray(effect)
    logp = -np.log10(np.clip(p_values, 1e-300, 1.0))
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(effect, logp, s=10, color="#4c72b0", alpha=0.8)
    top_idx = np.argsort(logp)[-5:]
    for idx in top_idx:
        ax.text(effect[idx], logp[idx], gene_names[idx], fontsize=7)
    ax.set_xlabel("Effect size")
    ax.set_ylabel("-log10 p-value")
    ax.set_title("Volcano plot")
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def mr_forest_plot(beta: Sequence[float], se: Sequence[float], labels: Sequence[str], out_path: Path, overall: tuple[float, float] | None = None) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    beta = np.asarray(beta)
    se = np.asarray(se)
    y_pos = np.arange(len(beta))
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.errorbar(beta, y_pos, xerr=1.96 * se, fmt="o", color="black")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.axvline(0, color="grey", linestyle="--")
    if overall is not None:
        ax.errorbar(overall[0], len(beta) + 0.5, xerr=1.96 * overall[1], fmt="s", color="red", label="IVW")
        ax.set_ylim(-1, len(beta) + 1)
    ax.set_xlabel("Effect size")
    ax.set_title("MR Forest plot")
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def leave_one_out_plot(beta: Sequence[float], se: Sequence[float], labels: Sequence[str], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    beta = np.asarray(beta)
    se = np.asarray(se)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.errorbar(range(len(beta)), beta, yerr=1.96 * se, fmt="o", color="#ff7f0e")
    ax.axhline(0, color="grey", linestyle="--")
    ax.set_xticks(range(len(beta)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_ylabel("IVW beta")
    ax.set_title("Leave-one-out MR")
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
