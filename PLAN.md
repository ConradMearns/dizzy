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

## Phase 3 — Scaffold Generators (LinkML stub generation only)

`dizzy scaffold` reads the feat file and writes `def/` LinkML stubs. That is all it does.
No Pydantic, no SQLAlchemy, no Protocols — just stubs for the user to author.

### `generators/commands.py` — scaffold only

- [x] Implement `render_scaffold_commands` + `write_scaffold_commands` (stub `def/commands.yaml`, skip if exists)
- [x] Write tests: linkml header, all commands listed with attributes
- [x] Run snapshot test; update + commit snapshots

### `generators/events.py` — scaffold only

- [x] Implement `render_scaffold_events` + `write_scaffold_events` (stub `def/events.yaml`, skip if exists)
- [x] Write tests: linkml header, all events listed with attributes
- [x] Run snapshot test; update + commit snapshots

### `generators/queries.py` — scaffold only

- [x] Implement `render_scaffold_query_input` + `render_scaffold_query_output` + writers (stubs in `def/queries/`, skip if exists)
- [x] Write tests: linkml header, class name, empty attributes
- [x] Run snapshot test; update + commit snapshots

### `generators/models.py` — scaffold only

- [x] Implement `render_scaffold_model` + `write_scaffold_model` (stub `def/models/<name>.yaml`, skip if exists)
- [x] Write tests: linkml header, schema name, description, empty classes
- [x] Run snapshot test; update + commit snapshots

## Phase 3 Cleanup — Remove incorrect gen code

The original implementation incorrectly added manual Pydantic generation to the scaffold
generators. `gen_def/` files must be produced by running `linkml gen-pydantic` on the
authored `def/` stubs, not by rendering Python strings from feat data.

### `generators/commands.py`

- [x] Remove `render_gen_commands` and `write_gen_commands`
- [x] Remove `test_render_gen_commands_*` tests and `test_write_gen_commands_*` test from `test_commands.py`
- [x] Remove `test_render_gen_commands_snapshot` from `test_commands.py`
- [x] Delete the `test_render_gen_commands_snapshot` entry from `tests/generators/__snapshots__/test_commands.ambr`

### `generators/events.py`

- [x] Remove `render_gen_events` and `write_gen_events`
- [x] Remove `test_render_gen_events_*` tests and `test_write_gen_events_*` test from `test_events.py`
- [x] Remove `test_render_gen_events_snapshot` from `test_events.py`
- [x] Delete the `test_render_gen_events_snapshot` entry from `tests/generators/__snapshots__/test_events.ambr`

### `generators/queries.py`

- [x] Remove `render_gen_query_pydantic_stub`, `write_gen_query_pydantic_input`, `write_gen_query_pydantic_output`
- [x] Remove `test_write_gen_query_pydantic_*` tests from `test_queries.py` (if any)
- [x] Keep all scaffold tests and Protocol tests — those are correct

### `generators/models.py`

- [x] Remove `render_gen_model_pydantic`, `write_gen_model_pydantic`, `render_gen_model_sqla`, `write_gen_model_sqla`
- [x] Remove `_load_def_classes` helper (no longer needed)
- [x] Remove corresponding tests from `test_models.py`: all `test_render_gen_model_*` and `test_write_gen_model_*` tests
- [x] Remove pydantic/sqla snapshot tests and their `.ambr` entries
- [x] Remove `tests/fixtures/def/` directory and `recipe_def_dir` fixture from `conftest.py` — no longer needed
- [x] Run `just test` — all tests pass

## Phase 4 — CLI: `dizzy scaffold`

Implement and test `dizzy scaffold` before any gen work begins.

- [x] Write `tests/test_cli.py` scaffold integration tests (call `scaffold()` directly — typer commands are plain functions):
  - `test_scaffold_creates_def_stubs` — calls `scaffold()` against fixture, asserts all `def/` stubs exist
  - `test_scaffold_does_not_overwrite` — calls `scaffold()` twice, asserts files unchanged
