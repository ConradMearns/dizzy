#!/usr/bin/env python3
"""Generate product planning matrix CSVs from YAML file.

Generates two House of Quality matrices:
1. problems-to-needs.csv: Problems (rows) x Needs (columns)
2. product-planning.csv: Needs (rows) x Features (columns)

Each cell represents the interaction strength.
Valid values: 5 (strong), 3 (medium), 1 (weak), or --- (none/unknown)
"""

import pandas as pd
import yaml
from pathlib import Path

# File paths
SCRIPT_DIR = Path(__file__).parent
YAML_FILE = SCRIPT_DIR / "product-planning.yaml"
PROBLEMS_TO_NEEDS_CSV = SCRIPT_DIR / "problems-to-needs.csv"
NEEDS_TO_FEATURES_CSV = SCRIPT_DIR / "product-planning.csv"

DEFAULT_CELL_VALUE = "~"  # Valid values: 5, 3, 1, or ---


def load_yaml():
    """Load the product planning YAML file."""
    with open(YAML_FILE, "r") as f:
        return yaml.safe_load(f)


def generate_matrix_csv(csv_file, row_data, col_data, row_name, col_name, col_prefix):
    """Generate a matrix CSV file.

    Args:
        csv_file: Path to output CSV file
        row_data: Dict of row items (key -> {title, description})
        col_data: Dict of column items (key -> {description})
        row_name: Name for the row dimension (e.g., "PROBLEM", "NEED")
        col_name: Name for the column dimension (e.g., "Need", "Feature")
        col_prefix: Prefix for column codes (e.g., "N", "F")
    """
    # Create column codes (N00, N01, ... or F00, F01, ...)
    col_keys = list(col_data.keys())
    col_codes = {key: f"{col_prefix}{i:02d}" for i, key in enumerate(col_keys)}
    col_code_names = list(col_codes.values())

    # Row keys
    row_keys = list(row_data.keys())

    # Load existing CSV if it exists (skip comment lines)
    if csv_file.exists():
        existing_df = pd.read_csv(csv_file, comment='#')
        # Handle both old format (rows as unnamed index) and new format (row_name column last)
        if row_name in existing_df.columns:
            existing_df = existing_df.set_index(row_name)
        elif existing_df.columns[0].startswith('Unnamed:'):
            # Old format: first column is unnamed index
            existing_df = pd.read_csv(csv_file, comment='#', index_col=0)
        print(f"Loaded existing {csv_file.name} with {len(existing_df)} rows and {len(existing_df.columns)} columns")
    else:
        existing_df = pd.DataFrame()
        print(f"No existing {csv_file.name} found, creating new one")

    # Create new DataFrame
    new_df = pd.DataFrame(
        index=row_keys,
        columns=col_code_names
    )

    # Populate with existing values or default (with spaces for readability)
    for row_key in row_keys:
        for col_code in col_code_names:
            if not existing_df.empty and row_key in existing_df.index and col_code in existing_df.columns:
                # Preserve existing value and format with spaces
                val = str(existing_df.loc[row_key, col_code]).strip()
                new_df.loc[row_key, col_code] = f" {val} "
            else:
                # New cell, use default with spaces
                new_df.loc[row_key, col_code] = f" {DEFAULT_CELL_VALUE} "

    # Reset index to make row dimension a regular column, then reorder so row_name is last
    new_df = new_df.reset_index()
    new_df = new_df.rename(columns={'index': row_name})
    # Reorder columns: col codes first, then row_name
    cols = col_code_names + [row_name]
    new_df = new_df[cols]

    # Write CSV with column mapping comments at the top
    with open(csv_file, 'w') as f:
        # Write header comments explaining column codes
        f.write(f"# {col_name} Mapping:\n")
        for col_key, code in col_codes.items():
            col_desc = col_data[col_key].get('description', col_key)
            f.write(f"# {code}: {col_key} - {col_desc}\n")
        f.write("#\n")
        f.write("# Interaction strength values: 5 (strong), 3 (medium), 1 (weak), --- (none/unknown)\n")
        f.write("#\n")

        # Write the DataFrame (index=False since row_name is now a regular column)
        new_df.to_csv(f, index=False)

    print(f"Wrote {csv_file.name} with {len(new_df)} rows and {len(new_df.columns) - 1} columns")

    # Print column mapping for reference
    print(f"\n{col_name} mapping:")
    for col_key, code in col_codes.items():
        print(f"  {code}: {col_key}")


def main():
    # Load YAML data
    data = load_yaml()

    problems = data.get("problems", {})
    needs = data.get("needs", {})
    features = data.get("features", {})

    # Generate problems-to-needs matrix (Problem x Need)
    print("=" * 60)
    print("Generating Problems-to-Needs Matrix")
    print("=" * 60)
    generate_matrix_csv(
        csv_file=PROBLEMS_TO_NEEDS_CSV,
        row_data=problems,
        col_data=needs,
        row_name="PROBLEM",
        col_name="Need",
        col_prefix="N"
    )

    print("\n" + "=" * 60)
    print("Generating Needs-to-Features Matrix")
    print("=" * 60)
    # Generate needs-to-features matrix (Need x Feature)
    generate_matrix_csv(
        csv_file=NEEDS_TO_FEATURES_CSV,
        row_data=needs,
        col_data=features,
        row_name="NEED",
        col_name="Feature",
        col_prefix="F"
    )


if __name__ == "__main__":
    main()
