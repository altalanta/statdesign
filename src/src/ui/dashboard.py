"""Streamlit dashboard for targetdb-mini."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

DB_PATH = Path("artifacts/targetdb.sqlite")
PLOTS_DIR = Path("artifacts")


def load_targets() -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as conn:
        targets = pd.read_sql_query("SELECT gene, description FROM targets", conn)
    return targets


def load_evidence(gene: str) -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as conn:
        evidence = pd.read_sql_query(
            "SELECT gene, disease, source, effect, p_value, qc_flag, details FROM evidence WHERE gene = ?",
            conn,
            params=(gene,),
        )
    return evidence


def main() -> None:
    st.set_page_config(page_title="targetdb-mini", layout="wide")
    st.title("TargetDB Mini Dashboard")

    if not DB_PATH.exists():
        st.warning("Database not found. Run `make db` first.")
        return

    targets = load_targets()
    gene = st.sidebar.selectbox("Gene", targets["gene"].unique())

    evidence = load_evidence(gene)
    st.subheader(f"Evidence for {gene}")
    st.dataframe(evidence)

    trait = st.sidebar.selectbox("Trait", ["quant_trait", "disease_status"])
    st.sidebar.write("Plots")
    manhattan = PLOTS_DIR / "gwas_plots" / f"manhattan_{trait}.png"
    qq = PLOTS_DIR / "gwas_plots" / f"qq_{trait}.png"
    volcano = PLOTS_DIR / "twas_plots" / f"volcano_{trait}.png"
    forest = PLOTS_DIR / "mr_plots" / "forest.png"

    cols = st.columns(2)
    if manhattan.exists():
        cols[0].image(str(manhattan), caption=f"GWAS Manhattan ({trait})")
    if qq.exists():
        cols[1].image(str(qq), caption=f"GWAS QQ ({trait})")
    if volcano.exists():
        st.image(str(volcano), caption=f"TWAS Volcano ({trait})")
    if forest.exists():
        st.image(str(forest), caption="MR Forest")


if __name__ == "__main__":  # pragma: no cover
    main()
