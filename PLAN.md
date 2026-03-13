# Dizzy Generator — Plan

## Phase 1 — Remove Legacy Scripts

- [x] Delete `generate_linkml_from_feature.py` from repo root
- [x] Delete `generate_protocols_from_commands.py` from repo root

---

## Phase 2 — Consolidate Root pyproject.toml

- [x] Delete `/home/conrad/dizzy/pyproject.toml` (root workspace wrapper)
- [x] Move `dizzy/pyproject.toml` up to repo root (or verify it already works as the root)
- [x] Remove `[tool.uv.workspace]` section; confirm `uv` commands still work from repo root

---

## Phase 3 — Support Partial Feats

**Bug:** `uv run dizzy def recipe.feat.yaml recipe` crashes with `KeyError: 'model'` when a query
omits the `model` field (valid in a partial feat that declares no `models` section).

### feat.py

- [x] Make `model` optional (`str | None`, default `None`) on `QueryDef`
- [x] Update `_parse_query_def` to use `raw.get("model")` instead of `raw["model"]`

### generators/queries.py

- [x] In `render_gen_query_protocol`: if `query.model` is `None`, omit the SQLAlchemy session
  field from the context dataclass (generate `pass` body instead)

### Tests

- [x] Add fixture `partial.feat.yaml` — commands + queries + procedures, no models/events/policies/projections
- [x] `test_queries.py`: assert `render_gen_query_protocol` with `model=None` omits session field
- [x] `test_cli.py`: `test_def_partial_feat` — `def_cmd` on partial feat does not crash and
  produces only the expected stubs

---

## Phase 4 — Feature Definition Validation

Implement cross-reference validation before any code generation (spec §8.3).

### feat.py (or new validators.py)

- [ ] `validate_feat(feat: FeatureDefinition) -> list[str]` — returns list of error strings:
  - All `command` refs in procedures exist in `commands`
  - All `event` refs in policies and projections exist in `events`
  - All `model` refs in queries (when set) exist in `models`
  - All `models` refs in projections exist in `models`
  - All `queries` refs in procedures exist in `queries`
  - All `emits` refs in procedures exist in `events`
  - All `emits` refs in policies exist in `commands`
- [ ] Call `validate_feat` in both `def_cmd` and `gen`; print errors and exit non-zero if any

### Tests

- [ ] `test_validation.py`:
  - Valid full feat → no errors
  - Valid partial feat → no errors
  - Procedure references unknown command → error
  - Procedure references unknown query → error
  - Procedure emits unknown event → error
  - Policy references unknown event → error
  - Policy emits unknown command → error
  - Projection references unknown event → error
  - Projection references unknown model → error
  - Query references unknown model → error

---

## Phase 5 — Snapshot Tests (syrupy)

End-to-end tests comparing every generated file against committed snapshots.

### Tests

- [ ] `test_cli.py`: `test_gen_full_example_snapshot` — run full pipeline on `recipe.feat.yaml`,
  compare every file under `tmp_path` against syrupy snapshots
- [ ] Commit initial snapshots: `pytest --snapshot-update`
- [ ] Confirm re-running `pytest` passes without `--snapshot-update`

---

## Phase 6 — Edge Case Coverage

Fill gaps in unit test coverage identified during exploration.

### test_commands.py / test_events.py

- [ ] Test commands/events declared as plain strings (no attributes map)
- [ ] Test commands/events with no entries (empty section)

### test_procedures.py

- [ ] Procedure with no `queries` — context omits `_queries` dataclass
- [ ] Procedure with no `emits` — emitters dataclass has `pass` body
- [ ] Procedure with multiple emits

### test_policies.py

- [ ] Policy with no `emits` — emitters dataclass has `pass` body
- [ ] Policy with multiple emits

### test_projections.py

- [ ] Projection writing to multiple models — context has multiple session fields

### test_queries.py

- [ ] Query with `model=None` (see Phase 3)

### test_cli.py

- [x] Fix Typer/Click exception mismatch: `typer.Exit` is `click.exceptions.Exit` — tests
  correctly catch `click.exceptions.Exit`, no change needed
