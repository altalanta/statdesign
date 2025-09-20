# statdesign

Deterministic power and sample-size utilities with a single Python API and CLI.

## Install

```bash
pip install statdesign
```

The library relies on analytical formulae for normal approximations. When
`t`/`F`-based designs are required, enable SciPy in a compatible environment by
setting `STATDESIGN_AUTO_SCIPY=1` before calling the API.

## Library usage

```python
from statdesign import n_two_prop, n_mean, n_anova, alpha_adjust

# Two-sample proportions (normal approximation)
n1, n2 = n_two_prop(p1=0.60, p2=0.50, power=0.80)

# Two-sample means with unequal allocation using the z-approximation
n1, n2 = n_mean(mu1=0.0, mu2=0.5, sd=1.0, ratio=1.5, test="z")

# Multiple testing helper
per_test_alpha = alpha_adjust(m=8, method="bonferroni")
```

All core APIs live in `statdesign.api` and are re-exported at the package root.
Functions guard their inputs and raise informative errors for unsupported
configurations (e.g. exact binomial with very large samples).

## CLI quickstart

```bash
statdesign n_two_prop --p1 0.6 --p2 0.5 --alpha 0.05 --power 0.8
statdesign alpha_adjust --m 12 --method bh
```

Every API function is mirrored by a subcommand. Results are emitted as JSON so
shell pipelines can consume them directly.

## Endpoints

- `n_two_prop` / `n_one_sample_prop` with optional non-inferiority/equivalence
  margins and exact small-sample support.
- `n_mean`, `n_one_sample_mean`, `n_paired` (normal approximation by default,
  optional SciPy-backed noncentral t when available).
- `n_anova` using Cohen's *f* (requires SciPy for noncentral F).
- `alpha_adjust` and `bh_thresholds` for Bonferroni and Benjamini–Hochberg.

Golden files cover the primary scenarios and doc examples provide parity tables
against R's `pwr` / G*Power values.

## Development

```bash
pip install -e ".[tests,docs]"
pytest
STATDESIGN_AUTO_SCIPY=1 pytest  # enable SciPy backed paths when available
mkdocs serve
```

Coverage thresholds are enforced at 95% on `statdesign/`.
