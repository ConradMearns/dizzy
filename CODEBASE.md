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

## Generator cookbook

Each generator module in `generators/` follows the same pattern. When adding a new one:

### Render/write split

Every section exposes pure `render_*` functions (return `str`, no filesystem access) and thin `write_*` wrappers (call `render_*`, write to the correct path). Tests call `render_*` directly — fast, no tmp_path needed.

### Import ordering in generated files

Generated Python files follow PEP 8 import grouping:
1. `from __future__` (if needed)
2. stdlib — `dataclasses`, `typing`
3. blank line
4. local generated imports — `gen_def.pydantic.*`, `gen_int.python.*`

Omit a group entirely (including its blank line) when it has no imports. Two blank lines before each top-level class.

### Edge-case conventions

- **Optional fields** (`queries`, `emits`, `models`, `attributes`): only emit the corresponding class/block/import when the list/dict is non-empty.
- **`pass`** in a dataclass body: used when the dataclass has no fields (e.g. emitters with no `emits`).
- **Skip-if-exists**: `write_*` functions that produce user-editable files (`def/` stubs, `src/` stubs) skip writing when the file already exists. Generated files (`gen_def/`, `gen_int/`) are always overwritten.

### Test workflow for a new generator

1. Write `tests/generators/test_<section>.py` — unit tests asserting on string content, plus writer tests, plus two snapshot tests at the bottom.
2. Run `just test` — all non-snapshot tests should pass; snapshot tests fail with "does not exist".
3. Run `just test-update` — creates the `.ambr` snapshot files.
4. Run `just test` again — all tests pass. Commit snapshots alongside the implementation.

`just test` is the gate; `just test-update` only runs when intentionally locking in new or changed output.

## Stale / ignore

- `dizzy/src/feature_model.py` — old LinkML-generated model, predates the full schema. Does not include models, queries, or projections. **Do not extend; use `feat.py` instead.**
- `dizzy/src/feature_schema.yaml` — the old schema that generated the above.
- `dizzy/cli.py` and `dizzy/__pycache__/` at repo root — stale artefacts, not the real CLI.

## Test Execution

Always run tests via the `justfile` — never call `uv run pytest` directly.

- `just test` — run the full test suite
- `just test-update` — run tests and update syrupy snapshots