# Product Planning Alignment Example: Coffee Shop Chain Expansion

A complete working example of QFD (Quality Function Deployment) inspired planning framework applied to a coffee shop chain expansion strategy.

## What This System Does

This framework helps you discover **emergent priorities** through network analysis of how problems, needs, and solutions interconnect. Unlike simple ranking or voting, it reveals which features deserve investment by analyzing the **entire relationship network**.

### The Core Concept

```
Problems → Needs → Features
```

- **Problems**: Customer pain points or business challenges
- **Needs**: Requirements that would address those problems
- **Features**: Concrete implementations/investments that satisfy needs

The system uses **iterative refinement** to calculate importance scores that flow through the network, revealing which features have the highest strategic value.

## The Coffee Shop Example

This example demonstrates planning for an urban coffee shop chain deciding how to prioritize expansion investments:

**Problems**: Morning rush chaos, remote worker needs, inconsistent quality, neighborhood disconnect, food quality issues

**Needs**: Reduce wait times, predictable seating, consistent training, local identity, expanded food program, workspace amenities, etc.

**Features**: Mobile ordering, seating API, barista certification, local artist program, kitchen retrofits, coworking memberships, etc.

## Quick Start

### 1. Generate the Matrices

```bash
./generate_planning_matrix.py
```

This creates three CSV files:
- `problems-to-needs.csv` - Problems (rows) × Needs (columns)
- `product-planning.csv` - Needs (rows) × Features (columns)
- `features-to-problems.csv` - Features (rows) × Problems (columns)

Each CSV has headers explaining what each column code means (N00, N01, etc.)

### 2. Score the Relationships

Open each CSV file and replace the `~` with scores representing relationship strength:

- **5** = Strong relationship (feature directly solves need, need directly addresses problem)
- **3** = Medium relationship (partial or indirect connection)
- **1** = Weak relationship (tangential connection)
- **~** = No relationship or unknown

**Tip**: Start with problems-to-needs.csv, as that's usually most intuitive.

### 3. Calculate Priorities

Run iterative steps to calculate importance scores:

```bash
./step.py 1    # Initial calculation from raw scores
./step.py 2    # First refinement using step 1 as weights
./step.py 3    # Second refinement
# ... continue as desired
./step.py 10   # Typically converges by step 5-10
```

Each step produces a `.step` file (e.g., `001.step`, `002.step`) with relative importance percentages.

### 4. Review Results

Each step output shows the top 5 items in each category:

```
Step 001 Summary
================

TOP 5 PROBLEMS:
  morning-rush-chaos                        32.15%
  remote-worker-homeless                    28.40%
  inconsistent-experience                   21.33%
  ...

TOP 5 NEEDS:
  reduce-wait-times                         12.45%
  mobile-convenience                        11.22%
  predictable-seating                       10.87%
  ...

TOP 5 FEATURES:
  mobile-order-ahead                        18.76%
  seating-availability-api                  15.43%
  barista-certification                     12.91%
  ...
```

### 5. Generate Investment Justification Report

Get actionable recommendations with full justification:

```bash
./report_top_todo.py 5    # Report on top 5 features (default)
./report_top_todo.py 3    # Report on top 3 features
```

This generates an **executive summary** plus **detailed justification** for each top feature, showing:
- Strategic importance percentage
- Which problems it directly addresses
- Which needs it satisfies (with relationship strength)
- For each need, which problems drive it
- All weighted by network-calculated importance

**Example output:**
```
FEATURE: neighborhood-manager-role (13.72%)
  DIRECTLY ADDRESSES PROBLEMS:
    ●●●●● Neighborhood Disconnect (25.65% importance)
    ●○○○○ Inconsistent Experience (23.82% importance)

  SATISFIES NEEDS:
    ●●●●● brand-differentiation (15.33% importance)
      → Which addresses problems:
         ●●●○○ Neighborhood Disconnect (25.6%)
         ●●●○○ Inconsistent Experience (23.8%)
```

This report provides **complete strategic justification** for investment decisions - perfect for stakeholder presentations!

## Understanding the Results

### Why Iterative Refinement?

**Step 1**: Simple sums - a feature scores high if it touches many needs

**Steps 2+**: Weighted sums - features that address *important* needs score higher

This reveals **network effects**: A feature like "neighborhood-manager-role" might not touch many needs, but if it strongly addresses several high-priority needs, it will rise in importance through iterations.

### What to Look For

1. **Convergence**: Scores typically stabilize after 5-10 iterations
2. **Surprises**: Features you expected to be low-priority might emerge as critical
3. **Justification**: High scores show *why* something is important (trace back through needs to problems)
4. **Trade-offs**: Similar scores mean features are roughly equivalent in strategic value

