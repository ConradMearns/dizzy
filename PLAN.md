# Dizzy Generator — Plan

## Phase 1 — Example & Schema

- [ ] Update `example.feat.yaml` to include all sections: `models`, `queries` (with inline attributes), `commands`, `events`, `procedures`, `policies`, `projections`
- [ ] Create `dizzy/src/dizzy/def/feat.yaml` — LinkML meta-schema formally defining the `.feat.yaml` format (`FeatureDefinition`, `ModelDef`, `QueryDef`, `CommandDef`, `EventDef`, `ProcedureDef`, `PolicyDef`, `ProjectionDef`)

## Phase 2 — Generator Modules

Create `dizzy/src/dizzy/generators/` with one module per feat section, each exposing `generate(feat, def_dir, gen_dir)` and skipping gracefully if the section is absent.

- [ ] `generators/models.py` — `models` → `def/models.yaml` + `gen/models.py` (via gen-pydantic)
- [ ] `generators/commands.py` — `commands` → `def/commands.yaml` + `gen/commands.py`
- [ ] `generators/events.py` — `events` → `def/events.yaml` + `gen/events.py`
- [ ] `generators/queries.py` — `queries` → `def/queries.yaml` + `gen/queries.py` + `gen/query_interfaces.py`
- [ ] `generators/procedures.py` — `procedures` → `gen/procedure/py/*_context.py` + `*_protocol.py`
- [ ] `generators/policies.py` — `policies` → `gen/policy/py/*_protocol.py`
- [ ] `generators/projections.py` — `projections` → `gen/projection/py/*_projection.py`

## Phase 3 — CLI

- [ ] Rebuild `dizzy/src/dizzy/cli.py` `gen` command to accept `feat_file` + `output_dir`, call each generator in order, and print a per-section summary
- [ ] Remove / retire the two standalone root scripts (`generate_linkml_from_feature.py`, `generate_protocols_from_commands.py`)

## Phase 4 — Install & Test

- [ ] Install dizzy globally: `uv tool install --editable /home/conrad/dizzy/dizzy`
- [ ] Run `dizzy gen example.feat.yaml app/example` — verify all sections generate correctly
- [ ] Run `dizzy gen /home/conrad/dizzy-recipe/app/01_dj_scripts/recipe.feat.yaml /home/conrad/dizzy-recipe/app/01_dj_scripts` — verify best-effort (no events, no projections → no output for those sections, no errors)
