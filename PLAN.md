# Dizzy Generator — Plan

## Phase 1 — Example & Schema

- [x] Update `example.feat.yaml` to include all sections: `models`, `queries`, `commands`, `events`, `procedures`, `policies`, `projections`
- [x] Create `dizzy/src/dizzy/def/feat.yaml` — LinkML meta-schema formally defining the `.feat.yaml` format (`FeatureDefinition`, `ModelDef`, `QueryDef`, `CommandDef`, `EventDef`, `ProcedureDef`, `PolicyDef`, `ProjectionDef`)

## Phase 2 — Test Infrastructure

Set up the test harness before writing any generator code.

- [x] Add `syrupy>=4.0` to the `dev` dependency group in `dizzy/pyproject.toml`
- [x] Create `dizzy/tests/conftest.py` — shared `recipe_feat` fixture that loads `tests/fixtures/recipe.feat.yaml`
- [x] Create `dizzy/tests/fixtures/recipe.feat.yaml` — full example feat (models, queries, commands, events, procedures, policies, projections) matching the spec's full example
- [x] Create `dizzy/tests/snapshots/` directory (empty, populated when snapshots are first updated)
- [x] Create empty test files to be filled in per-generator (TDD red phase):
  - `dizzy/tests/generators/test_commands.py`
  - `dizzy/tests/generators/test_events.py`
  - `dizzy/tests/generators/test_queries.py`
  - `dizzy/tests/generators/test_procedures.py`
  - `dizzy/tests/generators/test_policies.py`
  - `dizzy/tests/generators/test_projections.py`
  - `dizzy/tests/generators/test_models.py`
  - `dizzy/tests/test_cli.py`

## Phase 3 — Generator Modules (TDD: test → implement → snapshot)

For each generator, the cycle is:
1. Write unit tests for `render_*` functions (assert on string content)
2. Implement `render_*` + `write_*` functions (make tests pass)
3. Run snapshot tests to lock in output; commit snapshots

Create `dizzy/src/dizzy/generators/` with one module per feat section. Each module exposes:
- `render_*(feat, ...) -> str` — pure function, no filesystem access
- `write_*(feat, output_dir, ...)` — calls `render_*` and writes to the correct path

### `generators/commands.py`

- [x] Write `tests/generators/test_commands.py`:
  - unit: `render_scaffold_commands(feat)` produces valid LinkML stub listing all commands with attributes
  - unit: `render_gen_commands(feat)` produces valid Pydantic file for all commands
- [x] Implement `render_scaffold_commands` + `write_scaffold_commands` (stub `def/commands.yaml`, skip if exists)
- [x] Implement `render_gen_commands` + `write_gen_commands` (`gen_def/pydantic/commands.py`)
- [x] Run snapshot test; update + commit snapshots

### `generators/events.py`

- [x] Write `tests/generators/test_events.py`:
  - unit: `render_scaffold_events(feat)` produces valid LinkML stub listing all events with attributes
  - unit: `render_gen_events(feat)` produces valid Pydantic file for all events
- [x] Implement `render_scaffold_events` + `write_scaffold_events` (stub `def/events.yaml`, skip if exists)
- [x] Implement `render_gen_events` + `write_gen_events` (`gen_def/pydantic/events.py`)
- [x] Run snapshot test; update + commit snapshots

### `generators/queries.py`

- [x] Write `tests/generators/test_queries.py`:
  - unit: `render_scaffold_query_input(query_name, feat)` produces LinkML stub
  - unit: `render_scaffold_query_output(query_name, feat)` produces LinkML stub
  - unit: `render_gen_query_protocol(query_name, feat)` produces correct Protocol + context dataclass (imports, class names, docstring from description, model field)
- [x] Implement scaffold renders + writers (stubs in `def/queries/`, skip if exists)
- [x] Implement gen renders + writers (`gen_def/pydantic/query/`, `gen_int/python/query/`, `src/query/` stub if not exists)
- [x] Run snapshot test; update + commit snapshots

### `generators/procedures.py`

- [ ] Write `tests/generators/test_procedures.py`:
  - unit: `render_procedure_context(procedure_name, feat)` — assert context dataclass, nested emitters + queries dataclasses, correct imports
  - unit: `render_procedure_protocol(procedure_name, feat)` — assert Protocol class, `__call__` signature, correct imports
  - unit: procedure with no `queries` → no queries dataclass; procedure with no `emits` → empty emitters dataclass
- [ ] Implement `render_procedure_context` + `write_procedure_context` (`gen_int/python/procedure/*_context.py`)
- [ ] Implement `render_procedure_protocol` + `write_procedure_protocol` (`gen_int/python/procedure/*_protocol.py`)
- [ ] Implement `write_procedure_src_stub` (`src/procedure/<name>.py`, skip if exists)
- [ ] Run snapshot test; update + commit snapshots

