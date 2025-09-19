import subprocess
import sys


def test_cli_n_two_prop():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "statdesign.cli",
            "n-two-prop",
            "--p1",
            "0.1",
            "--p2",
            "0.14",
            "--alpha",
            "0.05",
            "--power",
            "0.8",
            "--ratio",
            "1.0",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Group" in result.stdout
