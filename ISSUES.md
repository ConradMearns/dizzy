# Known Issues

## Projection formatting inconsistencies vs. procedures/policies

Projections differ from procedures and policies in two ways not explained by the spec:
1. Context and protocol are combined in one `_projection.py` file, while procedures use
   separate `_context.py` and `_protocol.py` files. Plausible rationale (simpler context,
   no nested dataclasses), but not stated.
2. The projection `__call__` is formatted as a single line, while policies (same parameter
   structure: `event`, `context`) use multi-line formatting. No semantic reason for the
   difference — likely an inconsistency in how the spec example was written.

---

## Legacy generator scripts can be removed

`generate_linkml_from_feature.py` and `generate_protocols_from_commands.py` at the repo root
are the original hand-rolled predecessors to the dizzy generator pipeline. They are now fully
superseded by `dizzy scaffold` and `dizzy gen`. They should be deleted to avoid confusion about
which pipeline is canonical.

---

## Root pyproject.toml sets up an unnecessary workspace

The root `pyproject.toml` defines a `uv` workspace with `dizzy` as a member subproject.
The intent is for dizzy to be a standalone package — the workspace wrapper adds complexity
with no benefit. The root `pyproject.toml` and its dev dependencies (`plotext`, `xxhash`,
`pandas`, etc.) should be removed and `dizzy/pyproject.toml` promoted to the repo root.

---

## `dizzy gen` gives no useful error when def/ stubs are missing

`gen()` calls `run_linkml_pydantic` / `run_linkml_sqla` directly. If `def/` stubs don't
exist (i.e. `scaffold` was never run), the subprocess raises `CalledProcessError` with
no context. A guard at the top of `gen()` that checks for missing def/ files and prints
a clear message would improve DX significantly.

---

## `test_gen_creates_all_outputs` expected-paths list is not reused

The list of expected output paths in `test_gen_creates_all_outputs` is a long inline
sequence of `assert ... .exists()` calls. If the output layout changes, every assertion
must be updated by hand. Extracting the expected paths as a constant or fixture would
make the test easier to maintain and could be reused by other tests.

---

## Duplicated type maps across generator modules

`_LINKML_TYPE_MAP` and `_PYTHON_TYPE_MAP` are copy-pasted into every generator module
(`commands.py`, `events.py`, and future `queries.py`, `models.py`, etc.).

A change to a type mapping (e.g. adding `date` → `date`) must be applied in every file.
This is a maintenance hazard that will grow as more generators are added.