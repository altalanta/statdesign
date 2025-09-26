# CLI Reference

The package installs a single entry point `statdesign`. Global flags control the
output format:

- `--json/--no-json` (default `--json`) emits machine-friendly JSON payloads.
- `--table/--no-table` renders a human table. When stdout is a TTY the table is
  prettified with Rich (if installed), otherwise a GitHub-flavoured table is
  returned.

Example:

```bash
statdesign n_two_prop --p1 0.6 --p2 0.5 --alpha 0.05 --power 0.8
{"n1":389,"n2":389}

statdesign --no-json --table alpha_adjust --m 4 --alpha 0.04 --method bh
| key        | value                  |
|------------|------------------------|
| thresholds | 0.01, 0.02, 0.03, 0.04 |
```

Every public API function is mirrored by a subcommand:

| Command | Maps to | Notes |
| --- | --- | --- |
| `n_two_prop` | `statdesign.n_two_prop` | Supports normal and exact tests plus NI/TOST margins |
| `n_one_sample_prop` | `statdesign.n_one_sample_prop` | Exact enumeration for small $n$ |
| `n_mean` | `statdesign.n_mean` | `--test` accepts `z` or `t` with fallback cushion |
| `n_one_sample_mean` | `statdesign.n_one_sample_mean` | |
| `n_paired` | `statdesign.n_paired` | |
| `n_anova` | `statdesign.n_anova` | `--allocation` takes comma-separated weights |
| `alpha_adjust` | `statdesign.alpha_adjust` / `bh_thresholds` | `--method bh` emits thresholds |
| `bh_thresholds` | `statdesign.bh_thresholds` | Shortcut when only BH cutoffs are needed |

Errors are emitted on stderr with exit code `2` for invalid inputs and `3` for
unavailable approximations (e.g. requesting exact noncentral calculations without
SciPy). Use `statdesign COMMAND --help` for detailed per-command options.
