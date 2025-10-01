# Quickstart Guide

This guide demonstrates common use cases for statdesign's Python API and command-line interface.

## Installation

### Basic Installation

```bash
pip install statdesign
```

### With Enhanced Statistical Functions

For improved accuracy with exact noncentral distributions:

```bash
pip install statdesign[scipy]
```

## Python API Examples

### Two-Sample Proportions

```python
from statdesign import n_two_prop

# Basic calculation
n1, n2 = n_two_prop(p1=0.60, p2=0.50, alpha=0.05, power=0.80)
print(f"Group 1: {n1}, Group 2: {n2}")  # 394, 394

# Unequal allocation (2:1 ratio)
n1, n2 = n_two_prop(p1=0.60, p2=0.50, power=0.80, ratio=2.0)
print(f"Control: {n1}, Treatment: {n2}")  # 263, 526

# One-sided test
n1, n2 = n_two_prop(p1=0.60, p2=0.50, power=0.80, alternative="greater")
print(f"One-sided: {n1}, {n2}")  # 311, 311
```

### Two-Sample Means

```python
from statdesign import n_mean

# Z-test (known variance)
n1, n2 = n_mean(mu1=0.0, mu2=0.5, sd=1.0, power=0.80, test="z")
print(f"Z-test: {n1}, {n2}")  # 63, 63

# T-test (unknown variance) - requires SciPy for exact calculation
n1, n2 = n_mean(mu1=0.0, mu2=0.5, sd=1.0, power=0.80, test="t")
print(f"T-test: {n1}, {n2}")  # 64, 64 (with SciPy)

# Cohen's d effect size
import math
cohens_d = 0.5  # medium effect
n1, n2 = n_mean(mu1=0.0, mu2=cohens_d, sd=1.0, power=0.80, test="z")
print(f"Cohen's d={cohens_d}: {n1}, {n2}")  # 63, 63
```

### ANOVA Sample Sizes

```python
from statdesign import n_anova

# Requires SciPy for exact noncentral F calculations
try:
    n_per_group = n_anova(groups=4, cohen_f=0.25, power=0.80)
    print(f"Sample per group: {n_per_group}")  # 45
except RuntimeError as e:
    print(f"Install SciPy: {e}")
```

### Multiple Testing Corrections

```python
from statdesign import alpha_adjust

# Bonferroni correction (conservative)
alpha_bonf = alpha_adjust(m=10, alpha=0.05, method="bonferroni")
print(f"Bonferroni α: {alpha_bonf:.4f}")  # 0.0050

# Benjamini-Hochberg (less conservative)
alpha_bh = alpha_adjust(m=10, alpha=0.05, method="bh")
print(f"BH α: {alpha_bh:.4f}")  # 0.0500
```

## Command-Line Interface

### Basic Usage

```bash
# Two proportions
statdesign n_two_prop --p1 0.6 --p2 0.5 --alpha 0.05 --power 0.8

# Two means with table output
statdesign n_mean --mu1 0 --mu2 0.5 --sd 1 --power 0.8 --table

# Multiple testing correction
statdesign alpha_adjust --m 12 --method bh --alpha 0.05
```

### JSON Output

```bash
# Machine-readable output
statdesign n_two_prop --p1 0.6 --p2 0.5 --power 0.8 --json
# {"n1": 394, "n2": 394, "total": 788}
```

### Advanced Options

```bash
# Unequal allocation
statdesign n_mean --mu1 0 --mu2 0.5 --sd 1 --ratio 1.5 --power 0.8

# One-sided test
statdesign n_two_prop --p1 0.6 --p2 0.5 --alternative greater --power 0.8

# Custom alpha level
statdesign n_mean --mu1 0 --mu2 0.2 --sd 1 --alpha 0.01 --power 0.9
```

## SciPy Integration

### Manual Control

```python
from statdesign._scipy_backend import has_scipy, enable_scipy

# Check if SciPy is available
if has_scipy():
    print("SciPy available - using exact distributions")
    enable_scipy()
else:
    print("Using conservative normal approximations")
```

### Environment Variable

```bash
# Enable SciPy automatically if available
export STATDESIGN_AUTO_SCIPY=1

# Now all calculations use SciPy when possible
python -c "from statdesign import n_mean; print(n_mean(0, 0.5, 1, test='t'))"
```

## Power vs Sample Size Trade-offs

```python
from statdesign import n_two_prop

# Power curve: how sample size affects power
effect_size = 0.1  # p1=0.6, p2=0.5
for power in [0.70, 0.80, 0.90, 0.95]:
    n1, n2 = n_two_prop(p1=0.6, p2=0.5, power=power)
    print(f"Power {power:.0%}: n={n1} per group")

# Effect size curve: how effect size affects sample size  
for p2 in [0.45, 0.50, 0.55]:
    n1, n2 = n_two_prop(p1=0.60, p2=p2, power=0.80)
    effect = abs(0.60 - p2)
    print(f"Effect size {effect:.2f}: n={n1} per group")
```

## Common Pitfalls

### 1. Very Small Effect Sizes

```python
# This will require very large samples
n1, n2 = n_two_prop(p1=0.501, p2=0.500, power=0.80)  # n > 30,000!
```

### 2. Identical Groups (No Effect)

```python
# This raises an error
try:
    n_two_prop(p1=0.5, p2=0.5, power=0.80)
except ValueError as e:
    print(e)  # "Zero effect size detected"
```

### 3. Extreme Power Requirements

```python
# Very high power requires much larger samples
n_low = n_two_prop(p1=0.6, p2=0.5, power=0.80)[0]   # 394
n_high = n_two_prop(p1=0.6, p2=0.5, power=0.99)[0]  # 743
```

## Next Steps

- [CLI Reference](cli.md): Complete command-line documentation
- [API Reference](api.md): Detailed function reference with all parameters
- [Math Notes](math.md): Statistical formulas and assumptions
- [Contributing](contributing.md): Development setup and guidelines
