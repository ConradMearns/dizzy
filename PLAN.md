# Dizzy Generator — Plan

## Phase 1 — Example & Schema

- [x] Update `example.feat.yaml` to include all sections: `models`, `queries`, `commands`, `events`, `procedures`, `policies`, `projections`
- [x] Create `dizzy/src/dizzy/def/feat.yaml` — LinkML meta-schema formally defining the `.feat.yaml` format (`FeatureDefinition`, `ModelDef`, `QueryDef`, `CommandDef`, `EventDef`, `ProcedureDef`, `PolicyDef`, `ProjectionDef`)

## Phase 2 — Generator Modules

Create `dizzy/src/dizzy/generators/` with one module per feat section, each exposing `generate(feat, def_dir, gen_def_dir, gen_int_dir)` and skipping gracefully if the section is absent.

**scaffold generators** (def stubs only — never overwrite existing files):
- [ ] `generators/models.py` — `models` → stub `def/models/<schema_name>.yaml` (if not exists)
- [ ] `generators/commands.py` — `commands` → stub `def/commands.yaml` (if not exists)
- [ ] `generators/events.py` — `events` → stub `def/events.yaml` (if not exists)

**gen generators** (read def files, produce gen_def + gen_int + src stubs):
- [ ] `generators/models.py` — `def/models/<schema_name>.yaml` → `gen_def/pydantic/<schema_name>.py` + `gen_def/sqla/<schema_name>.py`
- [ ] `generators/commands.py` — `def/commands.yaml` → `gen_def/pydantic/commands.py`
- [ ] `generators/events.py` — `def/events.yaml` → `gen_def/pydantic/events.py`
- [ ] `generators/queries.py` — scaffold: `def/queries/<name>_input.yaml` + `def/queries/<name>_output.yaml` (stubs, if not exists); gen: `gen_def/pydantic/query/<name>_input.py` + `gen_def/pydantic/query/<name>_output.py` + `gen_int/python/query/<query_name>.py` (QueryProcess Protocol + context) + `src/query/<query_name>.py` (if not exists)
- [ ] `generators/procedures.py` — `procedures` → `gen_int/python/procedure/*_context.py` + `*_protocol.py` + `src/procedure/<procedure_name>.py` (if not exists)
- [ ] `generators/policies.py` — `policies` → `gen_int/python/policy/*_protocol.py` + `src/policy/<policy_name>.py` (if not exists)
- [ ] `generators/projections.py` — `projections` → `gen_int/python/projection/*_projection.py` + `src/projection/<projection_name>.py` (if not exists)

**todo generator** (optional, `--todos` flag):
- [ ] `generators/todos.py` — writes `def/TODO.md` (after scaffold) or `src/TODO.md` (after gen) summarising what needs to be authored/implemented

## Phase 3 — CLI

- [ ] Implement `dizzy scaffold <feat_file> <output_dir> [--todos]` — runs scaffold generators, prints next-steps message
- [ ] Implement `dizzy gen <feat_file> <output_dir> [--todos]` — runs gen generators, prints per-section summary and next-steps message
- [ ] Remove / retire the two standalone root scripts (`generate_linkml_from_feature.py`, `generate_protocols_from_commands.py`)

## Phase 4 — Install & Test

- [ ] Install dizzy globally: `uv tool install --editable /home/conrad/dizzy/dizzy`
- [ ] Run `dizzy scaffold example.feat.yaml app/example` — verify def stubs created, next-steps message printed
- [ ] Run `dizzy scaffold example.feat.yaml app/example --todos` — verify `def/TODO.md` written
- [ ] Run `dizzy gen example.feat.yaml app/example` — verify all sections generate correctly, src stubs created
- [ ] Run `dizzy gen example.feat.yaml app/example --todos` — verify `src/TODO.md` written
- [ ] Re-run both commands — verify existing def/ and src/ files are not overwritten
- [ ] Run `dizzy scaffold /home/conrad/dizzy-recipe/app/01_dj_scripts/recipe.feat.yaml /home/conrad/dizzy-recipe/app/01_dj_scripts` — verify best-effort (no events, no projections → no output for those sections, no errors)
