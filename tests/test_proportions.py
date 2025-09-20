from __future__ import annotations

import csv
from pathlib import Path

import pytest

from statdesign import api

DATA_DIR = Path(__file__).parent / "golden"


def _rows(path: str) -> list[dict[str, str]]:
    with (DATA_DIR / path).open(newline="") as handle:
        return list(csv.DictReader(handle))


@pytest.mark.parametrize("row", _rows("two_prop_normal_golden.csv"))
def test_two_prop_normal(row: dict[str, str]) -> None:
    options = {
        "p1": float(row["p1"]),
        "p2": float(row["p2"]),
        "alpha": float(row["alpha"]),
        "power": float(row["power"]),
        "ratio": float(row["ratio"]),
        "tail": row["tail"],
        "test": row.get("test") or "z",
    }
    if row.get("ni_margin"):
        options["ni_margin"] = float(row["ni_margin"])
    if row.get("ni_type"):
        options["ni_type"] = row["ni_type"]
    result = api.n_two_prop(**options)
    assert result == (int(row["exp_n1"]), int(row["exp_n2"]))


@pytest.mark.parametrize("row", _rows("two_prop_exact_golden.csv"))
def test_two_prop_exact(row: dict[str, str]) -> None:
    options = {
        "p1": float(row["p1"]),
        "p2": float(row["p2"]),
        "alpha": float(row["alpha"]),
        "power": float(row["power"]),
        "ratio": float(row["ratio"]),
        "tail": row["tail"],
        "exact": True,
    }
    result = api.n_two_prop(**options)
    assert result == (int(row["exp_n1"]), int(row["exp_n2"]))


@pytest.mark.parametrize("row", _rows("one_sample_prop_golden.csv"))
def test_one_sample_prop(row: dict[str, str]) -> None:
    options = {
        "p": float(row["p"]),
        "p0": float(row["p0"]),
        "alpha": float(row["alpha"]),
        "power": float(row["power"]),
        "tail": row["tail"],
        "exact": row["exact"].lower() == "true",
    }
    if row.get("ni_margin"):
        options["ni_margin"] = float(row["ni_margin"])
    if row.get("ni_type"):
        options["ni_type"] = row["ni_type"]
    result = api.n_one_sample_prop(**options)
    assert result == int(row["exp_n"])
