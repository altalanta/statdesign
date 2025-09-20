# Parity checks

CSV files in this directory capture parity comparisons against reference tools
(R's `pwr` package and G*Power). Each file stores both the external reference
value and the corresponding output from `statdesign`. The slow parity tests in
`tests/test_parity_numbers.py` load these tables and validate that the
statdesign values remain in sync with the references.

To regenerate the numbers, run the scripts in this directory (or the notebook
used in CI) within an environment where SciPy is enabled.
