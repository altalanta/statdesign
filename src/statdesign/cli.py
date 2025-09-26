"""Command-line interface for the statdesign package."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Any, Callable

try:  # Import Typer lazily so the library install stays lightweight.
    import typer
except ModuleNotFoundError:  # pragma: no cover - exercised only when CLI extra missing
    def main(argv: list[str] | None = None) -> int:
        sys.stderr.write(
            "statdesign CLI requires the optional 'cli' dependencies.\n"
            "Install with `pip install \"statdesign[cli]\"` and retry.\n"
        )
        return 1
else:
    from functools import wraps

    from typer import Exit

    try:  # Optional rich pretty tables for TTY output
        from rich.console import Console
        from rich.table import Table
    except ModuleNotFoundError:  # pragma: no cover - optional styling
        Console = None  # type: ignore
        Table = None  # type: ignore

    try:
        from tabulate import tabulate
    except ModuleNotFoundError:  # pragma: no cover - optional fallback
        tabulate = None  # type: ignore

    from . import api

    app = typer.Typer(
        add_completion=False,
        no_args_is_help=True,
        help=(
            "Deterministic power & sample-size calculations with analytic formulas.\n\n"
            "Examples:\n"
            "  statdesign n_two_prop --p1 0.6 --p2 0.5\n"
            "  statdesign n_mean --mu1 0 --mu2 0.5 --sd 1 --tail two-sided\n"
            "  statdesign alpha_adjust --m 12 --method bonferroni\n"
        ),
    )

    @dataclass
    class OutputSettings:
        json: bool = True
        table: bool = False

        def normalize(self) -> None:
            if not self.json and not self.table:
                self.json = True

    _SETTINGS = OutputSettings()

    def _emit_json(payload: dict[str, Any]) -> None:
        typer.echo(json.dumps(payload, sort_keys=True, separators=(",", ":")))

    def _stdout_isatty() -> bool:
        isatty = getattr(sys.stdout, "isatty", None)
        if callable(isatty):
            try:
                return bool(isatty())
            except Exception:  # pragma: no cover - defensive fallback
                return False
        return False

    def _format_value(value: Any) -> str:
        if isinstance(value, float):
            return f"{value:.6g}"
        if isinstance(value, (list, tuple)):
            return ", ".join(_format_value(item) for item in value)
        return str(value)

    def _emit_table(payload: dict[str, Any]) -> None:
        if not payload:
            return
        if Console is not None and Table is not None and _stdout_isatty():
            console = Console()
            table = Table(show_edge=True)
            table.add_column("key", justify="right")
            table.add_column("value", justify="left")
            for key, value in payload.items():
                table.add_row(str(key), _format_value(value))
            console.print(table)
            return
        if tabulate is not None:
            headers = ["key", "value"]
            rows = [(str(k), _format_value(v)) for k, v in payload.items()]
            typer.echo(tabulate(rows, headers=headers, tablefmt="github"))
            return
        for key, value in payload.items():
            typer.echo(f"{key}: {_format_value(value)}")

    def _emit(payload: dict[str, Any]) -> None:
        _SETTINGS.normalize()
        if _SETTINGS.json:
            _emit_json(payload)
        if _SETTINGS.table:
            _emit_table(payload)

    def _fail(message: str, code: int = 2) -> None:
        typer.echo(message, err=True)
        raise Exit(code)

    def _parse_allocation(allocation: str | None) -> list[float] | None:
        if allocation is None:
            return None
        parts = [part.strip() for part in allocation.split(",") if part.strip()]
        if not parts:
            raise ValueError("allocation must contain at least one positive weight")
        weights: list[float] = []
        for item in parts:
            try:
                value = float(item)
            except ValueError as exc:  # pragma: no cover
                raise ValueError(f"invalid allocation weight: {item}") from exc
            if value <= 0:
                raise ValueError("allocation weights must be positive")
            weights.append(value)
        return weights

    _ALLOWED_TAILS = ("two-sided", "greater", "less")
    _ALLOWED_TESTS = ("z", "t")
    _ALLOWED_NI_TYPES = ("noninferiority", "equivalence")
    _ALLOWED_METHODS = ("bonferroni", "bh")

    def _normalize_choice(value: str, allowed: tuple[str, ...], name: str) -> str:
        normalized = value.replace("_", "-").lower()
        if normalized not in allowed:
            raise ValueError(f"{name} must be one of {', '.join(allowed)}")
        return normalized

    def _normalize_optional(value: str | None, allowed: tuple[str, ...], name: str) -> str | None:
        if value is None:
            return None
        return _normalize_choice(value, allowed, name)

    @app.callback()
    def _configure(
        json_output: bool = typer.Option(
            True,
            "--json/--no-json",
            help="Emit JSON payloads (default true).",
            show_default=True,
        ),
        table_output: bool = typer.Option(
            False,
            "--table/--no-table",
            help="Emit a table rendering of the results.",
        ),
    ) -> None:
        """Configure global output preferences."""

        global _SETTINGS
        settings = OutputSettings(json=json_output, table=table_output)
        settings.normalize()
        _SETTINGS = settings

    def _handle_errors(func: Callable[..., dict[str, Any]]) -> Callable[..., None]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> None:
            try:
                payload = func(*args, **kwargs)
            except ValueError as exc:
                _fail(str(exc))
            except (NotImplementedError, RuntimeError) as exc:
                _fail(str(exc), code=3)
            else:
                _emit(payload)

        return wrapper

    @app.command(name="n_two_prop")
    @_handle_errors
    def n_two_prop(
        p1: float = typer.Option(..., min=0.0, max=1.0, help="Proportion for group 1."),
        p2: float = typer.Option(..., min=0.0, max=1.0, help="Proportion for group 2."),
        alpha: float = typer.Option(0.05, min=0.0, max=1.0, help="Type I error rate."),
        power: float = typer.Option(0.80, min=0.0, max=1.0, help="Target power."),
        ratio: float = typer.Option(1.0, min=0.0, help="Allocation ratio n2/n1."),
        test: str = typer.Option("z", help="Test statistic ('z' or 't')."),
        tail: str = typer.Option("two-sided", help="Alternative hypothesis tail."),
        ni_margin: float | None = typer.Option(None, help="Non-inferiority or equivalence margin."),
        ni_type: str | None = typer.Option(None, help="Margin type."),
        exact: bool = typer.Option(False, help="Toggle exact small-sample test."),
    ) -> dict[str, Any]:
        """Sample size for two independent proportions."""

        from . import api  # Import api types locally
        test_norm = _normalize_choice(test, _ALLOWED_TESTS, "test")
        tail_norm = _normalize_choice(tail, _ALLOWED_TAILS, "tail")
        ni_type_norm = _normalize_optional(ni_type, _ALLOWED_NI_TYPES, "ni_type")
        n1, n2 = api.n_two_prop(
            p1=p1,
            p2=p2,
            alpha=alpha,
            power=power,
            ratio=ratio,
            test=test_norm,  # type: ignore
            tail=tail_norm,  # type: ignore
            ni_margin=ni_margin,
            ni_type=ni_type_norm,  # type: ignore
            exact=exact,
        )
        return {"n1": n1, "n2": n2}

    @app.command(name="n_one_sample_prop")
    @_handle_errors
    def n_one_sample_prop(
        p: float = typer.Option(..., min=0.0, max=1.0, help="Observed proportion."),
        p0: float = typer.Option(..., min=0.0, max=1.0, help="Null hypothesis proportion."),
        alpha: float = typer.Option(0.05, min=0.0, max=1.0),
        power: float = typer.Option(0.80, min=0.0, max=1.0),
        tail: str = typer.Option("two-sided", help="Alternative hypothesis tail."),
        exact: bool = typer.Option(False, help="Use exact binomial enumeration."),
        ni_margin: float | None = typer.Option(None, help="Non-inferiority/equivalence margin."),
        ni_type: str | None = typer.Option(None, help="Margin type."),
    ) -> dict[str, Any]:
        """Sample size for a one-sample proportion test."""

        tail_norm = _normalize_choice(tail, _ALLOWED_TAILS, "tail")
        ni_type_norm = _normalize_optional(ni_type, _ALLOWED_NI_TYPES, "ni_type")
        n = api.n_one_sample_prop(
            p=p,
            p0=p0,
            alpha=alpha,
            power=power,
            tail=tail_norm,
            exact=exact,
            ni_margin=ni_margin,
            ni_type=ni_type_norm,
        )
        return {"n": n}

    @app.command(name="n_mean")
    @_handle_errors
    def n_mean(
        mu1: float = typer.Option(..., help="Mean for arm 1."),
        mu2: float = typer.Option(..., help="Mean for arm 2."),
        sd: float = typer.Option(..., min=0.0, help="Common standard deviation."),
        alpha: float = typer.Option(0.05, min=0.0, max=1.0),
        power: float = typer.Option(0.80, min=0.0, max=1.0),
        ratio: float = typer.Option(1.0, min=0.0, help="Allocation ratio n2/n1."),
        test: str = typer.Option("t", help="Test statistic ('z' or 't')."),
        tail: str = typer.Option("two-sided", help="Alternative hypothesis tail."),
        ni_margin: float | None = typer.Option(None, help="Non-inferiority/equivalence margin."),
        ni_type: str | None = typer.Option(None, help="Margin type."),
    ) -> dict[str, Any]:
        """Sample size for two independent means with shared variance."""

        test_norm = _normalize_choice(test, _ALLOWED_TESTS, "test")
        tail_norm = _normalize_choice(tail, _ALLOWED_TAILS, "tail")
        ni_type_norm = _normalize_optional(ni_type, _ALLOWED_NI_TYPES, "ni_type")
        n1, n2 = api.n_mean(
            mu1=mu1,
            mu2=mu2,
            sd=sd,
            alpha=alpha,
            power=power,
            ratio=ratio,
            test=test_norm,
            tail=tail_norm,
            ni_margin=ni_margin,
            ni_type=ni_type_norm,
        )
        return {"n1": n1, "n2": n2}

    @app.command(name="n_one_sample_mean")
    @_handle_errors
    def n_one_sample_mean(
        delta: float = typer.Option(..., help="Difference from null mean."),
        sd: float = typer.Option(..., min=0.0, help="Standard deviation."),
        alpha: float = typer.Option(0.05, min=0.0, max=1.0),
        power: float = typer.Option(0.80, min=0.0, max=1.0),
        tail: str = typer.Option("two-sided", help="Alternative hypothesis tail."),
        test: str = typer.Option("t", help="Test statistic ('z' or 't')."),
        ni_margin: float | None = typer.Option(None, help="Non-inferiority/equivalence margin."),
        ni_type: str | None = typer.Option(None, help="Margin type."),
    ) -> dict[str, Any]:
        """Sample size for a one-sample mean test."""

        tail_norm = _normalize_choice(tail, _ALLOWED_TAILS, "tail")
        test_norm = _normalize_choice(test, _ALLOWED_TESTS, "test")
        ni_type_norm = _normalize_optional(ni_type, _ALLOWED_NI_TYPES, "ni_type")
        n = api.n_one_sample_mean(
            delta=delta,
            sd=sd,
            alpha=alpha,
            power=power,
            tail=tail_norm,
            test=test_norm,
            ni_margin=ni_margin,
            ni_type=ni_type_norm,
        )
        return {"n": n}

    @app.command(name="n_paired")
    @_handle_errors
    def n_paired(
        delta: float = typer.Option(..., help="Mean paired difference."),
        sd_diff: float = typer.Option(..., min=0.0, help="SD of paired differences."),
        alpha: float = typer.Option(0.05, min=0.0, max=1.0),
        power: float = typer.Option(0.80, min=0.0, max=1.0),
        tail: str = typer.Option("two-sided", help="Alternative hypothesis tail."),
        ni_margin: float | None = typer.Option(None, help="Non-inferiority/equivalence margin."),
        ni_type: str | None = typer.Option(None, help="Margin type."),
    ) -> dict[str, Any]:
        """Sample size for paired mean comparisons."""

        tail_norm = _normalize_choice(tail, _ALLOWED_TAILS, "tail")
        ni_type_norm = _normalize_optional(ni_type, _ALLOWED_NI_TYPES, "ni_type")
        n = api.n_paired(
            delta=delta,
            sd_diff=sd_diff,
            alpha=alpha,
            power=power,
            tail=tail_norm,
            ni_margin=ni_margin,
            ni_type=ni_type_norm,
        )
        return {"n": n}

    @app.command(name="n_anova")
    @_handle_errors
    def n_anova(
        k_groups: int = typer.Option(..., min=2, help="Number of groups."),
        effect_f: float = typer.Option(..., min=0.0, help="Cohen's f effect size."),
        alpha: float = typer.Option(0.05, min=0.0, max=1.0),
        power: float = typer.Option(0.80, min=0.0, max=1.0),
        allocation: str | None = typer.Option(
            None,
            help="Comma separated allocation weights (defaults to equal).",
        ),
    ) -> dict[str, Any]:
        """Total sample size for fixed-effects one-way ANOVA."""

        weights = _parse_allocation(allocation)
        n_total = api.n_anova(
            k_groups=k_groups,
            effect_f=effect_f,
            alpha=alpha,
            power=power,
            allocation=weights,
        )
        payload: dict[str, Any] = {"n_total": n_total}
        if weights is not None:
            payload["allocation"] = weights
        return payload

    @app.command(name="alpha_adjust")
    @_handle_errors
    def alpha_adjust(
        m: int = typer.Option(..., min=1, help="Number of hypotheses."),
        alpha: float = typer.Option(0.05, min=0.0, max=1.0),
        method: str = typer.Option(
            "bonferroni",
            help="Adjustment method ('bonferroni' or 'bh').",
        ),
    ) -> dict[str, Any]:
        """Compute family-wise error rate adjustments."""

        method_norm = _normalize_choice(method, _ALLOWED_METHODS, "method")
        if method_norm == "bonferroni":
            value = api.alpha_adjust(m=m, alpha=alpha, method="bonferroni")
            return {"alpha": value}
        thresholds = api.bh_thresholds(m=m, alpha=alpha)
        return {"thresholds": thresholds}

    @app.command(name="bh_thresholds")
    @_handle_errors
    def bh_thresholds(
        m: int = typer.Option(..., min=1, help="Number of hypotheses."),
        alpha: float = typer.Option(0.05, min=0.0, max=1.0),
    ) -> dict[str, Any]:
        """Benjamini–Hochberg critical values."""

        thresholds = api.bh_thresholds(m=m, alpha=alpha)
        return {"thresholds": thresholds}

    def main(argv: list[str] | None = None) -> int:
        try:
            app(prog_name="statdesign", args=argv)
        except SystemExit as exc:  # click raises SystemExit with exit code
            code = exc.code or 0
            return int(code) if isinstance(code, int) else 1
        except KeyboardInterrupt:  # pragma: no cover - CLI interaction
            typer.echo("Aborted by user", err=True)
            return 130
        return 0

