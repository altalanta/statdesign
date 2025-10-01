from __future__ import annotations

import csv
from pathlib import Path

from statdesign import api
from statdesign.core import ncf

DATA_DIR = Path(__file__).parent / "golden"


def _rows(path: str) -> list[dict[str, str]]:
    with (DATA_DIR / path).open(newline="") as handle:
        return list(csv.DictReader(handle))


def _parse_allocation(value: str | None) -> list[float] | None:
    if not value:
        return None
    return [float(part) for part in value.split(",")]


def _fallback_acceptance(result: int, expected: int) -> None:
    assert result >= expected
    overshoot = (result - expected) / expected
    assert overshoot <= 0.25  # fallback should remain within 25%


def _sci_acceptance(result: int, expected: int) -> None:
    assert result == expected


def _assert_match(result: int, expected: int) -> None:
    if ncf.has_scipy():
        _sci_acceptance(result, expected)
    else:
        _fallback_acceptance(result, expected)


for row in _rows("anova_golden.csv"):

    def _make_test(r: dict[str, str]) -> None:
        allocation = _parse_allocation(r.get("allocation"))
        result = api.n_anova(
            k_groups=int(r["k_groups"]),
            effect_f=float(r["effect_f"]),
            alpha=float(r["alpha"]),
            power=float(r["power"]),
            allocation=allocation,
        )
        _assert_match(result, int(r["exp_n"]))

    globals()[f"test_one_way_anova_{row['k_groups']}_{row['effect_f']}"] = lambda r=row: _make_test(
        r
    )
