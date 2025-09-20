from __future__ import annotations

import csv
from pathlib import Path

import pytest

PARITY_DIR = Path(__file__).resolve().parents[1] / "docs" / "parity"


def _parity_files() -> list[Path]:
    if not PARITY_DIR.exists():
        return []
    return sorted(PARITY_DIR.glob("*.csv"))


@pytest.mark.slow
@pytest.mark.parametrize("path", _parity_files())
def test_parity_tables(path: Path) -> None:
    if path is None:
        pytest.skip("no parity data available")
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    if not rows:
        pytest.skip(f"empty parity table: {path.name}")
    for row in rows:
        ref = float(row["tool_reference"])
        ours = float(row["statdesign"])
        assert pytest.approx(ref, rel=1e-3) == ours
