#!/usr/bin/env python3
"""Generate actionable report for top features with backward justification.

This script takes the top N features from the latest step file and works
backwards through the matrices to explain:
- Which needs each feature satisfies (and their importance)
- Which problems those needs address (and their importance)

This provides strategic justification for feature investment decisions.
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


def find_latest_step():
    """Find the highest numbered step file."""
    step_files = list(SCRIPT_DIR.glob("*.step"))
    if not step_files:
        return None

    step_numbers = []
    for f in step_files:
        try:
            num = int(f.stem)
            step_numbers.append((num, f))
        except ValueError:
            continue

    if not step_numbers:
        return None

    step_numbers.sort(reverse=True)
    return step_numbers[0]


def load_step_file(step_file):
    """Load a step file."""
    with open(step_file, "r") as f:
        return yaml.safe_load(f)


def get_top_features(step_data, n=5):
    """Get top N features by importance score."""
    features = step_data.get("features", {})
    sorted_features = sorted(features.items(), key=lambda x: x[1], reverse=True)
    return sorted_features[:n]


def map_codes_to_keys(codes, keys, prefix):
    """Map codes (N00, F01, etc.) to entity keys."""
    mapping = {}
    for i, key in enumerate(keys):
        code = f"{prefix}{i:02d}"
        mapping[code] = key
    return mapping


def analyze_feature_justification(feature_key, step_data, yaml_data,
                                   df_n2f, df_p2n, df_f2p,
                                   need_keys, problem_keys):
    """Analyze why a feature is important by tracing backwards through needs to problems."""

    feature_score = step_data["features"].get(feature_key, 0)
    need_scores = step_data["needs"]
    problem_scores = step_data["problems"]

    # Create mappings
    code_to_need = map_codes_to_keys(df_n2f.columns, need_keys, "N")
    code_to_problem = map_codes_to_keys(df_p2n.columns, need_keys, "N")

    # Find which needs this feature satisfies
    needs_satisfied = []
    for need_key in need_keys:
        # Find the row in needs-to-features matrix
        if need_key not in df_n2f.index:
            continue

        # Find the column for this feature (need to map feature_key to column code)
        feature_cols = [col for col, key in
                       map_codes_to_keys(df_n2f.columns,
                                       list(yaml_data["features"].keys()), "F").items()
                       if key == feature_key]

        if not feature_cols:
            continue

        feature_col = feature_cols[0]
        strength = parse_value(df_n2f.loc[need_key, feature_col])

        if strength > 0:
            need_importance = need_scores.get(need_key, 0)
            weighted_contribution = strength * need_importance
            needs_satisfied.append({
                "key": need_key,
                "strength": strength,
                "importance": need_importance,
                "contribution": weighted_contribution
            })

    # Sort needs by weighted contribution
    needs_satisfied.sort(key=lambda x: x["contribution"], reverse=True)

    # For each important need, find which problems it addresses
    needs_with_problems = []
    for need_info in needs_satisfied:
        need_key = need_info["key"]

        # Find which problems drive this need
        problems_addressed = []

        # Find the column for this need in problems-to-needs matrix
        need_cols = [col for col, key in code_to_need.items() if key == need_key]

        if need_cols:
            need_col = need_cols[0]

            for problem_key in problem_keys:
                if problem_key not in df_p2n.index:
                    continue

                strength = parse_value(df_p2n.loc[problem_key, need_col])

                if strength > 0:
                    problem_importance = problem_scores.get(problem_key, 0)
                    weighted_contribution = strength * problem_importance
                    problems_addressed.append({
                        "key": problem_key,
                        "strength": strength,
                        "importance": problem_importance,
                        "contribution": weighted_contribution
                    })

        # Sort problems by weighted contribution
        problems_addressed.sort(key=lambda x: x["contribution"], reverse=True)

        need_info["problems"] = problems_addressed
        needs_with_problems.append(need_info)

    # Also check direct feature-to-problem relationships
    direct_problems = []
    problem_cols = [col for col, key in
                   map_codes_to_keys(df_f2p.columns, problem_keys, "P").items()
                   if key in problem_keys]

    if feature_key in df_f2p.index:
        for problem_key in problem_keys:
            # Find column for this problem
            prob_cols = [col for col, key in
                        map_codes_to_keys(df_f2p.columns, problem_keys, "P").items()
                        if key == problem_key]

            if prob_cols:
                prob_col = prob_cols[0]
                strength = parse_value(df_f2p.loc[feature_key, prob_col])

                if strength > 0:
                    problem_importance = problem_scores.get(problem_key, 0)
                    weighted_contribution = strength * problem_importance
                    direct_problems.append({
                        "key": problem_key,
                        "strength": strength,
                        "importance": problem_importance,
                        "contribution": weighted_contribution
                    })

    direct_problems.sort(key=lambda x: x["contribution"], reverse=True)

    return {
        "feature_key": feature_key,
        "feature_score": feature_score,
        "needs": needs_with_problems,
        "direct_problems": direct_problems
    }


def format_strength(strength):
    """Format relationship strength as indicator."""
    if strength == 5:
        return "●●●●●"
    elif strength == 3:
        return "●●●○○"
    elif strength == 1:
        return "●○○○○"
    return "○○○○○"


def print_feature_report(analysis, yaml_data):
    """Print a formatted report for a single feature."""
    feature_key = analysis["feature_key"]
    feature_info = yaml_data["features"][feature_key]

    print()
    print("=" * 80)
    print(f"FEATURE: {feature_key}")
    print("=" * 80)
    print(f"Description: {feature_info['description']}")
    print(f"Strategic Importance: {analysis['feature_score']:.2f}%")
    print()

    # Direct problem relationships
    if analysis["direct_problems"]:
        print("DIRECTLY ADDRESSES PROBLEMS:")
        print("-" * 80)
        for prob in analysis["direct_problems"][:5]:  # Top 5
            prob_info = yaml_data["problems"][prob["key"]]
            print(f"  {format_strength(prob['strength'])} {prob_info['title']}")
            print(f"      Problem Importance: {prob['importance']:.2f}%")
            print(f"      Weighted Impact: {prob['contribution']:.2f}")
            print()

    # Needs satisfied
    print("SATISFIES NEEDS:")
    print("-" * 80)
    for need in analysis["needs"][:5]:  # Top 5 needs
        need_info = yaml_data["needs"][need["key"]]
        print(f"  {format_strength(need['strength'])} {need['key']}")
        print(f"      {need_info['description']}")
        print(f"      Need Importance: {need['importance']:.2f}%")
        print(f"      Weighted Impact: {need['contribution']:.2f}")

        # Show which problems drive this need
        if need["problems"]:
            print(f"      → Which addresses problems:")
            for prob in need["problems"][:3]:  # Top 3 problems per need
                prob_info = yaml_data["problems"][prob["key"]]
                print(f"         {format_strength(prob['strength'])} {prob_info['title']} "
                      f"({prob['importance']:.1f}%)")
        print()


def print_executive_summary(analyses, yaml_data):
    """Print executive summary of all top features."""
    print()
    print("=" * 80)
    print("EXECUTIVE SUMMARY: TOP PRIORITY FEATURES")
    print("=" * 80)
    print()

    for i, analysis in enumerate(analyses, 1):
        feature_key = analysis["feature_key"]
        feature_info = yaml_data["features"][feature_key]

        # Collect all unique problems (direct + via needs)
        all_problems = {}

        for prob in analysis["direct_problems"]:
            prob_key = prob["key"]
            if prob_key not in all_problems:
                all_problems[prob_key] = prob["importance"]

        for need in analysis["needs"]:
            for prob in need["problems"]:
                prob_key = prob["key"]
                if prob_key not in all_problems:
                    all_problems[prob_key] = prob["importance"]

        top_problems = sorted(all_problems.items(), key=lambda x: x[1], reverse=True)[:3]
        problem_names = [yaml_data["problems"][k]["title"] for k, _ in top_problems]

        print(f"{i}. {feature_key} ({analysis['feature_score']:.2f}%)")
        print(f"   {feature_info['description']}")
        print(f"   → Addresses: {', '.join(problem_names)}")
        print()


def main():
    # Parse arguments
    top_n = 5
    if len(sys.argv) > 1:
        try:
            top_n = int(sys.argv[1])
        except ValueError:
            print(f"Usage: {sys.argv[0]} [num_features]")
            print(f"Example: {sys.argv[0]} 5")
            sys.exit(1)

    # Find latest step file
    step_info = find_latest_step()
    if not step_info:
        print("Error: No step files found. Please run ./step.py first.")
        sys.exit(1)

    step_num, step_file = step_info
    print(f"Using step file: {step_file.name} (step {step_num})")

    # Load data
    yaml_data = load_yaml()
    step_data = load_step_file(step_file)

    problem_keys = list(yaml_data["problems"].keys())
    need_keys = list(yaml_data["needs"].keys())
    feature_keys = list(yaml_data["features"].keys())

    df_p2n = load_csv(PROBLEMS_TO_NEEDS_CSV, "PROBLEM")
    df_n2f = load_csv(NEEDS_TO_FEATURES_CSV, "NEED")
    df_f2p = load_csv(FEATURES_TO_PROBLEMS_CSV, "FEATURE")

    # Get top features
    top_features = get_top_features(step_data, top_n)

    # Analyze each feature
    analyses = []
    for feature_key, score in top_features:
        analysis = analyze_feature_justification(
            feature_key, step_data, yaml_data,
            df_n2f, df_p2n, df_f2p,
            need_keys, problem_keys
        )
        analyses.append(analysis)

    # Print executive summary
    print_executive_summary(analyses, yaml_data)

    # Print detailed reports
    print()
    print("=" * 80)
    print("DETAILED JUSTIFICATION REPORTS")
    print("=" * 80)

    for analysis in analyses:
        print_feature_report(analysis, yaml_data)


if __name__ == "__main__":
    main()
