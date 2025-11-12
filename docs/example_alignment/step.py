#!/usr/bin/env python3
"""Generate iterative importance scores for Problems, Needs, and Features.

This script produces step files (001.step, 002.step, etc.) containing relative
importance scores that refine over iterations.

Step 001: Calculate directly from matrices (row/column sums)
Step 002+: Use previous step's scores as weights for refinement
"""

import pandas as pd
import yaml
import sys
from pathlib import Path

# File paths
SCRIPT_DIR = Path(__file__).parent
YAML_FILE = SCRIPT_DIR / "product-planning.yaml"
PROBLEMS_TO_NEEDS_CSV = SCRIPT_DIR / "problems-to-needs.csv"
NEEDS_TO_FEATURES_CSV = SCRIPT_DIR / "product-planning.csv"
FEATURES_TO_PROBLEMS_CSV = SCRIPT_DIR / "features-to-problems.csv"


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


def parse_value(val):
    """Parse a matrix value to numeric score."""
    val_str = str(val).strip()
    if val_str == '5':
        return 5
    elif val_str == '3':
        return 3
    elif val_str == '1':
        return 1
    return 0


def calculate_row_importance(df):
    """Calculate importance scores for each row (sum across columns)."""
    importance = {}
    for idx in df.index:
        total = sum(parse_value(val) for val in df.loc[idx])
        importance[idx] = total
    return importance


def calculate_column_importance(df):
    """Calculate importance scores for each column (sum down rows)."""
    importance = {}
    for col in df.columns:
        total = sum(parse_value(val) for val in df[col])
        importance[col] = total
    return importance


def calculate_weighted_column_importance(df, row_weights):
    """Calculate weighted importance for columns using row weights.

    Formula: Column_Score = Σ(Row_Weight × Relationship_Strength)
    """
    importance = {}
    for col in df.columns:
        total = 0
        for idx in df.index:
            row_weight = row_weights.get(idx, 0)
            strength = parse_value(df.loc[idx, col])
            total += row_weight * strength
        importance[col] = total
    return importance


def calculate_weighted_row_importance(df, col_weights):
    """Calculate weighted importance for rows using column weights.

    Formula: Row_Score = Σ(Column_Weight × Relationship_Strength)
    """
    importance = {}
    for idx in df.index:
        total = 0
        for col in df.columns:
            col_weight = col_weights.get(col, 0)
            strength = parse_value(df.loc[idx, col])
            total += col_weight * strength
        importance[idx] = total
    return importance


def calculate_relative(importance):
    """Convert absolute importance to relative percentages."""
    total = sum(importance.values())
    if total == 0:
        return {k: 0.0 for k in importance.keys()}
    return {k: (v / total) * 100 for k, v in importance.items()}


def map_codes_to_keys(codes, keys, prefix):
    """Map codes (N00, F01, etc.) to entity keys."""
    mapping = {}
    for i, key in enumerate(keys):
        code = f"{prefix}{i:02d}"
        mapping[code] = key
    return mapping


def map_keys_to_relative(keys, code_relative, code_to_key):
    """Map entity keys to relative scores via codes."""
    result = {}
    for key in keys:
        # Find the code for this key
        code = None
        for c, k in code_to_key.items():
            if k == key:
                code = c
                break
        if code:
            result[key] = code_relative.get(code, 0.0)
        else:
            result[key] = 0.0
    return result


