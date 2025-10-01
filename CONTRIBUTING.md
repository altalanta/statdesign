# Contributing to statdesign

Thank you for your interest in contributing to statdesign! This document provides guidelines for development, testing, and releases.

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/altalanta/statdesign.git
   cd statdesign
   ```

2. **Install in development mode**:
   ```bash
   pip install -e ".[tests,docs,scipy]"
   ```

3. **Install pre-commit hooks** (optional but recommended):
   ```bash
   pre-commit install
   ```

## Running Tests

### Basic test suite:
```bash
pytest
```

### With SciPy features enabled:
```bash
STATDESIGN_AUTO_SCIPY=1 pytest
```

### With coverage reporting:
```bash
pytest --cov=statdesign --cov-report=html
```

### Run specific test categories:
```bash
# Fast tests only
pytest -m "not slow"

# Golden file comparisons
pytest tests/test_parity_numbers.py

# CLI tests
pytest tests/test_cli.py
```

## Coverage Requirements

- **Minimum coverage**: 95% on `statdesign/` package code
- **Excluded from coverage**: CLI module and simulation utilities
- **Coverage report**: Generated in `htmlcov/` directory

## Code Quality

### Linting and formatting:
```bash
ruff check src tests          # Linting
ruff format src tests         # Auto-formatting
```

### Type checking:
```bash
mypy                         # Type checking (strict mode)
```

### Security scanning:
```bash
bandit -r src/statdesign     # Security analysis
```

## Testing Guidelines

### Test Structure
- **Unit tests**: `tests/test_*.py` for individual functions
- **Golden files**: `tests/golden/` for reference comparisons
- **Parity tests**: Comparison against R's `pwr` package outputs
- **CLI tests**: Command-line interface validation
- **Property tests**: Using Hypothesis for edge cases

### Adding New Tests
1. Write tests for both with/without SciPy paths when applicable
2. Include edge cases and error conditions
3. Add golden files for complex calculations
4. Document expected behavior and assumptions

## Documentation

### Building documentation locally:
```bash
mkdocs serve
```

### Documentation structure:
- **API Reference**: Auto-generated from docstrings
- **CLI Usage**: Command examples with outputs
- **Math Notes**: Statistical formulas and assumptions
- **Quickstart**: Installation and basic usage

### Writing documentation:
- Use clear, executable examples
- Include expected outputs
- Document mathematical assumptions
- Cross-reference related functions

## Release Process

### Version Numbering
We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Steps

1. **Update version number**:
   ```bash
   # Update src/statdesign/__init__.py
   __version__ = "x.y.z"
   
   # Update pyproject.toml
   version = "x.y.z"
   ```

2. **Update CHANGELOG.md**:
   - Move unreleased changes to new version section
   - Add release date
   - Update comparison links

3. **Create and push tag**:
   ```bash
   git tag vx.y.z
   git push origin vx.y.z
   ```

4. **GitHub Actions will automatically**:
   - Run full test suite
   - Build source distribution and wheel
   - Publish to TestPyPI then PyPI
   - Deploy documentation

### Manual Release (if needed)
```bash
# Build packages
python -m build

# Check packages
twine check dist/*

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## API Design Principles

1. **Consistency**: Function signatures should follow consistent patterns
2. **Validation**: Input validation with clear error messages
3. **Documentation**: Comprehensive docstrings with examples
4. **Performance**: Efficient implementations with optional optimizations
5. **Compatibility**: Maintain backward compatibility when possible

## Submission Guidelines

### Pull Requests
1. **Branch naming**: `feature/description` or `fix/description`
2. **Commit messages**: Follow conventional commit format
3. **Tests**: Include tests for new functionality
4. **Documentation**: Update docs for API changes
5. **Changelog**: Add entry to unreleased section

### Review Process
- All PRs require review before merging
- CI must pass (tests, linting, type checking)
- Coverage must meet minimum thresholds
- Documentation builds successfully

## Getting Help

- **Issues**: Report bugs or request features on GitHub Issues
- **Discussions**: Ask questions in GitHub Discussions
- **Documentation**: Check the official docs first

## License

By contributing to statdesign, you agree that your contributions will be licensed under the MIT License.