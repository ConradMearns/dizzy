# Known Issues

## No test coverage for 2+ emits in procedures and policies

`render_procedure_context` and `render_policy_context` both handle `emits` via a loop
and are correct for any count. However, tests only cover 0 emits and 1 emit.
A case with 2+ emits (multiple emitter fields in the generated dataclass) is untested.
This gap exists in both `test_procedures.py` and `test_policies.py`.

---

## Projection formatting inconsistencies vs. procedures/policies

Projections differ from procedures and policies in two ways not explained by the spec:
1. Context and protocol are combined in one `_projection.py` file, while procedures use
   separate `_context.py` and `_protocol.py` files. Plausible rationale (simpler context,
   no nested dataclasses), but not stated.
2. The projection `__call__` is formatted as a single line, while policies (same parameter
   structure: `event`, `context`) use multi-line formatting. No semantic reason for the
   difference — likely an inconsistency in how the spec example was written.

---

## Duplicated type maps across generator modules

`_LINKML_TYPE_MAP` and `_PYTHON_TYPE_MAP` are copy-pasted into every generator module
(`commands.py`, `events.py`, and future `queries.py`, `models.py`, etc.).

A change to a type mapping (e.g. adding `date` → `date`) must be applied in every file.
This is a maintenance hazard that will grow as more generators are added.