#!/usr/bin/env python3
"""Plot the evolution of importance scores across step files.

This script reads all .step files in the directory and creates terminal-based
line charts showing how Problems, Needs, and Features evolve over iterations.
"""

import plotext as plt
import yaml
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).parent


def find_step_files():
    """Find all .step files in the directory and return sorted by step number."""
    step_files = list(SCRIPT_DIR.glob("*.step"))
    # Sort by step number (extracted from filename)
    step_files.sort(key=lambda f: int(f.stem))
    return step_files


def load_all_steps():
    """Load all step files and organize data by entity type."""
    step_files = find_step_files()

    if not step_files:
        print("No .step files found in directory.")
        return None

    # Data structure: {entity_type: {entity_name: [scores_by_step]}}
    problems_data = {}
    needs_data = {}
    features_data = {}
    step_numbers = []

    for step_file in step_files:
        with open(step_file, "r") as f:
            data = yaml.safe_load(f)

        step_num = data.get("step", int(step_file.stem))
        step_numbers.append(step_num)

        # Collect problems
        for name, score in data.get("problems", {}).items():
            if name not in problems_data:
                problems_data[name] = []
            problems_data[name].append(score)

        # Collect needs
        for name, score in data.get("needs", {}).items():
            if name not in needs_data:
                needs_data[name] = []
            needs_data[name].append(score)

        # Collect features
        for name, score in data.get("features", {}).items():
            if name not in features_data:
                features_data[name] = []
            features_data[name].append(score)

    return {
        "step_numbers": step_numbers,
        "problems": problems_data,
        "needs": needs_data,
        "features": features_data
    }


def plot_entity_type(step_numbers, entity_data, entity_type, top_n=10):
    """Plot line chart for a specific entity type (Problems, Needs, or Features)."""
    if not entity_data:
        print(f"No data for {entity_type}")
        return

    # Calculate final scores (last step) to determine top N
    final_scores = {name: scores[-1] for name, scores in entity_data.items()}
    top_entities = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

    plt.clear_figure()
    plt.title(f"{entity_type} Importance Evolution (Top {top_n})")
    plt.xlabel("Step")
    plt.ylabel("Relative Importance (%)")

    # Plot each entity
    for name, _ in top_entities:
        scores = entity_data[name]
        # Pad with zeros if entity doesn't have data for all steps
        while len(scores) < len(step_numbers):
            scores.append(0)
        plt.plot(step_numbers, scores, label=name[:30])  # Truncate long names

    plt.show()
    print()


def plot_all(data, top_n=10):
    """Plot all three entity types."""
    step_numbers = data["step_numbers"]

    print("=" * 80)
    print(f"Step Evolution Analysis ({len(step_numbers)} steps: {step_numbers[0]}-{step_numbers[-1]})")
    print("=" * 80)
    print()

    # Plot Problems
    plot_entity_type(step_numbers, data["problems"], "Problems", top_n)

    # Plot Needs
    plot_entity_type(step_numbers, data["needs"], "Needs", top_n)

    # Plot Features
    plot_entity_type(step_numbers, data["features"], "Features", top_n)


def print_convergence_summary(data):
    """Print a summary of how scores are converging."""
    step_numbers = data["step_numbers"]

    if len(step_numbers) < 2:
        print("Need at least 2 steps to analyze convergence.")
        return

    print("=" * 80)
    print("Convergence Summary (Change from First to Last Step)")
    print("=" * 80)
    print()

    def analyze_category(entity_data, category_name):
        changes = {}
        for name, scores in entity_data.items():
            if len(scores) >= 2 and scores[0] > 0:  # Only analyze entities with data
                change = scores[-1] - scores[0]
                pct_change = (change / scores[0]) * 100 if scores[0] != 0 else 0
                changes[name] = (scores[0], scores[-1], change, pct_change)

        if not changes:
            return

        print(f"{category_name}:")
        print(f"{'Name':<40} {'Initial':>8} {'Final':>8} {'Change':>8} {'% Change':>10}")
        print("-" * 80)

        # Sort by absolute change (descending)
        sorted_changes = sorted(changes.items(), key=lambda x: abs(x[1][2]), reverse=True)[:10]

        for name, (initial, final, change, pct_change) in sorted_changes:
            arrow = "↑" if change > 0 else "↓" if change < 0 else "→"
            print(f"{name[:38]:<40} {initial:>8.2f} {final:>8.2f} {change:>7.2f}{arrow} {pct_change:>9.1f}%")

        print()

    analyze_category(data["problems"], "PROBLEMS")
    analyze_category(data["needs"], "NEEDS")
    analyze_category(data["features"], "FEATURES")


def main():
    # Optional: specify number of top items to show
    top_n = 10
    if len(sys.argv) > 1:
        try:
            top_n = int(sys.argv[1])
        except ValueError:
            print(f"Invalid top_n value: {sys.argv[1]}, using default of 10")

    # Load all step data
    data = load_all_steps()

    if not data:
        sys.exit(1)

    # Plot evolution charts
    plot_all(data, top_n)

    # Print convergence summary
    print_convergence_summary(data)


if __name__ == "__main__":
    main()
