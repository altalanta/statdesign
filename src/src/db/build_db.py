"""SQLite database builder for targetdb-mini."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS targets (
  gene TEXT PRIMARY KEY,
  description TEXT
);
CREATE TABLE IF NOT EXISTS diseases (
  disease TEXT PRIMARY KEY,
  category TEXT
);
CREATE TABLE IF NOT EXISTS evidence (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  gene TEXT,
  disease TEXT,
  source TEXT,
  effect REAL,
  p_value REAL,
  qc_flag TEXT,
  details TEXT
);
CREATE TABLE IF NOT EXISTS safety_flags (
  gene TEXT PRIMARY KEY,
  is_pLoF INTEGER,
  is_pGoF INTEGER,
  constraint_z REAL
);
CREATE TABLE IF NOT EXISTS sources (
  name TEXT PRIMARY KEY,
  description TEXT
);
"""


def build(database_path: Path) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as conn:
        conn.executescript(SCHEMA)
        conn.execute("INSERT OR IGNORE INTO sources (name, description) VALUES (?, ?)", ("GWAS", "Genome-wide association"))
        conn.execute("INSERT OR IGNORE INTO sources (name, description) VALUES (?, ?)", ("TWAS", "Transcriptome-wide association"))
        conn.execute("INSERT OR IGNORE INTO sources (name, description) VALUES (?, ?)", ("MR", "Mendelian randomization"))
        conn.execute("INSERT OR IGNORE INTO sources (name, description) VALUES (?, ?)", ("SV", "Structural variation"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build SQLite schema")
    parser.add_argument("--database", type=Path, default=Path("artifacts/targetdb.sqlite"))
    args = parser.parse_args()
    build(args.database)


if __name__ == "__main__":  # pragma: no cover
    main()
