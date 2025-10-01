from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import yaml

from src.db.build_db import build
from src.db.ingest_evidence import ingest


def test_ingest(tmp_path: Path):
    db_path = tmp_path / "targetdb.sqlite"
    build(db_path)

    config = {
        "paths": {
            "database": str(db_path),
            "constraint_flags": str(tmp_path / "flags.csv"),
            "gwas": {
                "results": str(tmp_path / "gwas.csv"),
                "plots_dir": str(tmp_path / "gwas_plots"),
            },
            "twas": {
                "results": str(tmp_path / "twas.csv"),
                "plots_dir": str(tmp_path / "twas_plots"),
            },
            "mr": {"results": str(tmp_path / "mr.csv"), "plots_dir": str(tmp_path / "mr_plots")},
            "sv": {"results": str(tmp_path / "sv.csv")},
        }
    }
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(yaml.safe_dump(config))

    pd.DataFrame(
        {"gene": ["GENE0001"], "is_pLoF": [1], "is_pGoF": [0], "constraint_z": [2.1]}
    ).to_csv(config["paths"]["constraint_flags"], index=False)
    pd.DataFrame(
        {
            "snp_id": ["rs1"],
            "trait": ["quant_trait"],
            "beta": [0.2],
            "p_value": [1e-4],
            "source": ["GWAS"],
            "qc_flag": ["OK"],
            "snp_index": [0],
            "chrom": [1],
            "position": [1000],
        }
    ).to_csv(config["paths"]["gwas"]["results"], index=False)
    pd.DataFrame(
        {"gene": ["GENE0001"], "trait": ["quant_trait"], "beta": [0.5], "p_value": [0.001]}
    ).to_csv(config["paths"]["twas"]["results"], index=False)
    pd.DataFrame({"method": ["IVW"], "beta": [0.2], "se": [0.1], "p_value": [0.05]}).to_csv(
        config["paths"]["mr"]["results"], index=False
    )
    pd.DataFrame(
        {"trait": ["disease_status"], "beta": [0.1], "se": [0.05], "p_value": [0.02]}
    ).to_csv(Path(config["paths"]["sv"]["results"]).with_name("cnv_assoc.csv"), index=False)

    ingest(cfg_path)

    with sqlite3.connect(db_path) as conn:
        evidence_count = conn.execute("SELECT COUNT(*) FROM evidence").fetchone()[0]
    assert evidence_count > 0
