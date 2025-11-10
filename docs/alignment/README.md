# Product Planning Alignment

QFD/House of Quality inspired planning workflow for mapping problems → needs → features.

## Workflow

1. **Edit** `product-planning.yaml` - Define problems, needs, and features
2. **Generate** matrices - Run `./generate_planning_matrix.py` to create/update CSVs
3. **Score** relationships - Edit CSVs to score interactions (5=strong, 3=medium, 1=weak, ~=none)
4. **Analyze** priorities - Run `./report.py` to see weighted importance scores

## Files

- `product-planning.yaml` - Source of truth for all items
- `problems-to-needs.csv` - Matrix: Problems (rows) × Needs (columns)
- `product-planning.csv` - Matrix: Needs (rows) × Features (columns)
- `generate_planning_matrix.py` - Generates/updates matrices from YAML
- `report.py` - Calculates and displays priority rankings

## Example

```bash
# After updating YAML
./generate_planning_matrix.py

# Edit CSVs to score relationships
vim problems-to-needs.csv product-planning.csv

# View priorities
./report.py
```

The generator preserves existing scores when regenerating matrices.
