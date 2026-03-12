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
      generators/
        __init__.py
        commands.py             ← render_scaffold_commands, render_gen_commands + writers
    tests/
      conftest.py               ← recipe_feat fixture
      fixtures/
        recipe.feat.yaml
      snapshots/                ← unused; syrupy places snapshots co-located with test files
      generators/
        __snapshots__/          ← syrupy snapshot files (committed)
          test_commands.ambr
        test_commands.py        ← complete
        test_events.py
        test_queries.py
        test_procedures.py
        test_policies.py
        test_projections.py
        test_models.py
      test_cli.py               ← stub
```

## Coding standards

- All functions and test functions must have full type annotations, including `-> None` return types.
- Test parameters (fixtures, `tmp_path`, etc.) must be typed — e.g. `tmp_path: Path`, `recipe_feat: FeatureDefinition`.

## Snapshot testing

Phase 3 snapshot tests live in `tests/generators/test_<section>.py` alongside the unit tests for each generator. Syrupy stores snapshots in `tests/generators/__snapshots__/<test_file>.ambr`, co-located with the test file (not in the top-level `tests/snapshots/` directory). They assert on rendered output using `assert result == snapshot` and are run/updated with:

```
just test-update
```

These tests operate directly on `render_*` / `write_*` functions and are **independent of the CLI** (Phase 4). The CLI's end-to-end snapshot in `tests/test_cli.py` is a separate, additional layer added in Phase 4.

## Stale / ignore

- `dizzy/src/feature_model.py` — old LinkML-generated model, predates the full schema. Does not include models, queries, or projections. **Do not extend; use `feat.py` instead.**
- `dizzy/src/feature_schema.yaml` — the old schema that generated the above.
- `dizzy/cli.py` and `dizzy/__pycache__/` at repo root — stale artefacts, not the real CLI.

## Test Execution

Always run tests via the `justfile` — never call `uv run pytest` directly.

- `just test` — run the full test suite
- `just test-update` — run tests and update syrupy snapshots