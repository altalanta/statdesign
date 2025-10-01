from __future__ import annotations

import json
from collections.abc import Iterable
from io import StringIO

import pytest

pytest.importorskip("pytest_regressions")

from statdesign import api, cli


def run_cli(args: Iterable[str], *, stdout: StringIO | None = None) -> tuple[int, str, str]:
    """Execute the CLI with ``args`` capturing stdout/stderr."""

    out_stream = stdout or StringIO()
    err_stream = StringIO()
    from contextlib import redirect_stderr, redirect_stdout

    with redirect_stdout(out_stream), redirect_stderr(err_stream):
        code = cli.main(list(args))
    return code, out_stream.getvalue(), err_stream.getvalue()


@pytest.mark.usefixtures("reset_cli_state")
def test_cli_two_prop_json(data_regression) -> None:
    code, out, err = run_cli(
        [
            "n_two_prop",
            "--p1",
            "0.6",
            "--p2",
            "0.5",
            "--alpha",
            "0.05",
            "--power",
            "0.8",
        ]
    )
    assert code == 0
    assert err == ""
    data_regression.check(json.loads(out))


@pytest.mark.usefixtures("reset_cli_state")
def test_cli_alpha_adjust_table(file_regression) -> None:
    stream = StringIO()
    code, out, err = run_cli(
        [
            "--no-json",
            "--table",
            "alpha_adjust",
            "--m",
            "4",
            "--alpha",
            "0.04",
            "--method",
            "bh",
        ],
        stdout=stream,
    )
    assert code == 0
    assert err == ""
    file_regression.check(out, extension=".txt")


@pytest.mark.usefixtures("reset_cli_state")
def test_cli_invalid_probability() -> None:
    code, out, err = run_cli(
        [
            "n_two_prop",
            "--p1",
            "-0.1",
            "--p2",
            "0.5",
        ]
    )
    assert code == 2
    assert out == ""
    assert "0.0<=x<=1.0" in err


@pytest.mark.usefixtures("reset_cli_state")
def test_cli_mean_fallback_conservative(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("STATDESIGN_AUTO_SCIPY", raising=False)
    args = [
        "n_mean",
        "--mu1",
        "0",
        "--mu2",
        "0.5",
        "--sd",
        "1.0",
        "--test",
        "t",
    ]
    code, out, err = run_cli(args)
    assert code == 0
    assert err == ""
    payload = json.loads(out)
    expected = api.n_mean(mu1=0.0, mu2=0.5, sd=1.0, test="z")
    # t-test should give conservative (larger) sample size than z-test
    assert payload["n1"] >= expected[0]
    assert payload["n2"] >= expected[1]
    # Should be reasonably close (within a few observations)
    assert payload["n1"] - expected[0] <= 3
    assert payload["n2"] - expected[1] <= 3


@pytest.fixture(autouse=True)
def reset_cli_state(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure each test starts without CLI or environment residue."""

    monkeypatch.delenv("STATDESIGN_AUTO_SCIPY", raising=False)
    monkeypatch.setattr(cli, "_SETTINGS", cli.OutputSettings(), raising=False)
