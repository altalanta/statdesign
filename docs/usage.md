# Usage

## Python API

```python
from statdesign import (
    n_two_prop,
    n_one_sample_prop,
    n_mean,
    n_one_sample_mean,
    n_paired,
    n_anova,
    alpha_adjust,
)

# Normal-approximation for two independent proportions
n1, n2 = n_two_prop(p1=0.60, p2=0.50, alpha=0.05, power=0.80, ratio=1.0)

# One-sample proportion with an exact binomial inversion
n_exact = n_one_sample_prop(p=0.65, p0=0.50, exact=True)

# Two-sample means (z-approximation)
n1, n2 = n_mean(mu1=0.0, mu2=0.5, sd=1.0, test="z", ratio=1.5)

# Enable SciPy-backed calculations when available
import os
os.environ["STATDESIGN_AUTO_SCIPY"] = "1"
n_pairs = n_paired(delta=0.4, sd_diff=1.1, power=0.85)
```

All functions validate arguments and return integer sample sizes.

## CLI

```bash
statdesign n_two_prop --p1 0.6 --p2 0.5 --alpha 0.05 --power 0.8
statdesign n_one_sample_prop --p 0.65 --p0 0.50 --exact
statdesign n_mean --mu1 0 --mu2 0.5 --sd 1.0 --test z
statdesign alpha_adjust --m 12 --method bh
```

Every subcommand prints JSON—handy for piping the output into other tooling.

## Multiple testing utilities

```python
from statdesign import alpha_adjust, bh_thresholds

per_test_alpha = alpha_adjust(m=4, method="bonferroni")  # 0.0125
bh_steps = bh_thresholds(5, alpha=0.05)  # [0.01, 0.02, 0.03, 0.04, 0.05]
```

Refer to `docs/approximations.md` for detailed formulas and limits used by each
function.
