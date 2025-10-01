# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-XX

### Added
- **Core statistical functions**:
  - `n_two_prop()`: Two-sample proportion tests
  - `n_mean()`: Two-sample mean tests (z-test and t-test)  
  - `n_one_sample_prop()`: One-sample proportion tests
  - `n_anova()`: One-way ANOVA sample size calculations
  - `alpha_adjust()`: Multiple testing corrections (Bonferroni, Benjamini-Hochberg)

- **Command-line interface**:
  - Complete CLI for all statistical functions
  - JSON and table output formats
  - Input validation and helpful error messages
  - `--version` flag to show version information
  - `--ci` flag for confidence interval assumptions

- **Optional SciPy integration**:
  - Enhanced accuracy with noncentral t and F distributions
  - Graceful fallback to conservative normal approximations
  - `STATDESIGN_AUTO_SCIPY` environment variable support
  - Separate `scipy` optional dependency group

- **Comprehensive testing**:
  - >95% test coverage
  - Parity tests against R's pwr package
  - Property-based testing with Hypothesis
  - Performance benchmarks with pytest-benchmark
  - Edge case validation

- **Documentation**:
  - Complete API reference with examples
  - Mathematical notes explaining formulas and assumptions
  - Command-line usage guide
  - Contributing guidelines
  - MkDocs site with Material theme

- **Production features**:
  - Type hints throughout (`py.typed` marker)
  - Comprehensive input validation
  - Deterministic calculations (no simulation)
  - Conservative adjustments when SciPy unavailable
  - Semantic versioning

### Technical Details
- Python 3.9+ support
- Pure Python core with optional SciPy acceleration
- Modern packaging with pyproject.toml
- CI/CD with GitHub Actions
- Automated PyPI publishing

[Unreleased]: https://github.com/altalanta/statdesign/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/altalanta/statdesign/releases/tag/v0.1.0