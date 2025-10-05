# Interactive Calculators

This page provides interactive calculators for common power and sample size calculations. These calculators use the same statistical methods as the statdesign library and provide immediate results in your browser.

## Two-Sample Proportion Calculator

Calculate the required sample size for comparing two proportions:

<iframe src="calculators/two_proportions.html" width="100%" height="800" frameborder="0" style="border: 1px solid #ddd; border-radius: 8px;"></iframe>

---

## Two-Sample Mean Calculator  

Calculate the required sample size for comparing two means:

<iframe src="calculators/two_means.html" width="100%" height="800" frameborder="0" style="border: 1px solid #ddd; border-radius: 8px;"></iframe>

---

## About These Calculators

These interactive calculators implement the same statistical formulas used in the statdesign Python library:

- **Two-Sample Proportions**: Uses the arcsin transformation method with normal approximation
- **Two-Sample Means**: Supports both z-test and t-test with degrees of freedom correction

### Key Features

- ✅ **Real-time calculation** as you change parameters  
- ✅ **Input validation** with helpful error messages
- ✅ **Effect size reporting** (Cohen's h for proportions, Cohen's d for means)
- ✅ **Allocation ratio support** for unequal group sizes
- ✅ **Multiple test types** (one-sided and two-sided)

### Limitations

- These calculators use JavaScript approximations for statistical functions
- For production use, we recommend the Python API for maximum accuracy
- Large sample approximations are used for t-distribution quantiles

### Corresponding CLI Commands

The calculations performed by these calculators correspond to these CLI commands:

```bash
# Two-sample proportions
statdesign n_two_prop --p1 0.6 --p2 0.5 --alpha 0.05 --power 0.8

# Two-sample means  
statdesign n_mean --mu1 0.0 --mu2 0.5 --sd 1.0 --alpha 0.05 --power 0.8
```

### Python API Examples

```python
from statdesign import n_two_prop, n_mean

# Two-sample proportions
n1, n2 = n_two_prop(p1=0.6, p2=0.5, alpha=0.05, power=0.8)
print(f"n1={n1}, n2={n2}")

# Two-sample means
n1, n2 = n_mean(mu1=0.0, mu2=0.5, sd=1.0, alpha=0.05, power=0.8)
print(f"n1={n1}, n2={n2}")
```