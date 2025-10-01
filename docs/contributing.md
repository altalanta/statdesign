# Contributing to statdesign

Thank you for your interest in contributing to statdesign! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git

### Installation

1. Fork and clone the repository:
```bash
git clone https://github.com/yourusername/statdesign.git
cd statdesign
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode with all dependencies:
```bash
pip install -e ".[dev,scipy]"
```

4. Verify installation:
```bash
statdesign --version
python -m pytest tests/ -v
```

## Development Workflow

### Code Style

We use several tools to maintain code quality:

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type checking
mypy src/statdesign

# Run all checks
python -m pytest tests/ --cov=src/statdesign --cov-report=term-missing
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/statdesign --cov-report=html

# Run specific test categories
pytest tests/test_core.py -v
pytest tests/test_benchmarks.py -k benchmark
pytest tests/test_edge_cases.py -k hypothesis

# Run parity tests against R
pytest tests/test_parity.py -v
```

### Documentation

Build and serve documentation locally:

```bash
mkdocs serve
```

View at http://localhost:8000

## Contributing Guidelines

### Issues

Before creating an issue:

1. Search existing issues to avoid duplicates
2. Use issue templates when available
3. Provide minimal reproducible examples for bugs
4. Include version information (`statdesign --version`)

### Pull Requests

1. **Fork and branch**: Create a feature branch from `main`
2. **Write tests**: All new functionality must have tests
3. **Update docs**: Add or update documentation as needed
4. **Follow conventions**: Use existing code style and patterns
5. **Test thoroughly**: Ensure all tests pass and coverage stays ≥95%

#### PR Checklist

- [ ] Tests added/updated and passing
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated for user-facing changes
- [ ] Type hints added for new functions
- [ ] Docstrings follow Google style
- [ ] No breaking changes without discussion

### Code Organization

```
src/statdesign/
├── __init__.py          # Public API exports
├── core/                # Core statistical functions
│   ├── proportions.py   # Proportion-based tests
│   ├── means.py         # Mean-based tests
│   ├── anova.py         # ANOVA calculations
│   └── ncf.py           # Noncentral distributions
├── corrections.py       # Multiple testing corrections
├── cli.py              # Command-line interface
└── _scipy_backend.py   # Optional SciPy integration
```

### Function Design Principles

1. **Deterministic**: Same inputs always produce same outputs
2. **Validated**: Comprehensive input validation with clear error messages
3. **Documented**: Google-style docstrings with examples
4. **Tested**: Unit tests, edge cases, and parity tests against R
5. **Backwards compatible**: Avoid breaking API changes

### Statistical Accuracy

All statistical functions should:

1. **Match R's pwr package** where applicable (see parity tests)
2. **Handle edge cases** gracefully (extreme effect sizes, boundary values)
3. **Provide conservative estimates** when using approximations
4. **Document assumptions** clearly in docstrings

### Testing Strategy

We use multiple testing approaches:

1. **Unit tests**: Basic functionality and expected results
2. **Parity tests**: Comparison against R's pwr package results
3. **Edge case tests**: Boundary conditions and error handling  
4. **Property-based tests**: Using Hypothesis for broader coverage
5. **Benchmark tests**: Performance monitoring with pytest-benchmark

## Release Process

1. **Update version** in `src/statdesign/__init__.py`
2. **Update CHANGELOG.md** with new features/fixes
3. **Tag release**: `git tag v0.2.0 && git push --tags`
4. **GitHub Actions** handles PyPI publication automatically

## Getting Help

- **Discussions**: Use GitHub Discussions for questions
- **Issues**: Report bugs or request features
- **Documentation**: Check the docs at https://altalanta.github.io/statdesign/

## Code of Conduct

We follow a simple guideline: be respectful and constructive in all interactions. We welcome contributions from developers of all experience levels.

## Statistical References

When implementing new statistical methods, please reference:

- Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences*
- Fleiss, J. L. (2003). *Statistical Methods for Rates and Proportions*  
- R's pwr package documentation and source code
- Relevant peer-reviewed statistical literature

Thank you for contributing to statdesign!