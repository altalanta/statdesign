"""Command-line interface mirroring the statdesign API."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Optional

from . import api


def _parse_allocation(allocation: Optional[str]) -> Optional[list[float]]:
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


def _print_json(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, sort_keys=True))
    sys.stdout.write("\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deterministic power & sample-size calculations")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # n_two_prop
    parser_two_prop = subparsers.add_parser("n_two_prop", help="Two-sample proportion sample sizes")
    parser_two_prop.add_argument("--p1", type=float, required=True)
    parser_two_prop.add_argument("--p2", type=float, required=True)
    parser_two_prop.add_argument("--alpha", type=float, default=0.05)
    parser_two_prop.add_argument("--power", type=float, default=0.80)
    parser_two_prop.add_argument("--ratio", type=float, default=1.0)
    parser_two_prop.add_argument("--test", choices=["z", "t"], default="z")
    parser_two_prop.add_argument(
        "--tail",
        choices=["two-sided", "greater", "less"],
        default="two-sided",
    )
    parser_two_prop.add_argument("--ni-margin", type=float, dest="ni_margin")
    parser_two_prop.add_argument(
        "--ni-type", choices=["noninferiority", "equivalence"], dest="ni_type"
    )
    parser_two_prop.add_argument("--exact", action="store_true")

    # n_mean
    parser_mean = subparsers.add_parser("n_mean", help="Two-sample mean sample sizes")
    parser_mean.add_argument("--mu1", type=float, required=True)
    parser_mean.add_argument("--mu2", type=float, required=True)
    parser_mean.add_argument("--sd", type=float, required=True)
    parser_mean.add_argument("--alpha", type=float, default=0.05)
    parser_mean.add_argument("--power", type=float, default=0.80)
    parser_mean.add_argument("--ratio", type=float, default=1.0)
    parser_mean.add_argument("--test", choices=["z", "t"], default="t")
    parser_mean.add_argument(
        "--tail",
        choices=["two-sided", "greater", "less"],
        default="two-sided",
    )
    parser_mean.add_argument("--ni-margin", type=float, dest="ni_margin")
    parser_mean.add_argument(
        "--ni-type", choices=["noninferiority", "equivalence"], dest="ni_type"
    )

    # n_paired
    parser_paired = subparsers.add_parser("n_paired", help="Paired means sample size")
    parser_paired.add_argument("--delta", type=float, required=True)
    parser_paired.add_argument("--sd-diff", type=float, required=True, dest="sd_diff")
    parser_paired.add_argument("--alpha", type=float, default=0.05)
    parser_paired.add_argument("--power", type=float, default=0.80)
    parser_paired.add_argument(
        "--tail",
        choices=["two-sided", "greater", "less"],
        default="two-sided",
    )
    parser_paired.add_argument("--ni-margin", type=float, dest="ni_margin")
    parser_paired.add_argument(
        "--ni-type", choices=["noninferiority", "equivalence"], dest="ni_type"
    )

    # n_one_sample_mean
    parser_one_mean = subparsers.add_parser(
        "n_one_sample_mean", help="One-sample mean sample size"
    )
    parser_one_mean.add_argument("--delta", type=float, required=True)
    parser_one_mean.add_argument("--sd", type=float, required=True)
    parser_one_mean.add_argument("--alpha", type=float, default=0.05)
    parser_one_mean.add_argument("--power", type=float, default=0.80)
    parser_one_mean.add_argument(
        "--tail",
        choices=["two-sided", "greater", "less"],
        default="two-sided",
    )
    parser_one_mean.add_argument("--test", choices=["z", "t"], default="t")
    parser_one_mean.add_argument("--ni-margin", type=float, dest="ni_margin")
    parser_one_mean.add_argument(
        "--ni-type", choices=["noninferiority", "equivalence"], dest="ni_type"
    )

    # n_one_sample_prop
    parser_one_prop = subparsers.add_parser(
        "n_one_sample_prop", help="One-sample proportion sample size"
    )
    parser_one_prop.add_argument("--p", type=float, required=True)
    parser_one_prop.add_argument("--p0", type=float, required=True)
    parser_one_prop.add_argument("--alpha", type=float, default=0.05)
    parser_one_prop.add_argument("--power", type=float, default=0.80)
    parser_one_prop.add_argument(
        "--tail",
        choices=["two-sided", "greater", "less"],
        default="two-sided",
    )
    parser_one_prop.add_argument("--exact", action="store_true")
    parser_one_prop.add_argument("--ni-margin", type=float, dest="ni_margin")
    parser_one_prop.add_argument(
        "--ni-type", choices=["noninferiority", "equivalence"], dest="ni_type"
    )

    # n_anova
    parser_anova = subparsers.add_parser("n_anova", help="One-way ANOVA sample size")
    parser_anova.add_argument("--k-groups", type=int, required=True, dest="k_groups")
    parser_anova.add_argument("--effect-f", type=float, required=True, dest="effect_f")
    parser_anova.add_argument("--alpha", type=float, default=0.05)
    parser_anova.add_argument("--power", type=float, default=0.80)
    parser_anova.add_argument("--allocation", type=str)

    # alpha_adjust
    parser_alpha = subparsers.add_parser("alpha_adjust", help="Multiple-testing alpha adjustment")
    parser_alpha.add_argument("--m", type=int, required=True)
    parser_alpha.add_argument("--alpha", type=float, default=0.05)
    parser_alpha.add_argument("--method", choices=["bonferroni", "bh"], default="bonferroni")

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "n_two_prop":
            result = api.n_two_prop(
                p1=args.p1,
                p2=args.p2,
                alpha=args.alpha,
                power=args.power,
                ratio=args.ratio,
                test=args.test,
                tail=args.tail,
                ni_margin=args.ni_margin,
                ni_type=args.ni_type,
                exact=args.exact,
            )
            _print_json({"n1": result[0], "n2": result[1]})
            return 0
        if args.command == "n_mean":
            result = api.n_mean(
                mu1=args.mu1,
                mu2=args.mu2,
                sd=args.sd,
                alpha=args.alpha,
                power=args.power,
                ratio=args.ratio,
                test=args.test,
                tail=args.tail,
                ni_margin=args.ni_margin,
                ni_type=args.ni_type,
            )
            _print_json({"n1": result[0], "n2": result[1]})
            return 0
        if args.command == "n_paired":
            n = api.n_paired(
                delta=args.delta,
                sd_diff=args.sd_diff,
                alpha=args.alpha,
                power=args.power,
                tail=args.tail,
                ni_margin=args.ni_margin,
                ni_type=args.ni_type,
            )
            _print_json({"n": n})
            return 0
        if args.command == "n_one_sample_mean":
            n = api.n_one_sample_mean(
                delta=args.delta,
                sd=args.sd,
                alpha=args.alpha,
                power=args.power,
                tail=args.tail,
                test=args.test,
                ni_margin=args.ni_margin,
                ni_type=args.ni_type,
            )
            _print_json({"n": n})
            return 0
        if args.command == "n_one_sample_prop":
            n = api.n_one_sample_prop(
                p=args.p,
                p0=args.p0,
                alpha=args.alpha,
                power=args.power,
                tail=args.tail,
                exact=args.exact,
                ni_margin=args.ni_margin,
                ni_type=args.ni_type,
            )
            _print_json({"n": n})
            return 0
        if args.command == "n_anova":
            allocation = _parse_allocation(args.allocation)
            n_total = api.n_anova(
                k_groups=args.k_groups,
                effect_f=args.effect_f,
                alpha=args.alpha,
                power=args.power,
                allocation=allocation,
            )
            payload: dict[str, object] = {"n_total": n_total}
            if allocation is not None:
                payload["allocation"] = allocation
            _print_json(payload)
            return 0
        if args.command == "alpha_adjust":
            if args.method == "bonferroni":
                value = api.alpha_adjust(m=args.m, alpha=args.alpha, method="bonferroni")
                _print_json({"alpha": value})
            else:
                thresholds = api.bh_thresholds(m=args.m, alpha=args.alpha)
                _print_json({"thresholds": thresholds})
            return 0
    except ValueError as exc:
        parser.error(str(exc))
    except (NotImplementedError, RuntimeError) as exc:
        sys.stderr.write(f"{exc}\n")
        return 2

    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
