# statdesign

Tiny, tested power & sample-size utilities with a CLI.

## Install

```bash
pip install statdesign
```

## Quickstart

```bash
statdesign n-two-prop --p1 0.10 --p2 0.14 --alpha 0.05 --power 0.8 --ratio 1.0
```

```python
from statdesign.power import n_two_prop
n1, n2 = n_two_prop(0.10, 0.14, alpha=0.05, power=0.8)
```

## Scope

- One/two-sample means & proportions
- Paired designs
- Approximate one-way ANOVA
- Multiple-testing adjustments (Bonferroni, BH)

## Docs

```bash
mkdocs serve
```
