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
| `def/` | **you** (scaffolded by `dizzy def`) | LinkML schemas. Scaffolds are generated; you fill in the `attributes`. |
| `libconfig.yaml` | **you** (scaffolded by `dizzy def`) | Which runtime each element targets. |
| `gen_def/` | `dizzy gen` | Pydantic + SQLAlchemy classes compiled from `def/` by LinkML. |
| `gen_int/` | `dizzy gen` | Typed Protocols, contexts, and adapters. |
| `src/` | **you** (scaffolded by `dizzy gen`) | Implementation stubs. The three files here are filled in. |
| `lib/` | `dizzy lib` | Per-element redistributable packages, one workspace member each. |
| `demo.py` | **you** | Host glue that wires the generated pieces together and runs them. |

> **Naming:** you write element names in `snake_case`; LinkML compiles them to
> `PascalCase` classes (`sign_guestbook` → `SignGuestbook`). Generated code imports
> the PascalCase class but keeps snake_case for runtime accessors like
> `context.emit.guestbook_signed(...)`.

## Run the finished example

From the repository root:

```bash
uv run python examples/guestbook/demo.py
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
and calls the query. Dizzy generated everything it imports.

## Rebuild it from scratch

Delete the generated trees and re-run the three commands. `def/` stubs and `src/`
implementations are **never overwritten**, so to regenerate them too, remove them.

```bash
# from the repo root
rm -rf examples/guestbook/{gen_def,gen_int,src,lib}

# 1. scaffold def/ LinkML schemas + libconfig.yaml (idempotent; won't clobber edits)
uv run dizzy def examples/guestbook/guestbook.feat.yaml examples/guestbook

# 2. (human step) fill in attributes in def/*.yaml — see the committed files here

# 3. compile LinkML + generate protocols, contexts, and src/ stubs
uv run dizzy gen examples/guestbook/guestbook.feat.yaml examples/guestbook

# 4. (human step) implement the src/ stubs — see the committed files here

# 5. split each element into a redistributable runtime package
uv run dizzy lib examples/guestbook/guestbook.feat.yaml examples/guestbook
```

## The three steps, in detail

### `dizzy def` — scaffold the schemas

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

### `dizzy gen` — compile and generate interfaces

Runs LinkML over `def/` to produce `gen_def/` (Pydantic + SQLAlchemy), generates the
typed `gen_int/` Protocols/contexts/adapters from the feat structure, and writes
`src/` implementation stubs that raise `NotImplementedError`. You implement them —
see `src/procedure/record_signature.py`, `src/projection/signature_store.py`, and
`src/query/list_signatures.py`.

### `dizzy lib` — package per runtime

Reads `libconfig.yaml` (every element targets `python-uv` here) and emits
`lib/python-uv/`, a uv workspace with one package per element. This is the
redistribution boundary: each procedure, policy, query, and projection becomes an
independently versionable package.
