# Quickstart (Python API)

```python
from statdesign import n_two_prop, n_mean, alpha_adjust

# Two-sample proportions (normal approximation).
n1, n2 = n_two_prop(p1=0.60, p2=0.50, alpha=0.05, power=0.80)
print(n1, n2)  # 389 389

# Two-sample means with a conservative t-approximation fallback.
n1, n2 = n_mean(mu1=0.0, mu2=0.5, sd=1.0, ratio=1.0, test="t")
print(n1, n2)  # 64 64 when SciPy is available or via the fallback cushion

# Family-wise error control for multiple hypotheses.
per_test_alpha = alpha_adjust(m=8, method="bonferroni")
```

### SciPy-backed distributions

Activate SciPy support when you need exact noncentral $t$ or $F$ behaviour:

```bash
export STATDESIGN_AUTO_SCIPY=1
pip install "statdesign[full]"  # ensures SciPy is available
```

When SciPy is unavailable the package uses normal approximations and inflates
sample sizes slightly to remain conservative. The documentation details when
approximations are adequate and when you should enable SciPy.
