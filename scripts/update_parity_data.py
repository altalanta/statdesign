#!/usr/bin/env python3
"""Script to update parity test data with computed statdesign values."""

import csv
from pathlib import Path

import statdesign


def update_parity_file(file_path: Path):
    """Update a parity CSV file with computed statdesign values."""
    if not file_path.exists():
        print(f"Skipping {file_path} - file does not exist")
        return

    rows = []
    with open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        for row in reader:
            # Compute statdesign value based on the type of test
            if "two_prop" in file_path.name:
                try:
                    n1, n2 = statdesign.n_two_prop(
                        p1=float(row["p1"]),
                        p2=float(row["p2"]),
                        power=float(row["power"]),
                        alpha=float(row["alpha"]),
                    )
                    row["statdesign"] = str(n1)  # Use n1 for comparison
                except Exception as e:
                    print(f"Error computing two_prop for row {row}: {e}")
                    row["statdesign"] = "ERROR"

            elif "two_means" in file_path.name:
                try:
                    n1, n2 = statdesign.n_mean(
                        mu1=float(row["mu1"]),
                        mu2=float(row["mu2"]),
                        sd=float(row["sd"]),
                        power=float(row["power"]),
                        alpha=float(row["alpha"]),
                        test="z",  # Use z-test for consistency with R pwr.t.test default
                    )
                    row["statdesign"] = str(n1)  # Use n1 for comparison
                except Exception as e:
                    print(f"Error computing two_means for row {row}: {e}")
                    row["statdesign"] = "ERROR"

            rows.append(row)

    # Write back the updated data
    with open(file_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Updated {file_path}")


def main():
    """Update all parity test files."""
    parity_dir = Path(__file__).parent.parent / "docs" / "parity"

    if not parity_dir.exists():
        print(f"Parity directory {parity_dir} does not exist")
        return

    for csv_file in parity_dir.glob("*.csv"):
        update_parity_file(csv_file)


if __name__ == "__main__":
    main()