def calculate_step_001(data):
    """Calculate importance scores directly from matrices (step 001)."""
    problems = data.get("problems", {})
    needs = data.get("needs", {})
    features = data.get("features", {})

    problem_keys = list(problems.keys())
    need_keys = list(needs.keys())
    feature_keys = list(features.keys())

    # Load matrices
    df_p2n = load_csv(PROBLEMS_TO_NEEDS_CSV, "PROBLEM")
    df_n2f = load_csv(NEEDS_TO_FEATURES_CSV, "NEED")
    df_f2p = load_csv(FEATURES_TO_PROBLEMS_CSV, "FEATURE")

    # Initialize accumulators
    problem_scores = {k: 0 for k in problem_keys}
    need_scores = {k: 0 for k in need_keys}
    feature_scores = {k: 0 for k in feature_keys}

    # Problems-to-Needs matrix
    # Problem importance: row sums
    p_row_imp = calculate_row_importance(df_p2n)
    for prob_key, score in p_row_imp.items():
        problem_scores[prob_key] += score

    # Need importance: column sums
    # Columns are coded (N00, N01, etc), need to map back to keys
    n_col_imp = calculate_column_importance(df_p2n)
    code_to_need = map_codes_to_keys(n_col_imp.keys(), need_keys, "N")
    for code, score in n_col_imp.items():
        need_key = code_to_need[code]
        need_scores[need_key] += score

    # Needs-to-Features matrix
    # Need importance: row sums
    n_row_imp = calculate_row_importance(df_n2f)
    for need_key, score in n_row_imp.items():
        need_scores[need_key] += score

    # Feature importance: column sums
    f_col_imp = calculate_column_importance(df_n2f)
    code_to_feature = map_codes_to_keys(f_col_imp.keys(), feature_keys, "F")
    for code, score in f_col_imp.items():
        feature_key = code_to_feature[code]
        feature_scores[feature_key] += score

    # Features-to-Problems matrix
    # Feature importance: row sums
    f_row_imp = calculate_row_importance(df_f2p)
    for feature_key, score in f_row_imp.items():
        feature_scores[feature_key] += score

    # Problem importance: column sums
    p_col_imp = calculate_column_importance(df_f2p)
    code_to_problem = map_codes_to_keys(p_col_imp.keys(), problem_keys, "P")
    for code, score in p_col_imp.items():
        problem_key = code_to_problem[code]
        problem_scores[problem_key] += score

    # Calculate relative percentages
    problem_relative = calculate_relative(problem_scores)
    need_relative = calculate_relative(need_scores)
    feature_relative = calculate_relative(feature_scores)

    return {
        "problems": problem_relative,
        "needs": need_relative,
        "features": feature_relative
    }


def load_step_file(step_num):
    """Load a previous step file."""
    step_file = SCRIPT_DIR / f"{step_num:03d}.step"
    with open(step_file, "r") as f:
        return yaml.safe_load(f)


def calculate_step_n(data, prev_step_num):
    """Calculate importance scores using previous step as weights."""
    problems = data.get("problems", {})
    needs = data.get("needs", {})
    features = data.get("features", {})

    problem_keys = list(problems.keys())
    need_keys = list(needs.keys())
    feature_keys = list(features.keys())

    # Load previous step scores
    prev_scores = load_step_file(prev_step_num)
    prev_problems = prev_scores.get("problems", {})
    prev_needs = prev_scores.get("needs", {})
    prev_features = prev_scores.get("features", {})

    # Load matrices
    df_p2n = load_csv(PROBLEMS_TO_NEEDS_CSV, "PROBLEM")
    df_n2f = load_csv(NEEDS_TO_FEATURES_CSV, "NEED")
    df_f2p = load_csv(FEATURES_TO_PROBLEMS_CSV, "FEATURE")

    # Initialize accumulators
    problem_scores = {k: 0.0 for k in problem_keys}
    need_scores = {k: 0.0 for k in need_keys}
    feature_scores = {k: 0.0 for k in feature_keys}

    # Problems-to-Needs matrix
    # Weighted column importance for needs (using problem weights from prev step)
    n_col_imp_weighted = calculate_weighted_column_importance(df_p2n, prev_problems)
    code_to_need = map_codes_to_keys(n_col_imp_weighted.keys(), need_keys, "N")
    for code, score in n_col_imp_weighted.items():
        need_key = code_to_need[code]
        need_scores[need_key] += score

    # Weighted row importance for problems (using need weights from prev step)
    # Map need codes back for weighting
    need_code_weights = {}
    for i, need_key in enumerate(need_keys):
        code = f"N{i:02d}"
        need_code_weights[code] = prev_needs.get(need_key, 0.0)
    p_row_imp_weighted = calculate_weighted_row_importance(df_p2n, need_code_weights)
    for prob_key, score in p_row_imp_weighted.items():
        problem_scores[prob_key] += score

    # Needs-to-Features matrix
    # Weighted column importance for features (using need weights from prev step)
    f_col_imp_weighted = calculate_weighted_column_importance(df_n2f, prev_needs)
    code_to_feature = map_codes_to_keys(f_col_imp_weighted.keys(), feature_keys, "F")
    for code, score in f_col_imp_weighted.items():
        feature_key = code_to_feature[code]
        feature_scores[feature_key] += score

    # Weighted row importance for needs (using feature weights from prev step)
    feature_code_weights = {}
    for i, feature_key in enumerate(feature_keys):
        code = f"F{i:02d}"
        feature_code_weights[code] = prev_features.get(feature_key, 0.0)
    n_row_imp_weighted = calculate_weighted_row_importance(df_n2f, feature_code_weights)
    for need_key, score in n_row_imp_weighted.items():
        need_scores[need_key] += score

    # Features-to-Problems matrix
    # Weighted column importance for problems (using feature weights from prev step)
    p_col_imp_weighted = calculate_weighted_column_importance(df_f2p, prev_features)
    code_to_problem = map_codes_to_keys(p_col_imp_weighted.keys(), problem_keys, "P")
    for code, score in p_col_imp_weighted.items():
        problem_key = code_to_problem[code]
        problem_scores[problem_key] += score

    # Weighted row importance for features (using problem weights from prev step)
    problem_code_weights = {}
    for i, problem_key in enumerate(problem_keys):
        code = f"P{i:02d}"
        problem_code_weights[code] = prev_problems.get(problem_key, 0.0)
    f_row_imp_weighted = calculate_weighted_row_importance(df_f2p, problem_code_weights)
    for feature_key, score in f_row_imp_weighted.items():
        feature_scores[feature_key] += score

    # Calculate relative percentages
    problem_relative = calculate_relative(problem_scores)
    need_relative = calculate_relative(need_scores)
    feature_relative = calculate_relative(feature_scores)

    return {
        "problems": problem_relative,
        "needs": need_relative,
        "features": feature_relative
    }


