# Usage

## CLI

```bash
statdesign power-two-prop --p1 0.10 --p2 0.14 --alpha 0.05 --n1 350 --n2 350
statdesign n-two-prop --p1 0.10 --p2 0.14 --alpha 0.05 --power 0.8 --ratio 1.0
```

## Python

```python
from statdesign.power import n_two_prop, power_two_prop
n1, n2 = n_two_prop(p1=0.10, p2=0.14, alpha=0.05, power=0.8, ratio=1.0)
power = power_two_prop(p1=0.10, p2=0.14, n1=n1, n2=n2, alpha=0.05)
```
