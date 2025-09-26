# statdesign

`statdesign` provides deterministic power and sample size calculations for common
clinical and translational study designs. Every calculation is exposed through a
well-typed Python API and a streamlined CLI so you can integrate power checks
into notebooks, CI pipelines, or handoff documents without touching spreadsheets.

## Highlights

- Analytic solutions for proportions, means, one-way ANOVA, and exponential
  survival models.
- Optional SciPy integration (`STATDESIGN_AUTO_SCIPY=1`) enables exact
  noncentral $t$/$F$ distributions while the default install stays lightweight
  using conservative normal approximations.
- Consistent input validation with rich error messages and JSON-friendly CLI
  output for automation.
- Test suite with >70% coverage, parity checks against R `pwr`/G*Power, and
  property tests to guard monotonicity.
- MkDocs material documentation, parity tables, and reproducible scripts for
  generating published tables.

Use the navigation sidebar to explore installation instructions, quickstart
examples, theoretical notes, and an auto-generated API reference.
