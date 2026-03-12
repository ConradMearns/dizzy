# Codebase Context

## Current file layout

```
dizzy/                          ← repo root
  SPECIFICATION.md
  PLAN.md
  PROMPT.md
  example.feat.yaml
  dizzy/                        ← Python package
    pyproject.toml
    src/dizzy/
      __init__.py
      cli.py                    ← typer skeleton, scaffold + gen not yet wired
      feat.py                   ← FeatureDefinition dataclasses + load_feat()
      def/
        feat.yaml               ← LinkML meta-schema (reference only)
      generators/               ← does not exist yet (Phase 3)
    tests/
      conftest.py               ← recipe_feat fixture
      fixtures/
        recipe.feat.yaml
      snapshots/                ← empty; populated on first --snapshot-update
      generators/
        test_commands.py        ← stub (no tests yet)
        test_events.py
        test_queries.py
        test_procedures.py
        test_policies.py
        test_projections.py
        test_models.py
      test_cli.py               ← stub
```

## Stale / ignore

- `dizzy/src/feature_model.py` — old LinkML-generated model, predates the full schema. Does not include models, queries, or projections. **Do not extend; use `feat.py` instead.**
- `dizzy/src/feature_schema.yaml` — the old schema that generated the above.
- `dizzy/cli.py` and `dizzy/__pycache__/` at repo root — stale artefacts, not the real CLI.