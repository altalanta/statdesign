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


@pytest.mark.parametrize("row", _rows("anova_golden.csv"))
def test_one_way_anova(row: dict[str, str]) -> None:
    if not ncf.has_scipy():
        pytest.skip("SciPy not available for ANOVA sizing")
    allocation = None
    if row.get("allocation"):
        allocation = [float(part) for part in row["allocation"].split(",")]
    result = api.n_anova(
        k_groups=int(row["k_groups"]),
        effect_f=float(row["effect_f"]),
        alpha=float(row["alpha"]),
        power=float(row["power"]),
        allocation=allocation,
    )
    assert result == int(row["exp_n"])