### `generators/policies.py`

- [ ] Write `tests/generators/test_policies.py`:
  - unit: `render_policy_context(policy_name, feat)` — assert emitters dataclass, correct imports
  - unit: `render_policy_protocol(policy_name, feat)` — assert Protocol class, `__call__` signature with event param
  - unit: policy with no `emits` → emitters dataclass has `pass`
- [ ] Implement `render_policy_context` + `write_policy_context` (`gen_int/python/policy/*_context.py`)
- [ ] Implement `render_policy_protocol` + `write_policy_protocol` (`gen_int/python/policy/*_protocol.py`)
- [ ] Implement `write_policy_src_stub` (`src/policy/<name>.py`, skip if exists)
- [ ] Run snapshot test; update + commit snapshots

### `generators/projections.py`

- [ ] Write `tests/generators/test_projections.py`:
  - unit: `render_projection(projection_name, feat)` — assert context dataclass with one session field per model, Protocol class, `__call__` with event + context params, correct imports
  - unit: projection with multiple models → multiple session fields in context
- [ ] Implement `render_projection` + `write_projection` (`gen_int/python/projection/*_projection.py`)
- [ ] Implement `write_projection_src_stub` (`src/projection/<name>.py`, skip if exists)
- [ ] Run snapshot test; update + commit snapshots

### `generators/models.py`

- [ ] Write `tests/generators/test_models.py`:
  - unit: `render_scaffold_model(schema_name, feat)` produces minimal LinkML stub with correct schema name
  - unit: `render_gen_model_pydantic(schema_name, def_dir)` produces Pydantic models from authored LinkML
  - unit: `render_gen_model_sqla(schema_name, def_dir)` produces SQLAlchemy models from authored LinkML
- [ ] Implement scaffold render + writer (stub `def/models/<name>.yaml`, skip if exists)
- [ ] Implement gen renders + writers (`gen_def/pydantic/models/<name>.py`, `gen_def/sqla/models/<name>.py`)
- [ ] Run snapshot test; update + commit snapshots

### `__init__.py` emitter

- [ ] Implement helper that writes an empty `__init__.py` in every generated directory
- [ ] Add assertions to integration snapshot tests that `__init__.py` exists in each generated dir

## Phase 4 — CLI

- [ ] Write `tests/test_cli.py` integration tests first:
  - `test_scaffold_creates_def_stubs` — runs `dizzy scaffold` against fixture, asserts def stubs exist
  - `test_scaffold_does_not_overwrite` — runs scaffold twice, asserts files unchanged
  - `test_scaffold_todos_flag` — runs with `--todos`, asserts `def/TODO.md` written
  - `test_gen_creates_all_outputs` — runs `dizzy gen`, snapshot-tests every generated file
  - `test_gen_does_not_overwrite_src` — runs gen twice, asserts src stubs unchanged
  - `test_gen_todos_flag` — runs with `--todos`, asserts `src/TODO.md` written
- [ ] Implement `dizzy scaffold <feat_file> <output_dir> [--todos]` — runs scaffold generators, prints next-steps message
- [ ] Implement `dizzy gen <feat_file> <output_dir> [--todos]` — runs gen generators, prints per-section summary and next-steps message
- [ ] Implement `generators/todos.py` — writes `def/TODO.md` (after scaffold) or `src/TODO.md` (after gen)
- [ ] Remove / retire the two standalone root scripts (`generate_linkml_from_feature.py`, `generate_protocols_from_commands.py`)
- [ ] Run full test suite; all tests pass

## Phase 5 — Install & Manual Smoke Test

- [ ] Install dizzy globally: `uv tool install --editable /home/conrad/dizzy/dizzy`
- [ ] Run `dizzy scaffold example.feat.yaml app/example` — verify def stubs created, next-steps message printed
- [ ] Run `dizzy scaffold example.feat.yaml app/example --todos` — verify `def/TODO.md` written
- [ ] Run `dizzy gen example.feat.yaml app/example` — verify all sections generate correctly, src stubs created
- [ ] Run `dizzy gen example.feat.yaml app/example --todos` — verify `src/TODO.md` written
- [ ] Re-run both commands — verify existing def/ and src/ files are not overwritten
- [ ] Run `dizzy scaffold /home/conrad/dizzy-recipe/app/01_dj_scripts/recipe.feat.yaml /home/conrad/dizzy-recipe/app/01_dj_scripts` — verify best-effort (no events, no projections → no output for those sections, no errors)
