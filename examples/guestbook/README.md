# Guestbook — a minimal worked example

The smallest feature that still exercises both of Dizzy's loops:

```
SignGuestbook ─▶ record_signature ─▶ GuestbookSigned          (reactivity)
GuestbookSigned ─▶ signature_store ─▶ guestbook ─▶ list_signatures   (data)
```

A visitor signs the guestbook (a **command**). A **procedure** validates it and
emits a **fact** (an **event**). A **projection** folds that fact into a **model**
(a read-optimized table). A **query** reads the model back out.

This directory contains the whole thing **already generated and implemented**, so
you can read the output without running anything. To rebuild it from scratch, follow
the steps below.

## What's in here

| Path | Who writes it | What it is |
|------|---------------|------------|
| `guestbook.feat.yaml` | **you** | The feature definition — the single source of truth. |
| `def/` | **you** (scaffolded by `dizzy generate definitions`) | LinkML schemas. Scaffolds are generated; you fill in the `attributes`. |
| `libconfig.yaml` | **you** (scaffolded by `dizzy generate definitions`) | Which runtime each element targets. |
| `lib/python-uv/gen_def/` | `dizzy generate static` | Pydantic + SQLAlchemy classes compiled from `def/` — an installable package. |
| `lib/python-uv/gen_int/` | `dizzy generate static` | Typed Protocols, contexts, and adapters — an installable package. |
| `lib/python-uv/<kind>/<name>/` | `dizzy generate libraries` | One redistributable package per element; `src/<name>.py` is the implementation stub (the three here are filled in). |
| `lib/python-uv/pyproject.toml` | `dizzy generate libraries` | The uv workspace tying `gen_def`, `gen_int`, and every element package together. |
| `demo.py` | **you** | Host glue that wires the generated pieces together and runs them. |

> **Naming:** you write element names in `snake_case`; LinkML compiles them to
> `PascalCase` classes (`sign_guestbook` → `SignGuestbook`). Generated code imports
> the PascalCase class but keeps snake_case for runtime accessors like
> `context.emit.guestbook_signed(...)`.

## Run the finished example

The generated `lib/python-uv/` is a uv workspace. Sync it once, then run `demo.py`
inside that environment — from the repository root:

```bash
uv sync --project examples/guestbook/lib/python-uv
uv run --project examples/guestbook/lib/python-uv python examples/guestbook/demo.py
```

Expected output:

```
Guestbook (newest first):
  - Edsger: Goto considered harmful
  - Grace: Compiled it
  - Ada: Hello from 1843
```

`demo.py` plays the role of the host application: it owns the database (here an
in-memory SQLite), routes each emitted event to the projections that listen for it,
and calls the query. Dizzy generated everything it imports, and each piece is an
installed workspace package.

## Rebuild it from scratch

Delete the generated tree and re-run the three commands. `def/` stubs and the
`src/` implementations inside `lib/` are **never overwritten**, so to regenerate them
too, remove them.

```bash
# from the repo root
rm -rf examples/guestbook/lib

# 1. scaffold def/ LinkML schemas + libconfig.yaml (idempotent; won't clobber edits)
uv run dizzy generate definitions examples/guestbook/guestbook.feat.yaml examples/guestbook

# 2. (human step) fill in attributes in def/*.yaml — see the committed files here

# 3. compile LinkML into the gen_def/gen_int type packages under lib/python-uv/
uv run dizzy generate static examples/guestbook/guestbook.feat.yaml examples/guestbook

# 4. split each element into a redistributable runtime package
uv run dizzy generate libraries examples/guestbook/guestbook.feat.yaml examples/guestbook

# 5. (human step) implement the src/ stubs in lib/python-uv/<kind>/<name>/src/
#    — see the committed files here
```

## The three steps, in detail

### `dizzy generate definitions` — scaffold the schemas

Reads `guestbook.feat.yaml` and writes empty LinkML stubs into `def/` plus a
`libconfig.yaml`. You then fill in the field-level detail. For example, the
scaffold writes `attributes: {}` for the command; you author:

```yaml
# def/commands.yaml
classes:
  sign_guestbook:
    description: A visitor wants to leave a signature
    attributes:
      visitor_name: { range: string, required: true }
      message:      { range: string, required: true }
```

### `dizzy generate static` — compile the type packages

Runs LinkML over `def/` to produce the `gen_def` package (Pydantic + SQLAlchemy) and
generates the typed `gen_int` package (Protocols/contexts/adapters) from the feat
structure. Both land under `lib/python-uv/` as installable uv packages, each with its
own `pyproject.toml`.

### `dizzy generate libraries` — package per runtime

Reads `libconfig.yaml` (every element targets `python-uv` here) and emits the element
packages under `lib/python-uv/`, plus the workspace `pyproject.toml` tying them and the
type packages together. Each element package declares `gen_def`/`gen_int` as workspace
dependencies and carries a real-signature implementation stub in `src/<name>.py` that
raises `NotImplementedError`. You implement them — see
`lib/python-uv/procedure/record_signature/src/record_signature.py`,
`.../projection/signature_store/src/signature_store.py`, and
`.../query/list_signatures/src/list_signatures.py`.

This is the redistribution boundary: each procedure, policy, query, and projection is
an independently versionable package, and the whole `lib/python-uv/` workspace is
self-contained.
