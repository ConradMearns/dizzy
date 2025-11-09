#!/usr/bin/env python3
"""Generate House of Quality priority reports from product planning data.

This script generates two reports:
1. Problems-to-Needs: Which needs are most important for solving core problems
2. Needs-to-Features: Which features are most important for delivering needs

Each report calculates:
- Importance: Sum of interaction strengths
- Relative Importance: Percentage contribution
"""

import pandas as pd
import yaml
from pathlib import Path

# File paths
SCRIPT_DIR = Path(__file__).parent
YAML_FILE = SCRIPT_DIR / "product-planning.yaml"
PROBLEMS_TO_NEEDS_CSV = SCRIPT_DIR / "problems-to-needs.csv"
NEEDS_TO_FEATURES_CSV = SCRIPT_DIR / "product-planning.csv"


def load_yaml():
    """Load the product planning YAML file."""
    with open(YAML_FILE, "r") as f:
        return yaml.safe_load(f)


def load_csv(csv_file, row_name):
    """Load a matrix CSV file."""
    df = pd.read_csv(csv_file, comment='#')
    # Set row dimension as index
    if row_name in df.columns:
        df = df.set_index(row_name)
    return df


def calculate_importance(df):
    """Calculate importance scores for each column.

    For each column, sum up the interaction strengths.
    Values: 5 (strong), 3 (medium), 1 (weak), --- or ~ (0)
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
            # else: '---', '~', or other values count as 0
        importance[col] = total

    return importance


def calculate_relative_importance(importance):
    """Calculate relative importance as percentages."""
    total = sum(importance.values())
    if total == 0:
        return {k: 0.0 for k in importance.keys()}

    relative = {k: (v / total) * 100 for k, v in importance.items()}
    return relative


def print_priority_report(title, df, importance, relative_importance, item_data, prefix):
    """Print a priority report table.

    Args:
        title: Report title
        df: DataFrame with the matrix
        importance: Dict of importance scores
        relative_importance: Dict of relative importance percentages
        item_data: Dict of item descriptions
        prefix: Code prefix (e.g., "N" or "F")
    """
    print("=" * 60)
    print(title)
    print("=" * 60)
    print()

    # Sort by importance (descending)
    sorted_items = sorted(importance.items(), key=lambda x: x[1], reverse=True)

    # Print results
    print(f"{'Code':<8} {'Importance':<12} {'Relative %':<12} {'Description'}")
    print("-" * 60)

    for code, imp_score in sorted_items:
        rel_pct = relative_importance[code]

        # Find the item key from the code (N00 -> reversible-architecture)
        idx = int(code[1:])  # Extract number from N00, F01, etc.
        item_keys = list(item_data.keys())
        if idx < len(item_keys):
            item_key = item_keys[idx]
            item_desc = item_data[item_key].get('description', '')
            # Truncate description if too long
            if len(item_desc) > 40:
                item_desc = item_desc[:37] + "..."
        else:
            item_desc = "Unknown"

        print(f"{code:<8} {imp_score:<12} {rel_pct:>6.1f}%      {item_desc}")

    print()
    print(f"Total Importance: {sum(importance.values())}")
    print()


def main():
    # Load data
    data = load_yaml()
    problems = data.get("problems", {})
    needs = data.get("needs", {})
    features = data.get("features", {})

    # ========== REPORT 1: Problems to Needs ==========
    df_p2n = load_csv(PROBLEMS_TO_NEEDS_CSV, "PROBLEM")
    importance_p2n = calculate_importance(df_p2n)
    relative_p2n = calculate_relative_importance(importance_p2n)

    print_priority_report(
        title="Problems-to-Needs: Need Priority Report",
        df=df_p2n,
        importance=importance_p2n,
        relative_importance=relative_p2n,
        item_data=needs,
        prefix="N"
    )

    # ========== REPORT 2: Needs to Features ==========
    df_n2f = load_csv(NEEDS_TO_FEATURES_CSV, "NEED")
    importance_n2f = calculate_importance(df_n2f)
    relative_n2f = calculate_relative_importance(importance_n2f)

    print_priority_report(
        title="Needs-to-Features: Feature Priority Report",
        df=df_n2f,
        importance=importance_n2f,
        relative_importance=relative_n2f,
        item_data=features,
        prefix="F"
    )


if __name__ == "__main__":
    main()