- [x] Implement `dizzy scaffold <feat_file> <output_dir>` in `cli.py` — calls all scaffold writers, prints next-steps message
- [x] Run `just test` — all tests pass

## Phase 5 — Gen Generators (linkml runner + Protocol generators)

`dizzy gen` runs in two sub-steps:
1. Run the LinkML toolchain on each `def/` stub to produce `gen_def/` files
2. Read the feat file to generate `gen_int/` Protocol files and `src/` stubs

### `generators/linkml_runner.py`

- [ ] Implement `run_linkml_pydantic(def_file: Path, output_file: Path) -> None` — shells out to `linkml gen-pydantic <def_file>` and writes result to `output_file`
- [ ] Implement `run_linkml_sqla(def_file: Path, output_file: Path) -> None` — shells out to `linkml gen-sqla <def_file>` and writes result to `output_file`
- [ ] Write `tests/generators/test_linkml_runner.py`:
  - Verify `linkml gen-pydantic` can be run against `def/commands.yaml` stub and produces valid Python
  - Verify `linkml gen-pydantic` can be run against `def/events.yaml` stub and produces valid Python
  - Verify `linkml gen-pydantic` can be run against `def/queries/*_input.yaml` stub and produces valid Python
  - Verify `linkml gen-pydantic` can be run against `def/models/<name>.yaml` stub and produces valid Python
  - Verify `linkml gen-sqla` can be run against `def/models/<name>.yaml` stub and produces valid Python
  - Use the scaffold fixture stubs (scaffolded from `recipe.feat.yaml`) as inputs

### Protocol generators (already implemented — verify correct)

- [x] `render_gen_query_protocol` + `write_gen_query_protocol` — `gen_int/python/query/<name>.py`
- [x] `render_procedure_context` + `render_procedure_protocol` + writers — `gen_int/python/procedure/`
- [x] `render_policy_context` + `render_policy_protocol` + writers — `gen_int/python/policy/`
- [x] `render_projection` + writer — `gen_int/python/projection/`

### `src/` stub generators (already implemented — verify correct)

- [x] `write_src_query_stub` — `src/query/<name>.py`, skip if exists
- [x] `write_procedure_src_stub` — `src/procedure/<name>.py`, skip if exists
- [x] `write_policy_src_stub` — `src/policy/<name>.py`, skip if exists
- [x] `write_projection_src_stub` — `src/projection/<name>.py`, skip if exists

### `__init__.py` emitter

- [ ] Implement helper that writes an empty `__init__.py` in every generated directory
- [ ] Add assertions to integration snapshot tests that `__init__.py` exists in each generated dir

## Phase 6 — CLI: `dizzy gen`

- [ ] Write `tests/test_cli.py` gen integration tests (call `gen()` directly — typer commands are plain functions):
  - `test_gen_creates_all_outputs` — calls `gen()`, asserts all `gen_def/`, `gen_int/`, `src/` files exist
  - `test_gen_does_not_overwrite_src` — calls `gen()` twice, asserts src stubs unchanged
- [ ] Implement `dizzy gen <feat_file> <output_dir>` in `cli.py` — runs linkml runner then Protocol generators, prints per-section summary and next-steps message
- [ ] Run `just test` — all tests pass

## Phase 7 — Install & Manual Smoke Test

- [ ] Install dizzy globally: `uv tool install --editable /home/conrad/dizzy/dizzy`
- [ ] Run `dizzy scaffold example.feat.yaml app/example` — verify def stubs created, next-steps message printed
- [ ] Run `dizzy gen example.feat.yaml app/example` — verify all sections generate correctly, src stubs created
- [ ] Re-run both commands — verify existing def/ and src/ files are not overwritten
- [ ] Run `dizzy scaffold /home/conrad/dizzy-recipe/app/01_dj_scripts/recipe.feat.yaml /home/conrad/dizzy-recipe/app/01_dj_scripts` — verify best-effort (no events, no projections → no output for those sections, no errors)
