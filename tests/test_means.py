from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from statdesign import api
from statdesign.core import ncf

DATA_DIR = Path(__file__).parent / "golden"


def _rows(path: str) -> list[dict[str, str]]:
    with (DATA_DIR / path).open(newline="") as handle:
        return list(csv.DictReader(handle))


def _options(row: dict[str, str]) -> dict[str, Any]:
    opts: dict[str, Any] = {
        "alpha": float(row["alpha"]),
        "power": float(row["power"]),
        "tail": row["tail"],
    }
    if row.get("ni_margin"):
        opts["ni_margin"] = float(row["ni_margin"])
    if row.get("ni_type"):
        opts["ni_type"] = row["ni_type"]
    return opts


def _slug(value: str) -> str:
    return value.replace("-", "_neg").replace(".", "_")


def _assert_mean_result(result: tuple[int, int], row: dict[str, str]) -> None:
    expected = (int(row["exp_n1"]), int(row["exp_n2"]))
    if (row.get("test") or "t") == "t" and not ncf.has_scipy():
        z_options = {
            "mu1": float(row["mu1"]),
            "mu2": float(row["mu2"]),
            "sd": float(row["sd"]),
            "ratio": float(row["ratio"]),
            "test": "z",
            **_options(row),
        }
        z_result = api.n_mean(**z_options)
        assert result[0] >= z_result[0]
        assert result[1] >= z_result[1]
    else:
        assert result == expected


def _assert_one_sample_result(result: int, row: dict[str, str]) -> None:
    expected = int(row["exp_n"])
    if (row.get("test") or "t") == "t" and not ncf.has_scipy():
        z_result = api.n_one_sample_mean(
            delta=float(row["delta"]),
            sd=float(row["sd"]),
            test="z",
            **_options(row),
        )
        assert result >= z_result
    else:
        assert result == expected


def _assert_paired_result(result: int, row: dict[str, str]) -> None:
    expected = int(row["exp_n"])
    if not ncf.has_scipy():
        assert result >= expected
    else:
        assert result == expected


for row in _rows("means_two_sample_golden.csv"):

    def _make_two_sample(r: dict[str, str]) -> None:
        options = {
            "mu1": float(r["mu1"]),
            "mu2": float(r["mu2"]),
            "sd": float(r["sd"]),
            "ratio": float(r["ratio"]),
            "test": r.get("test") or "t",
            **_options(r),
        }
        result = api.n_mean(**options)
        _assert_mean_result(result, r)

    globals()[
        f"test_two_sample_means_{row['test'] or 't'}_{_slug(row['mu1'])}_{_slug(row['mu2'])}"
    ] = (lambda r=row: _make_two_sample(r))


for row in _rows("one_sample_mean_golden.csv"):

    def _make_one_sample(r: dict[str, str]) -> None:
        options = {
            "delta": float(r["delta"]),
            "sd": float(r["sd"]),
            "test": r.get("test") or "t",
            **_options(r),
        }
        result = api.n_one_sample_mean(**options)
        _assert_one_sample_result(result, r)

    globals()[
        f"test_one_sample_mean_{row.get('test') or 't'}_{_slug(row['delta'])}"
    ] = (lambda r=row: _make_one_sample(r))


for row in _rows("paired_mean_golden.csv"):

    def _make_paired(r: dict[str, str]) -> None:
        options = {
            "delta": float(r["delta"]),
            "sd_diff": float(r["sd_diff"]),
            **_options(r),
        }
        result = api.n_paired(**options)
        _assert_paired_result(result, r)

    globals()[f"test_paired_mean_{_slug(row['delta'])}"] = (lambda r=row: _make_paired(r))
