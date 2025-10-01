# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-10-01

### Added
- Initial public release
- Core statistical power and sample size calculation functions
- Support for two-sample proportions, means, ANOVA, and survival analysis
- Optional SciPy integration for noncentral t/F distributions
- Command-line interface with JSON and table output formats
- Comprehensive test suite with golden files and parity tests
- Documentation with MkDocs and Material theme
- CI/CD workflows for testing and releases

### Features
- **Power calculations**: n_two_prop, n_mean, n_paired, n_one_sample_mean, n_one_sample_prop
- **ANOVA**: n_anova using Cohen's f (requires SciPy for noncentral F)
- **Survival analysis**: required_events_logrank, required_events_cox, power_logrank_from_n
- **Design effects**: Cluster randomization and repeated measures adjustments
- **Multiple testing**: Bonferroni and Benjamini-Hochberg corrections
- **CLI**: Full command-line interface with `statdesign` command

[Unreleased]: https://github.com/altalanta/statdesign/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/altalanta/statdesign/releases/tag/v0.1.0