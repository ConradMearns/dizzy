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


def calculate_weighted_importance(df, row_weights):
    """Calculate weighted importance scores for each column.

    For House of Quality, this multiplies relationship strength by row importance.
    Formula: Column_Score = Σ(Row_Weight × Relationship_Strength)

    Args:
        df: DataFrame with relationship matrix
        row_weights: Dict mapping row names to their importance weights

    Returns:
        Dict of weighted importance scores for each column
    """
    importance = {}

    for col in df.columns:
        total = 0
        for idx, val in enumerate(df[col]):
            row_name = df.index[idx]
            row_weight = row_weights.get(row_name, 0)

            val_str = str(val).strip()
            strength = 0
            if val_str == '5':
                strength = 5
            elif val_str == '3':
                strength = 3
            elif val_str == '1':
                strength = 1

            total += row_weight * strength

        importance[col] = total

    return importance


def calculate_relative_importance(importance):
    """Calculate relative importance as percentages."""
    total = sum(importance.values())
    if total == 0:
        return {k: 0.0 for k in importance.keys()}

    relative = {k: (v / total) * 100 for k, v in importance.items()}
    return relative


def print_priority_report(title, df, importance, relative_importance, item_data, prefix,
                          weighted_importance=None, weighted_relative=None):
    """Print a priority report table.

    Args:
        title: Report title
        df: DataFrame with the matrix
        importance: Dict of importance scores (unweighted)
        relative_importance: Dict of relative importance percentages (unweighted)
        item_data: Dict of item descriptions
        prefix: Code prefix (e.g., "N" or "F")
        weighted_importance: Optional dict of customer-voice weighted importance scores
        weighted_relative: Optional dict of weighted relative importance percentages
    """
    print("=" * 100)
    print(title)
    print("=" * 100)
    print()

    # Determine if we're showing weighted columns
    show_weighted = weighted_importance is not None and weighted_relative is not None

    if show_weighted:
        # Sort by weighted importance (descending)
        sorted_items = sorted(weighted_importance.items(), key=lambda x: x[1], reverse=True)
        header = f"{'Code':<8} {'Unwt.':<10} {'Unwt.%':<8} {'Weighted':<12} {'Wt.%':<8} {'Description'}"
    else:
        # Sort by unweighted importance (descending)
        sorted_items = sorted(importance.items(), key=lambda x: x[1], reverse=True)
        header = f"{'Code':<8} {'Importance':<12} {'Relative %':<12} {'Description'}"

    print(header)
    print("-" * 100)

    for code, _ in sorted_items:
        imp_score = importance[code]
        rel_pct = relative_importance[code]

        # Find the item key from the code (N00 -> reversible-architecture)
        idx = int(code[1:])  # Extract number from N00, F01, etc.
        item_keys = list(item_data.keys())
        if idx < len(item_keys):
            item_key = item_keys[idx]
            item_desc = item_data[item_key].get('description', '')
            # Truncate description if too long
            if len(item_desc) > 45:
                item_desc = item_desc[:42] + "..."
        else:
            item_desc = "Unknown"

        if show_weighted:
            wt_score = weighted_importance[code]
            wt_pct = weighted_relative[code]
            print(f"{code:<8} {imp_score:<10.0f} {rel_pct:>6.1f}%  {wt_score:<12.1f} {wt_pct:>6.1f}%  {item_desc}")
        else:
            print(f"{code:<8} {imp_score:<12} {rel_pct:>6.1f}%      {item_desc}")

    print()
    if show_weighted:
        print(f"Total Unweighted: {sum(importance.values()):.0f}  |  Total Weighted: {sum(weighted_importance.values()):.1f}")
    else:
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

    # Get problem importance weights (customer voice)
    # For now, assume all problems have equal weight of 1.0
    # In future, these could come from YAML as 'importance' field
    problem_weights = {prob_key: 1.0 for prob_key in problems.keys()}

    # Calculate weighted need importance using problem weights
    weighted_importance_p2n = calculate_weighted_importance(df_p2n, problem_weights)
    weighted_relative_p2n = calculate_relative_importance(weighted_importance_p2n)

    print_priority_report(
        title="Problems-to-Needs: Need Priority Report (Unweighted - All Problems Equal)",
        df=df_p2n,
        importance=importance_p2n,
        relative_importance=relative_p2n,
        item_data=needs,
        prefix="N"
    )

    # ========== REPORT 2: Needs to Features (WITHOUT Customer Voice) ==========
    df_n2f = load_csv(NEEDS_TO_FEATURES_CSV, "NEED")
    importance_n2f = calculate_importance(df_n2f)
    relative_n2f = calculate_relative_importance(importance_n2f)

    print_priority_report(
        title="Needs-to-Features: Feature Priority Report (WITHOUT Customer Voice)",
        df=df_n2f,
        importance=importance_n2f,
        relative_importance=relative_n2f,
        item_data=features,
        prefix="F"
    )

    # ========== REPORT 3: Needs to Features (WITH Customer Voice) ==========
    # Use the need importance from problems-to-needs as customer voice weights
    # This implements the full House of Quality calculation:
    # Feature_Score = Σ(Need_Importance × Need-Feature_Relationship_Strength)
    # Map need keys to their codes (N00, N01, etc) for weighting
    need_keys = list(needs.keys())
    need_weights = {}
    for i, need_key in enumerate(need_keys):
        need_code = f"N{i:02d}"
        # Use the need importance from problems-to-needs as the weight
        need_weights[need_key] = importance_p2n.get(need_code, 0)

    weighted_importance_n2f = calculate_weighted_importance(df_n2f, need_weights)
    weighted_relative_n2f = calculate_relative_importance(weighted_importance_n2f)

    print_priority_report(
        title="Needs-to-Features: Feature Priority Report (WITH Customer Voice via Problem→Need weights)",
        df=df_n2f,
        importance=importance_n2f,
        relative_importance=relative_n2f,
        item_data=features,
        prefix="F",
        weighted_importance=weighted_importance_n2f,
        weighted_relative=weighted_relative_n2f
    )


if __name__ == "__main__":
    main()
