"""FastAPI application serving target database."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from src.db.build_db import build

DB_PATH = Path("artifacts/targetdb.sqlite")


class Target(BaseModel):
    gene: str
    description: str | None = None


class Evidence(BaseModel):
    gene: str
    disease: str
    source: str
    effect: float | None
    p_value: float | None
    qc_flag: str | None
    details: str | None


app = FastAPI(title="targetdb-mini")


@app.on_event("startup")
def start_db() -> None:
    if not DB_PATH.exists():
        build(DB_PATH)


@app.get("/targets", response_model=List[Target])
def list_targets(limit: int = 20) -> List[Target]:
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT gene, description FROM targets LIMIT ?", (limit,)).fetchall()
    return [Target(gene=row[0], description=row[1]) for row in rows]


@app.get("/targets/{gene}", response_model=List[Evidence])
def target_detail(gene: str) -> List[Evidence]:
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT gene, disease, source, effect, p_value, qc_flag, details FROM evidence WHERE gene = ?",
            (gene,),
        ).fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="Gene not found")
    return [
        Evidence(
            **{
                "gene": row[0],
                "disease": row[1],
                "source": row[2],
                "effect": row[3],
                "p_value": row[4],
                "qc_flag": row[5],
                "details": row[6],
            }
        )
        for row in rows
    ]


@app.get("/search", response_model=List[Evidence])
def search(disease: str = Query(...)) -> List[Evidence]:
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT gene, disease, source, effect, p_value, qc_flag, details FROM evidence WHERE disease LIKE ?",
            (f"%{disease}%",),
        ).fetchall()
    return [
        Evidence(
            **{
                "gene": row[0],
                "disease": row[1],
                "source": row[2],
                "effect": row[3],
                "p_value": row[4],
                "qc_flag": row[5],
                "details": row[6],
            }
        )
        for row in rows
    ]
