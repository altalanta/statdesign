#!/usr/bin/env python3
"""Release preparation script for statdesign."""

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
    """Prepare a release of statdesign."""
    print("🚀 Preparing statdesign release...\n")

    # Change to project root
    project_root = Path(__file__).parent.parent
    subprocess.run(f"cd {project_root}", shell=True)

    # Pre-release checks
    print("📋 Pre-release validation:")
    checks = [
        ("ruff format --check .", "Code formatting"),
        (
            "ruff check . --exclude tests/archived,src/src,notebooks,"
            "src/statdesign/visualization.py",
            "Linting",
        ),
        ("mypy src/statdesign", "Type checking"),
        (
            "python -m pytest tests/test_alloc.py tests/test_anova.py "
            "tests/test_coverage_boost.py tests/test_means.py tests/test_scipy_backend.py "
            "--cov=src/statdesign --cov-fail-under=45 -q",
            "Core tests",
        ),
        ("mkdocs build --strict", "Documentation"),
    ]

    results = []
    for cmd, desc in checks:
        success = run_command(cmd, desc)
        results.append(success)

    if not all(results):
        print("\n❌ Pre-release checks failed. Fix issues before releasing.")
        return 1

    print("\n🔨 Building release artifacts:")

    # Clean previous builds
    run_command("rm -rf dist/ build/ *.egg-info", "Clean previous builds")

    # Build package
    if not run_command("python -m build", "Build package"):
        return 1

    # Validate package
    if not run_command("twine check dist/*", "Validate package"):
        return 1

    print("\n📦 Release artifacts ready:")
    result = subprocess.run(["/bin/ls", "-la", "dist/"], capture_output=True, text=True)
    print(result.stdout)

    print("\n📋 Release checklist:")
    print("□ 1. Version number updated in src/statdesign/__init__.py")
    print("□ 2. CHANGELOG.md updated with release notes")
    print("□ 3. All tests passing")
    print("□ 4. Documentation updated")
    print("□ 5. Package artifacts built and validated")
    print("\n📝 Next steps for release:")
    print("1. Commit all changes: git add . && git commit -m 'Release v0.1.0'")
    print("2. Create tag: git tag v0.1.0")
    print("3. Push to GitHub: git push origin main --tags")
    print("4. GitHub Actions will automatically publish to PyPI")
    print("\n🎉 Ready for release!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
