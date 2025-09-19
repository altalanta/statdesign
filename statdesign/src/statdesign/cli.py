"""Typer CLI for statdesign."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from .power import (
    n_anova_oneway,
    n_one_mean,
    n_one_prop,
    n_paired_t,
    n_two_mean,
    n_two_prop,
    power_one_mean,
    power_one_prop,
    power_paired_t,
    power_two_mean,
    power_two_prop,
)

app = typer.Typer(help="Power & sample-size utilities")
console = Console()


@app.command("power-one-prop")
def cmd_power_one_prop(p: float, p0: float, n: int, alpha: float = 0.05, two_sided: bool = True) -> None:
    value = power_one_prop(p=p, p0=p0, n=n, alpha=alpha, two_sided=two_sided)
    console.print(f"[bold]Power:[/] {value:.3f}")


@app.command("n-one-prop")
def cmd_n_one_prop(p: float, p0: float, alpha: float = 0.05, power: float = 0.8, two_sided: bool = True) -> None:
    n = n_one_prop(p=p, p0=p0, alpha=alpha, power=power, two_sided=two_sided)
    console.print(f"[bold]n:[/] {n}")


@app.command("power-two-prop")
def cmd_power_two_prop(
    p1: float,
    p2: float,
    n1: int,
    n2: int = typer.Option(None, help="Sample size for group 2"),
    alpha: float = 0.05,
    two_sided: bool = True,
) -> None:
    value = power_two_prop(p1=p1, p2=p2, n1=n1, n2=n2, alpha=alpha, two_sided=two_sided)
    console.print(f"[bold]Power:[/] {value:.3f}")


@app.command("n-two-prop")
def cmd_n_two_prop(
    p1: float,
    p2: float,
    alpha: float = 0.05,
    power: float = 0.8,
    ratio: float = 1.0,
    two_sided: bool = True,
) -> None:
    n1, n2 = n_two_prop(p1=p1, p2=p2, alpha=alpha, power=power, ratio=ratio, two_sided=two_sided)
    table = Table(title="Sample size: two proportions")
    table.add_column("Group")
    table.add_column("n", justify="right")
    table.add_row("Group 1", str(n1))
    table.add_row("Group 2", str(n2))
    console.print(table)


@app.command("n-one-mean")
def cmd_n_one_mean(
    mu0: float,
    mu1: float,
    sd: float,
    alpha: float = 0.05,
    power: float = 0.8,
    two_sided: bool = True,
) -> None:
    n = n_one_mean(mu0=mu0, mu1=mu1, sd=sd, alpha=alpha, power=power, two_sided=two_sided)
    console.print(f"[bold]n:[/] {n}")


@app.command("power-one-mean")
def cmd_power_one_mean(
    mu0: float,
    mu1: float,
    sd: float,
    n: int,
    alpha: float = 0.05,
    two_sided: bool = True,
) -> None:
    value = power_one_mean(mu0=mu0, mu1=mu1, sd=sd, n=n, alpha=alpha, two_sided=two_sided)
    console.print(f"[bold]Power:[/] {value:.3f}")


@app.command("n-two-mean")
def cmd_n_two_mean(
    mu1: float,
    mu2: float,
    sd1: float,
    sd2: float,
    alpha: float = 0.05,
    power: float = 0.8,
    ratio: float = 1.0,
    two_sided: bool = True,
) -> None:
    n1, n2 = n_two_mean(mu1=mu1, mu2=mu2, sd1=sd1, sd2=sd2, alpha=alpha, power=power, ratio=ratio, two_sided=two_sided)
    console.print(f"n1={n1}, n2={n2}")


@app.command("power-two-mean")
def cmd_power_two_mean(
    mu1: float,
    mu2: float,
    sd1: float,
    sd2: float,
    n1: int,
    n2: int = typer.Option(None, help="Sample size for group 2"),
    alpha: float = 0.05,
    pooled: bool = True,
    two_sided: bool = True,
) -> None:
    value = power_two_mean(
        mu1=mu1,
        mu2=mu2,
        sd1=sd1,
        sd2=sd2,
        n1=n1,
        n2=n2,
        alpha=alpha,
        pooled=pooled,
        two_sided=two_sided,
    )
    console.print(f"[bold]Power:[/] {value:.3f}")


@app.command("n-paired-t")
def cmd_n_paired(mu_diff: float, sd_diff: float, alpha: float = 0.05, power: float = 0.8, two_sided: bool = True) -> None:
    n = n_paired_t(mu_diff=mu_diff, sd_diff=sd_diff, alpha=alpha, power=power, two_sided=two_sided)
    console.print(f"[bold]n:[/] {n}")


@app.command("n-anova")
def cmd_n_anova(k: int, effect_f: float, alpha: float = 0.05, power: float = 0.8) -> None:
    n = n_anova_oneway(k=k, effect_f=effect_f, alpha=alpha, power=power)
    console.print(f"[bold]n per group:[/] {n}")


if __name__ == "__main__":  # pragma: no cover
    app()