def save_step_file(step_num, scores):
    """Save scores to a step file in YAML format."""
    step_file = SCRIPT_DIR / f"{step_num:03d}.step"

    output = {
        "step": step_num,
        "description": f"Relative importance scores for step {step_num}",
        "problems": scores["problems"],
        "needs": scores["needs"],
        "features": scores["features"]
    }

    with open(step_file, "w") as f:
        yaml.dump(output, f, default_flow_style=False, sort_keys=False)

    print(f"✓ Saved {step_file.name}")
    return step_file


def print_summary(step_num, scores):
    """Print a summary of the scores."""
    print()
    print("=" * 80)
    print(f"Step {step_num:03d} Summary")
    print("=" * 80)
    print()

    print("TOP 5 PROBLEMS:")
    top_problems = sorted(scores["problems"].items(), key=lambda x: x[1], reverse=True)[:5]
    for key, score in top_problems:
        print(f"  {key:40s} {score:6.2f}%")

    print()
    print("TOP 5 NEEDS:")
    top_needs = sorted(scores["needs"].items(), key=lambda x: x[1], reverse=True)[:5]
    for key, score in top_needs:
        print(f"  {key:40s} {score:6.2f}%")

    print()
    print("TOP 5 FEATURES:")
    top_features = sorted(scores["features"].items(), key=lambda x: x[1], reverse=True)[:5]
    for key, score in top_features:
        print(f"  {key:40s} {score:6.2f}%")

    print()


def main():
    if len(sys.argv) != 2:
        print("Usage: python step.py <step_number>")
        print("Example: python step.py 001")
        sys.exit(1)

    try:
        step_num = int(sys.argv[1])
    except ValueError:
        print("Error: Step number must be an integer")
        sys.exit(1)

    if step_num < 1:
        print("Error: Step number must be >= 1")
        sys.exit(1)

    print(f"Calculating step {step_num:03d}...")
    print()

    # Load YAML data
    data = load_yaml()

    # Calculate scores
    if step_num == 1:
        scores = calculate_step_001(data)
    else:
        prev_step_num = step_num - 1
        prev_step_file = SCRIPT_DIR / f"{prev_step_num:03d}.step"
        if not prev_step_file.exists():
            print(f"Error: Previous step file {prev_step_file.name} not found.")
            print(f"Please run step {prev_step_num:03d} first.")
            sys.exit(1)
        scores = calculate_step_n(data, prev_step_num)

    # Save to file
    step_file = save_step_file(step_num, scores)

    # Print summary
    print_summary(step_num, scores)


if __name__ == "__main__":
    main()
