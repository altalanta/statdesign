"""Ingest evidence into SQLite database."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
from typing import Dict

import pandas as pd
import yaml


def ingest(config_path: Path) -> None:
    config = yaml.safe_load(config_path.read_text())
    paths: Dict[str, str] = config["paths"]
    db_path = Path(paths["database"])
    with sqlite3.connect(db_path) as conn:
        _load_constraint_flags(conn, Path(paths["constraint_flags"]))
        _load_gwas(conn, Path(paths["gwas"]["results"]))
        _load_twas(conn, Path(paths["twas"]["results"]))
        _load_mr(conn, Path(paths["mr"]["results"]))
        _load_sv(conn, Path(paths["sv"]["results"]))


def _load_constraint_flags(conn: sqlite3.Connection, path: Path) -> None:
    df = pd.read_csv(path)
    df.to_sql("safety_flags", conn, if_exists="replace", index=False)


def _insert_target(conn: sqlite3.Connection, gene: str) -> None:
    conn.execute("INSERT OR IGNORE INTO targets (gene, description) VALUES (?, ?)", (gene, None))


def _insert_disease(conn: sqlite3.Connection, disease: str) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO diseases (disease, category) VALUES (?, ?)", (disease, "synthetic")
    )


def _load_gwas(conn: sqlite3.Connection, path: Path) -> None:
    if not path.exists():
        return
    df = pd.read_csv(path)
    top_hits = df[df["p_value"] < 5e-4].copy()
    top_hits["disease"] = top_hits["trait"]
    top_hits["source"] = "GWAS"
    top_hits["qc_flag"] = "OK"
    records = top_hits
    for row in records.itertuples(index=False):
        gene = getattr(row, "gene", None)
        if gene is None and hasattr(row, "snp_id"):
            gene = row.snp_id
        if gene is None:
            gene = str(getattr(row, "snp_index", "NA"))
        conn.execute(
            "INSERT INTO evidence (gene, disease, source, effect, p_value, qc_flag, details) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (gene, row.disease, row.source, row.beta, row.p_value, row.qc_flag, ""),
        )
        _insert_target(conn, gene)
        _insert_disease(conn, row.disease)


def _load_twas(conn: sqlite3.Connection, path: Path) -> None:
    if not path.exists():
        return
    df = pd.read_csv(path)
    for row in df[df["p_value"] < 1e-3].itertuples(index=False):
        conn.execute(
            "INSERT INTO evidence (gene, disease, source, effect, p_value, qc_flag, details) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (row.gene, row.trait, "TWAS", row.beta, row.p_value, "OK", ""),
        )
        _insert_target(conn, row.gene)
        _insert_disease(conn, row.trait)


def _load_mr(conn: sqlite3.Connection, path: Path) -> None:
    if not path.exists():
        return
    df = pd.read_csv(path)
    for row in df[df["method"] == "IVW"].itertuples(index=False):
        conn.execute(
            "INSERT INTO evidence (gene, disease, source, effect, p_value, qc_flag, details) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("GENE0001", "Disease", "MR", row.beta, row.p_value, "OK", "IVW estimate"),
        )
        _insert_target(conn, "GENE0001")
        _insert_disease(conn, "Disease")


def _load_sv(conn: sqlite3.Connection, path: Path) -> None:
    if not path.exists():
        return
    for file in ["cnv_assoc.csv", "repeat_assoc.csv"]:
        fpath = path.with_name(file)
        if not fpath.exists():
            continue
        df = pd.read_csv(fpath)
        for row in df.itertuples(index=False):
            conn.execute(
                "INSERT INTO evidence (gene, disease, source, effect, p_value, qc_flag, details) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("GENE0001", row.trait, "SV", row.beta, row.p_value, "QC", file),
            )
            _insert_target(conn, "GENE0001")
            _insert_disease(conn, row.trait)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest evidence into SQLite DB")
    parser.add_argument("--config", type=Path, default=Path("config/config.yaml"))
    args = parser.parse_args()
    ingest(args.config)


if __name__ == "__main__":  # pragma: no cover
    main()
