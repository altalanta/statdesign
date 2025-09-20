from __future__ import annotations

import csv
from pathlib import Path

import pytest

from statdesign import api
from statdesign.core import ncf

DATA_DIR = Path(__file__).parent / "golden"


def _rows(path: str) -> list[dict[str, str]]:
    with (DATA_DIR / path).open(newline="") as handle:
        return list(csv.DictReader(handle))


@pytest.mark.parametrize("row", _rows("means_two_sample_golden.csv"))
def test_two_sample_means(row: dict[str, str]) -> None:
    test_kind = row["test"] or "t"
    if test_kind == "t" and not ncf.has_scipy():
        pytest.skip("SciPy not available for t-based calculation")
    options = {
        "mu1": float(row["mu1"]),
        "mu2": float(row["mu2"]),
        "sd": float(row["sd"]),
        "alpha": float(row["alpha"]),
        "power": float(row["power"]),
        "ratio": float(row["ratio"]),
        "test": test_kind,
        "tail": row["tail"],
    }
    if row.get("ni_margin"):
        options["ni_margin"] = float(row["ni_margin"])
    if row.get("ni_type"):
        options["ni_type"] = row["ni_type"]
    result = api.n_mean(**options)
    assert result == (int(row["exp_n1"]), int(row["exp_n2"]))


@pytest.mark.parametrize("row", _rows("one_sample_mean_golden.csv"))
def test_one_sample_mean(row: dict[str, str]) -> None:
    test_kind = row.get("test") or "t"
    if test_kind == "t" and not ncf.has_scipy():
        pytest.skip("SciPy not available for t-based calculation")
    options = {
        "delta": float(row["delta"]),
        "sd": float(row["sd"]),
        "alpha": float(row["alpha"]),
        "power": float(row["power"]),
        "tail": row["tail"],
        "test": test_kind,
    }
    if row.get("ni_margin"):
        options["ni_margin"] = float(row["ni_margin"])
    if row.get("ni_type"):
        options["ni_type"] = row["ni_type"]
    result = api.n_one_sample_mean(**options)
    assert result == int(row["exp_n"])


@pytest.mark.parametrize("row", _rows("paired_mean_golden.csv"))
def test_paired_mean(row: dict[str, str]) -> None:
    if not ncf.has_scipy():
        pytest.skip("SciPy not available for paired t calculation")
    options = {
        "delta": float(row["delta"]),
        "sd_diff": float(row["sd_diff"]),
        "alpha": float(row["alpha"]),
        "power": float(row["power"]),
        "tail": row["tail"],
    }
    if row.get("ni_margin"):
        options["ni_margin"] = float(row["ni_margin"])
    if row.get("ni_type"):
        options["ni_type"] = row["ni_type"]
    result = api.n_paired(**options)
    assert result == int(row["exp_n"])
