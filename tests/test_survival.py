from __future__ import annotations

import csv
from pathlib import Path

import pytest

from statdesign import api

DATA_DIR = Path(__file__).parent / "golden"


def _load(path: str) -> list[dict[str, str]]:
    with (DATA_DIR / path).open(newline="") as handle:
        return list(csv.DictReader(handle))


@pytest.mark.parametrize("row", _load("survival_events_golden.csv"))
def test_required_events_logrank(row: dict[str, str]) -> None:
    events = api.required_events_logrank(
        hr=float(row["hr"]),
        alpha=float(row["alpha"]),
        power=float(row["power"]),
        allocation=float(row["allocation"]),
        tail=row["tail"],
    )
    assert pytest.approx(float(row["exp_events"]), rel=1e-3) == events


@pytest.mark.parametrize("row", _load("survival_convertN_golden.csv"))
def test_events_to_n(row: dict[str, str]) -> None:
    total, _, _ = api.events_to_n_exponential(
        events_required=float(row["events_required"]),
        accrual_years=float(row["accrual_years"]),
        followup_years=float(row["followup_years"]),
        base_hazard_ctrl=float(row["base_hazard_ctrl"]),
        hr=float(row["hr"]),
        allocation=float(row["allocation"]),
        dropout_hazard=float(row["dropout_hazard"]),
        entry_distribution=row["entry_distribution"],
    )
    assert total == int(row["exp_n_total"])


def test_power_logrank_matches_inverse() -> None:
    events = api.required_events_logrank(hr=0.7, alpha=0.05, power=0.8)
    total, exp_n, ctrl_n = api.events_to_n_exponential(
        events_required=events,
        accrual_years=2.0,
        followup_years=1.0,
        base_hazard_ctrl=0.2,
        hr=0.7,
        allocation=0.5,
        dropout_hazard=0.02,
        entry_distribution="uniform",
    )
    power = api.power_logrank_from_n(
        hr=0.7,
        n_exp=exp_n,
        n_ctrl=ctrl_n,
        accrual_years=2.0,
        followup_years=1.0,
        base_hazard_ctrl=0.2,
        dropout_hazard=0.02,
        entry_distribution="uniform",
        alpha=0.05,
        tail="two-sided",
    )
    assert total == exp_n + ctrl_n
    assert pytest.approx(0.8, rel=5e-3) == power
