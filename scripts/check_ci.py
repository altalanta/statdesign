#!/usr/bin/env python3
"""Script to validate CI/CD setup locally before pushing."""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, description: str) -> bool:
    """Run a command and return True if successful."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description}")
            return True
        else:
            print(f"❌ {description}")
            print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description}")
        print(f"   Exception: {e}")
        return False


def main():
    """Run all CI checks locally."""
    print("🚀 Running CI/CD validation checks...\n")

    # Change to project root
    project_root = Path(__file__).parent.parent
    subprocess.run(f"cd {project_root}", shell=True)

    checks = [
        ("ruff format --check .", "Code formatting check"),
        ("ruff check .", "Linting check"),
        ("mypy src/statdesign", "Type checking"),
        (
            "python -m pytest tests/test_alloc.py tests/test_anova.py "
            "tests/test_coverage_boost.py tests/test_means.py tests/test_scipy_backend.py "
            "--cov=src/statdesign --cov-fail-under=45 -q",
            "Test suite with coverage",
        ),
        ("mkdocs build --strict", "Documentation build"),
        ("python -m build", "Package build"),
        ("twine check dist/*", "Package validation"),
    ]

    results = []
    for cmd, desc in checks:
        success = run_command(cmd, desc)
        results.append(success)

    print("\n📋 Summary:")
    print(f"✅ Passed: {sum(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}")

    if all(results):
        print("\n🎉 All checks passed! Ready for CI/CD.")
        return 0
    else:
        print("\n⚠️  Some checks failed. Fix issues before pushing.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