## Customizing for Your Use Case

### 1. Edit product-planning.yaml

```yaml
problems:
  your-problem-key:
    title: Short Title
    description: Detailed description of the problem

needs:
  your-need-key:
    description: What capability is needed

features:
  your-feature-key:
    description: Concrete implementation or solution
```

### 2. Regenerate and Score

```bash
./generate_planning_matrix.py  # Creates new matrices preserving old scores
# Edit CSVs
./step.py 1                    # Calculate
```

The generator **preserves existing scores** when you add new items, so you can evolve your planning over time.

## Example Workflow: Making a Strategic Decision

**Question**: Should we invest in kitchen retrofits or focus on mobile tech?

1. Look at the latest step file (e.g., `010.step`)
2. Find the features:
   - `kitchen-retrofit: 14.2%`
   - `mobile-order-ahead: 18.8%`
   - `seating-availability-api: 15.4%`

3. Trace back why:
   - Kitchen retrofit addresses `expanded-food-program` need (medium priority)
   - Mobile-order-ahead addresses `reduce-wait-times` + `mobile-convenience` (both high priority)
   - Seating API addresses `predictable-seating` (high priority, unique to remote-worker problem)

4. Decision: Mobile tech has higher strategic value, but kitchen retrofit might be worth it if you can find a cheaper way to address `expanded-food-program`

## Tips for Effective Use

### Scoring Guidelines

- **Be honest**: Don't inflate scores for pet projects
- **Be consistent**: Use the same mental model for 5/3/1 across all matrices
- **Be conservative**: When in doubt, use a lower score
- **Iterate**: Your first scoring won't be perfect - revise as you learn

### Common Patterns

1. **High-leverage features**: Touch multiple high-priority needs
2. **Gateway needs**: Needs that many features depend on
3. **Orphaned problems**: Problems with no strong need connections (add more needs!)
4. **Over-engineered features**: Features that don't strongly connect to any need

### When to Use This System

- **Strategic planning**: Prioritizing roadmap items
- **Investment decisions**: Which initiatives deserve budget
- **Stakeholder alignment**: Objective framework for debates
- **Opportunity evaluation**: Should we pursue this new idea?

### When NOT to Use This

- **Urgent bugs**: Just fix them
- **Compliance requirements**: No choice, must do
- **Simple decisions**: Overkill for obvious priorities
- **Political decisions**: If outcomes are predetermined, don't pretend to analyze

## Files in This Directory

- `product-planning.yaml` - Source of truth for all problems, needs, and features
- `generate_planning_matrix.py` - Generates CSV matrices from YAML
- `step.py` - Calculates iterative importance scores
- `report_top_todo.py` - Generates investment justification reports for top features
- `plot_steps.py` - Visualizes score evolution across iterations
- `problems-to-needs.csv` - Matrix showing which needs address which problems
- `product-planning.csv` - Matrix showing which features satisfy which needs
- `features-to-problems.csv` - Matrix showing direct feature-to-problem relationships
- `*.step` - Calculated importance scores for each iteration

## Understanding the Three-Matrix Approach

Traditional QFD uses a two-matrix approach (Problems → Needs → Features). This system adds a third matrix (Features → Problems) to create a **feedback loop**:

```
Problems ←──────────────┐
   ↓                    │
 Needs                  │
   ↓                    │
Features ───────────────┘
```

This captures cases where:
- Features directly address problems (bypassing formal needs)
- Features create new problems or reveal hidden ones
- Strategic importance flows in both directions

The iterative refinement process propagates importance through all three relationships, revealing the true strategic value of each element.

## Further Reading

- [House of Quality (QFD)](https://en.wikipedia.org/wiki/Quality_function_deployment)
- [Design Structure Matrix](https://en.wikipedia.org/wiki/Design_structure_matrix)
- [Network Centrality](https://en.wikipedia.org/wiki/Centrality) - Similar concepts in graph theory

## Adapting This Example

Want to use this for your own domain? Here are some successful adaptations:

- **Software Platform**: Problems (user pain) → Needs (capabilities) → Features (implementations)
- **Medical Device**: Problems (clinical needs) → Needs (technical requirements) → Features (components)
- **Education Curriculum**: Problems (learning gaps) → Needs (competencies) → Features (courses/modules)
- **Supply Chain**: Problems (inefficiencies) → Needs (operational improvements) → Features (initiatives)

The framework is domain-agnostic as long as you have a three-level hierarchy of challenge → requirement → solution.
