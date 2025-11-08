#!/usr/bin/env python3
"""Generate product planning matrix CSV from YAML file.

Each cell represents the interaction strength between a need and a feature.
Valid values: 5 (strong), 3 (medium), 1 (weak), or --- (none/unknown)
"""

import pandas as pd
import yaml
from pathlib import Path

# File paths
SCRIPT_DIR = Path(__file__).parent
YAML_FILE = SCRIPT_DIR / "product-planning.yaml"
CSV_FILE = SCRIPT_DIR / "product-planning.csv"

DEFAULT_CELL_VALUE = "~"  # Valid values: 5, 3, 1, or ---


def load_yaml():
    """Load the product planning YAML file."""
    with open(YAML_FILE, "r") as f:
        return yaml.safe_load(f)


def main():
    # Load YAML data
    data = load_yaml()

    # Extract features and needs with their keys and descriptions
    features = data.get("features", {})
    needs = list(data.get("needs", {}).keys())

    # Create feature column names with numbers (F00, F01, etc.)
    feature_keys = list(features.keys())
    feature_cols = {feat: f"F{i:02d}" for i, feat in enumerate(feature_keys)}
    feature_col_names = list(feature_cols.values())

    # Load existing CSV if it exists (skip comment lines)
    if CSV_FILE.exists():
        existing_df = pd.read_csv(CSV_FILE, comment='#')
        # Handle both old format (needs as unnamed index) and new format (NEED column last)
        if 'NEED' in existing_df.columns:
            existing_df = existing_df.set_index('NEED')
        elif existing_df.columns[0].startswith('Unnamed:'):
            # Old format: first column is unnamed index
            existing_df = pd.read_csv(CSV_FILE, comment='#', index_col=0)
        print(f"Loaded existing CSV with {len(existing_df)} needs and {len(existing_df.columns)} features")
    else:
        existing_df = pd.DataFrame()
        print("No existing CSV found, creating new one")

    # Create new DataFrame with current needs and features
    new_df = pd.DataFrame(
        index=needs,
        columns=feature_col_names
    )

    # Populate with existing values or default (with spaces for readability)
    for need in needs:
        for feat_col in feature_col_names:
            if not existing_df.empty and need in existing_df.index and feat_col in existing_df.columns:
                # Preserve existing value and format with spaces
                val = str(existing_df.loc[need, feat_col]).strip()
                new_df.loc[need, feat_col] = f" {val} "
            else:
                # New cell, use default with spaces
                new_df.loc[need, feat_col] = f" {DEFAULT_CELL_VALUE} "

    # Reset index to make needs a regular column, then reorder so NEED is last
    new_df = new_df.reset_index()
    new_df = new_df.rename(columns={'index': 'NEED'})
    # Reorder columns: features first, then NEED
    cols = feature_col_names + ['NEED']
    new_df = new_df[cols]

    # Write CSV with feature mapping comments at the top
    with open(CSV_FILE, 'w') as f:
        # Write header comments explaining feature codes
        f.write("# Feature Mapping:\n")
        for feat_key, code in feature_cols.items():
            feat_desc = features[feat_key].get('description', feat_key)
            f.write(f"# {code}: {feat_key} - {feat_desc}\n")
        f.write("#\n")
        f.write("# Interaction strength values: 5 (strong), 3 (medium), 1 (weak), --- (none/unknown)\n")
        f.write("#\n")

        # Write the DataFrame (index=False since NEED is now a regular column)
        new_df.to_csv(f, index=False)

    print(f"Wrote CSV with {len(new_df)} needs and {len(new_df.columns) - 1} features to {CSV_FILE}")

    # Print feature mapping for reference
    print("\nFeature mapping:")
    for feat, code in feature_cols.items():
        print(f"  {code}: {feat}")


if __name__ == "__main__":
    main()
