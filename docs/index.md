# statdesign

[![PyPI version](https://badge.fury.io/py/statdesign.svg)](https://badge.fury.io/py/statdesign)
[![CI](https://github.com/altalanta/statdesign/workflows/CI/badge.svg)](https://github.com/altalanta/statdesign/actions)
[![Coverage](https://codecov.io/gh/altalanta/statdesign/branch/main/graph/badge.svg)](https://codecov.io/gh/altalanta/statdesign)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Deterministic power and sample-size calculations with a unified Python API and CLI.

## Features

- **Comprehensive calculations**: Two-sample proportions, means, paired samples, one-sample tests, ANOVA
- **Survival analysis**: Logrank tests, Cox regression event requirements
- **Design effects**: Cluster randomization and repeated measures adjustments  
- **Multiple testing**: Bonferroni and Benjamini-Hochberg corrections
- **Optional SciPy integration**: Enhanced accuracy with noncentral t/F distributions
- **Command-line interface**: Full CLI with JSON and table output formats
- **Production ready**: Comprehensive test suite, parity tests against R, CI/CD

## Quick Start

```bash
pip install statdesign
```

For enhanced statistical distributions (recommended):

```bash
pip install statdesign[scipy]
```

### Library Usage

```python
from statdesign import n_two_prop, n_mean, n_anova, alpha_adjust

# Two-sample proportions (normal approximation)
n1, n2 = n_two_prop(p1=0.60, p2=0.50, power=0.80)
# Returns: (394, 394)

# Two-sample means with unequal allocation
n1, n2 = n_mean(mu1=0.0, mu2=0.5, sd=1.0, ratio=1.5, test="z")
# Returns: (51, 77)

# ANOVA using Cohen's f (requires SciPy)
n_per_group = n_anova(groups=4, cohen_f=0.25, power=0.80)
# Returns: 45

# Multiple testing correction
adjusted_alpha = alpha_adjust(m=8, method="bonferroni")
# Returns: 0.00625
```

### CLI Usage

```bash
# Sample size for two proportions
statdesign n_two_prop --p1 0.6 --p2 0.5 --alpha 0.05 --power 0.8

# Sample size for two means with table output
statdesign n_mean --mu1 0 --mu2 0.5 --sd 1 --table

# Multiple testing correction
statdesign alpha_adjust --m 12 --method bh
```

## Why statdesign?

- **Deterministic**: Reproducible results across environments
- **Fast**: Analytical formulas, no simulation
- **Comprehensive**: Covers common study designs
- **Validated**: Parity tests against R's `pwr` package
- **Flexible**: Python API and CLI for different workflows
- **Well-tested**: >95% test coverage with edge cases

## Next Steps

- [Quickstart Guide](quickstart.md): Complete installation and usage guide
- [CLI Reference](cli.md): Command-line interface documentation
- [API Reference](api.md): Complete function reference
- [Math Notes](math.md): Statistical formulas and assumptions
