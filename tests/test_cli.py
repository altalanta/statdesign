from __future__ import annotations

import json
import sys
from io import StringIO

import pytest

from statdesign import cli
from statdesign.core import ncf


def run_cli(args: list[str]) -> tuple[int, str, str]:
    stdout = StringIO()
    stderr = StringIO()
    original_out, original_err = sys.stdout, sys.stderr
    try:
        sys.stdout = stdout
        sys.stderr = stderr
        code = cli.main(args)
    finally:
        sys.stdout = original_out
        sys.stderr = original_err
    return code, stdout.getvalue(), stderr.getvalue()


def test_cli_two_prop() -> None:
    code, out, err = run_cli([
        "n_two_prop",
        "--p1",
        "0.6",
        "--p2",
        "0.5",
        "--alpha",
        "0.05",
        "--power",
        "0.8",
    ])
    assert code == 0
    payload = json.loads(out)
    assert payload == {"n1": 389, "n2": 389}
    assert err == ""


def test_cli_alpha_adjust_bh() -> None:
    code, out, err = run_cli([
        "alpha_adjust",
        "--m",
        "4",
        "--alpha",
        "0.04",
        "--method",
        "bh",
    ])
    assert code == 0
    payload = json.loads(out)
    assert payload == {"thresholds": [0.01, 0.02, 0.03, 0.04]}
    assert err == ""


@pytest.mark.skipif(ncf.has_scipy(), reason="SciPy enabled")
def test_cli_n_mean_requires_scipy() -> None:
    code, out, err = run_cli([
        "n_mean",
        "--mu1",
        "0",
        "--mu2",
        "0.5",
        "--sd",
        "1.0",
    ])
    assert code == 2
    assert out == ""
    assert "SciPy is required" in err
