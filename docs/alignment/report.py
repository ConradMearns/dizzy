#!/usr/bin/env python3
"""Generate House of Quality priority report from product planning data.

This script calculates:
- Feature Importance: Sum of interaction strengths for each feature
- Relative Feature Importance: Percentage contribution of each feature
"""

import pandas as pd
import yaml
from pathlib import Path

# File paths
SCRIPT_DIR = Path(__file__).parent
YAML_FILE = SCRIPT_DIR / "product-planning.yaml"
CSV_FILE = SCRIPT_DIR / "product-planning.csv"


def load_yaml():
    """Load the product planning YAML file."""
    with open(YAML_FILE, "r") as f:
        return yaml.safe_load(f)


def load_csv():
    """Load the product planning CSV file."""
    df = pd.read_csv(CSV_FILE, comment='#')
    # Set NEED as index
    if 'NEED' in df.columns:
        df = df.set_index('NEED')
    return df


def calculate_feature_importance(df):
    """Calculate feature importance scores.

    For each feature column, sum up the interaction strengths.
    Values: 5 (strong), 3 (medium), 1 (weak), --- (0)
    """
    importance = {}

    for col in df.columns:
        total = 0
        for val in df[col]:
            val_str = str(val).strip()
            if val_str == '5':
                total += 5
            elif val_str == '3':
                total += 3
            elif val_str == '1':
                total += 1
            # else: '---' or other values count as 0
        importance[col] = total

    return importance


def calculate_relative_importance(importance):
    """Calculate relative importance as percentages."""
    total = sum(importance.values())
    if total == 0:
        return {k: 0.0 for k in importance.keys()}

    relative = {k: (v / total) * 100 for k, v in importance.items()}
    return relative


def main():
    print("=" * 60)
    print("House of Quality - Feature Priority Report")
    print("=" * 60)
    print()

    # Load data
    data = load_yaml()
    df = load_csv()

    # Get feature descriptions
    features = data.get("features", {})

    # Calculate importance
    importance = calculate_feature_importance(df)
    relative_importance = calculate_relative_importance(importance)

    # Sort by importance (descending)
    sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)

    # Print results
    print(f"{'Feature':<8} {'Importance':<12} {'Relative %':<12} {'Description'}")
    print("-" * 60)

    for feat_code, imp_score in sorted_features:
        rel_pct = relative_importance[feat_code]

        # Find the feature key from the code (F00 -> mermaid-def-rendering)
        feat_idx = int(feat_code[1:])  # Extract number from F00, F01, etc.
        feat_keys = list(features.keys())
        if feat_idx < len(feat_keys):
            feat_key = feat_keys[feat_idx]
            feat_desc = features[feat_key].get('description', '')
            # Truncate description if too long
            if len(feat_desc) > 40:
                feat_desc = feat_desc[:37] + "..."
        else:
            feat_desc = "Unknown"

        print(f"{feat_code:<8} {imp_score:<12} {rel_pct:>6.1f}%      {feat_desc}")

    print()
    print(f"Total Importance: {sum(importance.values())}")
    print()


if __name__ == "__main__":
    main()
