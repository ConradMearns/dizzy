# Implementation Plan — Model Adapters

Each phase ends with a concrete validation command. Complete all checkboxes in a phase before
moving to the next.

---

## Phase 1 — Data model + schema migration

Goal: parsers and generators compile against the new types; `dizzy def` and `dizzy gen` run
cleanly on `receipts.feat.yaml`.

**`feat.py` — data model**
- [ ] Add `ModelDef` dataclass with `description: str` and `adapters: list[str]`
- [ ] Change `FeatureDefinition.models` from `dict[str, str]` to `dict[str, ModelDef]`
- [ ] Add `adapter: str | None = None` to `QueryDef`
- [ ] Replace `models: list[str]` with `model: str | None` and `adapter: str | None` on `ProjectionDef`
- [ ] Update `load_feat` — parse models as full object form into `ModelDef`
- [ ] Update `_parse_query_def` to read `adapter`
- [ ] Update `_parse_projection_def` to read singular `model` + `adapter` (drop `models` list)

**Generator minimal fixes — compile against new types, no new behaviour**
- [ ] `generators/models.py` — access `model_def.description` instead of raw string
- [ ] `generators/queries.py` — read `query.adapter` (may be `None`); keep existing output for now
- [ ] `generators/projections.py` — replace loop over `projection.models` with `projection.model`; keep existing output for now
- [ ] `cli.py` — remove `run_linkml_sqla` call for models that don't declare `sqla` as an adapter (guard on `feat.models[name].adapters`)

**Migrate feat files**
- [ ] `receipts.feat.yaml` — models: full object form with `adapters`; add a query and a projection that use the model so the demo exercises the full path
- [ ] `recipe.feat.yaml` (test fixture) — models: full object form with `adapters`; queries: add `adapter`; projections: singular `model` + `adapter`
- [ ] `partial.feat.yaml` (test fixture) — no models/projections; verify it loads cleanly as-is

**Validate**
```
rm -rf demo/
dizzy def receipts.feat.yaml demo/
dizzy gen receipts.feat.yaml demo/
# expect: no errors, def/ and gen_int/ files created under demo/
```

---

## Phase 2 — Validation rules

Goal: `validate_feat` rejects bad adapter bindings; all validation tests pass.

- [ ] Update existing model reference checks to use `ModelDef` (was plain string)
- [ ] Update projection model check for singular `model` field
- [ ] Add: query with `model` but no `adapter` → error
- [ ] Add: query with `adapter` but no `model` → error
- [ ] Add: query adapter not in `model.adapters` → error
- [ ] Add: projection with `model` but no `adapter` → error
- [ ] Add: projection with `adapter` but no `model` → error
- [ ] Add: projection adapter not in `model.adapters` → error
- [ ] `test_validation.py` — update `test_projection_references_unknown_model` and `test_query_references_unknown_model` to use `ModelDef`
- [ ] `test_validation.py` — add a test for each new error rule above

**Validate**
```
pytest dizzy/tests/test_validation.py -v
# expect: all tests pass including new cases
```

---

## Phase 3 — Adapter generator

Goal: `dizzy gen` writes shared adapter class files under `gen_int/python/adapters/`.

- [ ] Create `generators/adapters.py` with adapter registry: `sqla → SqlaAdapter(session: Session)`, `relative_filesystem → RelativeFilesystemAdapter(root: Path)`
- [ ] Implement `render_adapter(adapter_name) -> str` — produces the dataclass source
- [ ] Implement `write_adapter(adapter_name, output_dir)` — writes to `gen_int/python/adapters/<name>.py`, always overwrites
- [ ] Emit a warning (not an error) for unrecognised adapter names
- [ ] `cli.py` — collect unique adapters across all `feat.models` values; call `write_adapter` for each
- [ ] Create `tests/generators/test_adapters.py`:
  - [ ] `render_adapter("sqla")` contains `SqlaAdapter`, `session: Session`, correct import
  - [ ] `render_adapter("relative_filesystem")` contains `RelativeFilesystemAdapter`, `root: Path`, correct import
  - [ ] `write_adapter` creates file at correct path and always overwrites
  - [ ] Unknown adapter name emits a warning

**Validate**
```
dizzy gen receipts.feat.yaml demo/
ls demo/gen_int/python/adapters/
# expect: sqla.py and/or relative_filesystem.py present with correct content
pytest dizzy/tests/generators/test_adapters.py -v
```

---

## Phase 4 — Query context uses adapter class

Goal: generated query protocol files import and use the correct adapter class instead of `Any`.

- [ ] `generators/queries.py` — when `query.adapter` is set, import adapter class from `gen_int.python.adapters.<adapter>`; emit `adapter: <AdapterClass>` field on context dataclass
- [ ] `generators/queries.py` — when `query.adapter` is `None`, emit `pass` (unchanged)
- [ ] Remove `Any` from query protocol imports when no longer needed
- [ ] `test_queries.py` — update `test_render_gen_query_protocol_imports`: expect adapter import not `Any`
- [ ] `test_queries.py` — update `test_render_gen_query_protocol_context_class`: expect `adapter: <AdapterClass>` not `<model>: Any`
- [ ] `test_queries.py` — update `test_render_gen_query_protocol_second_query` similarly
- [ ] Regenerate `__snapshots__/test_queries.ambr` (`pytest --snapshot-update`)

**Validate**
```
dizzy gen receipts.feat.yaml demo/
grep -A5 "class.*_context" demo/gen_int/python/query/*.py
# expect: adapter field with correct type, no Any
pytest dizzy/tests/generators/test_queries.py -v
```

---

## Phase 5 — Projection context uses adapter class

Goal: generated projection protocol files use singular model + adapter class.

- [ ] `generators/projections.py` — when `projection.adapter` is set, import adapter class; emit single `adapter: <AdapterClass>` field on context dataclass
- [ ] `generators/projections.py` — when `projection.model` is `None`, emit `pass`
- [ ] Remove `Any` from projection imports when no longer needed
- [ ] `test_projections.py` — remove `test_render_projection_multiple_models` (no longer valid)
- [ ] `test_projections.py` — update `test_render_projection_imports`: expect adapter import not `Any`
- [ ] `test_projections.py` — update `test_render_projection_context_dataclass`: expect `adapter: <AdapterClass>` not `recipes: Any`
- [ ] Regenerate `__snapshots__/test_projections.ambr` (`pytest --snapshot-update`)

**Validate**
```
dizzy gen receipts.feat.yaml demo/
grep -A5 "class.*_context" demo/gen_int/python/projection/*.py
# expect: adapter field with correct type, no Any
pytest dizzy/tests/generators/test_projections.py -v
```

---

## Phase 6 — Full test suite cleanup

Goal: all tests green, no stale assertions or snapshots.

- [ ] `test_models.py` — update any inline `FeatureDefinition(models={"x": "str"})` to use `ModelDef`
- [ ] `test_validation.py` — confirm all inline feat constructions use `ModelDef`
- [ ] Run full suite and fix any remaining failures

**Validate**
```
pytest dizzy/ -v
# expect: all tests pass, no warnings about snapshots
```
