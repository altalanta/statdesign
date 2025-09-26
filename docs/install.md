# Installation

The project targets Python 3.9 and newer. Once the first release is published
on PyPI the preferred installation will be:

```bash
pip install statdesign
```

Until then, install from TestPyPI or a local checkout:

```bash
pip install -i https://test.pypi.org/simple/ statdesign
```

Optional extras expose development tooling:

```bash
pip install "statdesign[cli]"     # Typer CLI with rich/table formatting
pip install "statdesign[tests]"   # pytest, hypothesis, coverage helpers
pip install "statdesign[docs]"    # MkDocs Material + mkdocstrings
pip install "statdesign[full]"    # SciPy paths + CLI extras
```

SciPy is intentionally optional. To enable exact noncentral distributions set
`STATDESIGN_AUTO_SCIPY=1` in an environment where `scipy` is installed. Without
SciPy the package falls back to conservative normal approximations.
