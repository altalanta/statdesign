"""Generate markdown parity tables comparing statdesign output to reference values."""

from __future__ import annotations

import csv
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from statdesign import api

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "tests" / "golden"
PARITY = ROOT / "docs" / "parity"


@dataclass
class TableSpec:
    path: Path
    rows: Sequence[dict[str, str]]
    headers: Sequence[str]
    build_row: Callable[[dict[str, str]], Sequence[str]]


def _fmt_float(value: float) -> str:
    return f"{value:.6g}"


def _read_csv(name: str) -> list[dict[str, str]]:
    with (GOLDEN / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


def _means_row(row: dict[str, str]) -> Sequence[str]:
    mu1 = float(row["mu1"])
    mu2 = float(row["mu2"])
    sd = float(row["sd"])
    ratio = float(row["ratio"])
    result = api.n_mean(
        mu1=mu1,
        mu2=mu2,
        sd=sd,
        ratio=ratio,
        alpha=float(row["alpha"]),
        power=float(row["power"]),
        test=row["test"] or "t",
        tail=row["tail"],
    )
    expected = (int(row["exp_n1"]), int(row["exp_n2"]))
    return (
        f"μ1={mu1}, μ2={mu2}, σ={sd}, test={row['test'] or 't'}",
        str(expected[0]),
        str(result[0]),
        str(expected[1]),
        str(result[1]),
    )


def _one_sample_mean_row(row: dict[str, str]) -> Sequence[str]:
    delta = float(row["delta"])
    sd = float(row["sd"])
    result = api.n_one_sample_mean(
        delta=delta,
        sd=sd,
        alpha=float(row["alpha"]),
        power=float(row["power"]),
        test=row.get("test") or "t",
        tail=row["tail"],
    )
    expected = int(row["exp_n"])
    return (
        f"Δ={delta}, σ={sd}, test={row.get('test') or 't'}",
        str(expected),
        str(result),
    )


def _paired_row(row: dict[str, str]) -> Sequence[str]:
    delta = float(row["delta"])
    sd_diff = float(row["sd_diff"])
    result = api.n_paired(
        delta=delta,
        sd_diff=sd_diff,
        alpha=float(row["alpha"]),
        power=float(row["power"]),
        tail=row["tail"],
    )
    expected = int(row["exp_n"])
    return (
        f"Δ={delta}, σ_d={sd_diff}",
        str(expected),
        str(result),
    )


def _two_prop_row(row: dict[str, str]) -> Sequence[str]:
    p1 = float(row["p1"])
    p2 = float(row["p2"])
    result = api.n_two_prop(
        p1=p1,
        p2=p2,
        alpha=float(row["alpha"]),
        power=float(row["power"]),
        ratio=float(row.get("ratio") or 1.0),
        test=row.get("test") or "z",
        tail=row["tail"],
        exact=row.get("exact", "false").lower() == "true",
    )
    expected = (int(row["exp_n1"]), int(row["exp_n2"]))
    return (
        f"p1={p1}, p2={p2}, exact={row.get('exact', 'false')}",
        str(expected[0]),
        str(result[0]),
        str(expected[1]),
        str(result[1]),
    )


def _anova_row(row: dict[str, str]) -> Sequence[str]:
    allocation = row.get("allocation")
    weights = [float(part) for part in allocation.split(",")] if allocation else None
    result = api.n_anova(
        k_groups=int(row["k_groups"]),
        effect_f=float(row["effect_f"]),
        alpha=float(row["alpha"]),
        power=float(row["power"]),
        allocation=weights,
    )
    expected = int(row["exp_n"])
    alloc_desc = f", weights={allocation}" if allocation else ""
    return (
        f"k={row['k_groups']}, f={row['effect_f']}{alloc_desc}",
        str(expected),
        str(result),
    )


def _survival_row(row: dict[str, str]) -> Sequence[str]:
    result = api.required_events_logrank(
        hr=float(row["hr"]),
        alpha=float(row["alpha"]),
        power=float(row["power"]),
        allocation=float(row["allocation"]),
        tail=row["tail"],
    )
    expected = float(row["exp_events"])
    return (
        f"HR={row['hr']}, allocation={row['allocation']}",
        _fmt_float(expected),
        _fmt_float(result),
    )


TABLES: Iterable[TableSpec] = [
    TableSpec(
        path=PARITY / "means.md",
        rows=_read_csv("means_two_sample_golden.csv"),
        headers=["Scenario", "Reference n1", "statdesign n1", "Reference n2", "statdesign n2"],
        build_row=_means_row,
    ),
    TableSpec(
        path=PARITY / "one_sample_means.md",
        rows=_read_csv("one_sample_mean_golden.csv"),
        headers=["Scenario", "Reference n", "statdesign n"],
        build_row=_one_sample_mean_row,
    ),
    TableSpec(
        path=PARITY / "paired_means.md",
        rows=_read_csv("paired_mean_golden.csv"),
        headers=["Scenario", "Reference n", "statdesign n"],
        build_row=_paired_row,
    ),
    TableSpec(
        path=PARITY / "two_proportions.md",
        rows=_read_csv("two_prop_normal_golden.csv"),
        headers=["Scenario", "Reference n1", "statdesign n1", "Reference n2", "statdesign n2"],
        build_row=_two_prop_row,
    ),
    TableSpec(
        path=PARITY / "anova.md",
        rows=_read_csv("anova_golden.csv"),
        headers=["Scenario", "Reference n", "statdesign n"],
        build_row=_anova_row,
    ),
    TableSpec(
        path=PARITY / "survival.md",
        rows=_read_csv("survival_events_golden.csv"),
        headers=["Scenario", "Reference events", "statdesign events"],
        build_row=_survival_row,
    ),
]


def _write_markdown(spec: TableSpec) -> None:
    spec.path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Parity Table", ""]
    header = " | ".join(spec.headers)
    separator = " | ".join(["---"] * len(spec.headers))
    lines.append(header)
    lines.append(separator)
    for row in spec.rows:
        values = spec.build_row(row)
        lines.append(" | ".join(values))
    spec.path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    for table in TABLES:
        _write_markdown(table)


if __name__ == "__main__":
    main()
