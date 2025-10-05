# StatDesign Examples

This directory contains JSON examples of `statdesign` CLI outputs for various statistical designs.

## Basic Examples

### two_prop_example.json
```bash
statdesign n_two_prop --p1 0.6 --p2 0.5 --alpha 0.05 --power 0.8
```
Standard two-sample proportion comparison (superiority test).

### two_mean_example.json  
```bash
statdesign n_mean --mu1 0.0 --mu2 0.5 --sd 1.0 --alpha 0.05 --power 0.8
```
Standard two-sample mean comparison (superiority test) using t-test.

### alpha_adjust_example.json
```bash
statdesign alpha_adjust --m 12 --method bonferroni
```
Bonferroni correction for multiple testing with 12 hypotheses.

## Equivalence/Non-inferiority Examples

### two_prop_equivalence.json
```bash
statdesign n_two_prop --p1 0.85 --p2 0.8 --alpha 0.05 --power 0.8 --ni-type equivalence --ni-margin 0.1
```
Two-sample proportion **equivalence** test with margin δ = 0.1.
Tests H₀: |p₁ - p₂| ≥ δ vs H₁: |p₁ - p₂| < δ

### two_prop_noninferiority.json
```bash
statdesign n_two_prop --p1 0.8 --p2 0.75 --alpha 0.05 --power 0.8 --ni-type noninferiority --ni-margin 0.05 --tail greater
```
Two-sample proportion **non-inferiority** test with margin δ = 0.05.
Tests H₀: p₁ - p₂ ≤ -δ vs H₁: p₁ - p₂ > -δ

### two_mean_equivalence.json
```bash
statdesign n_mean --mu1 10.0 --mu2 9.5 --sd 2.0 --alpha 0.05 --power 0.8 --ni-type equivalence --ni-margin 1.0
```
Two-sample mean **equivalence** test with margin δ = 1.0.
Tests H₀: |μ₁ - μ₂| ≥ δ vs H₁: |μ₁ - μ₂| < δ

### one_prop_equivalence.json
```bash
statdesign n_one_sample_prop --p 0.85 --p0 0.8 --alpha 0.05 --power 0.8 --ni-type equivalence --ni-margin 0.1
```
One-sample proportion **equivalence** test with margin δ = 0.1.
Tests H₀: |p - p₀| ≥ δ vs H₁: |p - p₀| < δ

## Usage Notes

### Equivalence vs Non-inferiority

- **Equivalence**: Two-sided test proving similarity within a margin
- **Non-inferiority**: One-sided test proving the new treatment is not worse by more than a margin

### Margin Selection

- **Proportions**: Margins are absolute differences (e.g., 0.05 = 5 percentage points)
- **Means**: Margins are in the same units as the outcome (consider standardizing)

### CLI Schema Validation

All examples can be validated against the CLI schema:

```bash
statdesign validate examples/two_prop_example.json
```

### Python API Equivalents

```python
from statdesign import n_two_prop, n_mean, n_one_sample_prop, alpha_adjust

# Basic two-sample proportion
n1, n2 = n_two_prop(p1=0.6, p2=0.5, alpha=0.05, power=0.8)

# Equivalence test
n1, n2 = n_two_prop(p1=0.85, p2=0.8, alpha=0.05, power=0.8, 
                    ni_type="equivalence", ni_margin=0.1)

# Non-inferiority test  
n1, n2 = n_two_prop(p1=0.8, p2=0.75, alpha=0.05, power=0.8,
                    ni_type="noninferiority", ni_margin=0.05, tail="greater")
```

### Statistical Context

These examples cover the most common clinical trial and research designs:

1. **Superiority trials**: Show one treatment is better than another
2. **Equivalence trials**: Show two treatments are similar within acceptable limits  
3. **Non-inferiority trials**: Show new treatment is not meaningfully worse
4. **Multiple testing**: Adjust for increased Type I error when testing multiple hypotheses

All calculations use established statistical methods with appropriate normal/t-distribution theory.