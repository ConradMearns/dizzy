# DIZZY

**DIZZY is a methodology for writing event-sourced software.**

You describe a *feature* in a single `.feat.yaml` file. Dizzy scaffolds typed schemas,
generates protocols and implementation stubs, and packages each piece into
redistributable libraries. You fill in the business logic; Dizzy owns the wiring.

The goal is **reproducible, redistributable software**: features defined as data, with
no architecture or database baked in, so the same definition can target different
runtimes and deployments.

> ⚠️ **Research code.** Dizzy is a work in progress. The Python (`python-uv`) path is
> the most complete; the `rust-cargo` and `typescript-npm` runtimes are experimental.

## The model

A feature is built from two kinds of data and two kinds of functions, connected in two
loops:

```
Commands  ─▶  Procedures  ─▶  Events  ─▶  Policies  ─▶  Commands   (reactivity loop)
Events    ─▶  Projections ─▶  Models  ─▶  Queries   ─▶  Procedures (data loop)
```

- **Commands** — write intents ("please do this").
- **Events** — immutable facts ("this happened"). The source of truth.
- **Procedures** — handle a command, do the work, emit events.
- **Policies** — react to an event, dispatch follow-up commands.
- **Projections** — fold events into **models** (read-optimized state).
- **Queries** — read models back out.

Procedures emit an event for every effect, every fact worth recording, and every
business-level error. Those events accumulate in an event store and become the basis
for everything the system knows about itself over time.

## Install

Requires **Python 3.11+**, [uv](https://docs.astral.sh/uv/), and (optionally)
[just](https://github.com/casey/just).

```bash
uv tool install --editable .   # or: just install
dizzy --help
```

## A minimal feature

A guestbook: visitors sign it, signatures get stored and listed. This is the smallest
definition that uses both loops.

```yaml
# guestbook.feat.yaml
description: Guestbook — visitors sign, signatures are stored and listed

commands:
  sign_guestbook: A visitor wants to leave a signature

events:
  guestbook_signed: A visitor signed the guestbook

procedures:
  record_signature:
    description: Validate the signature and record it as a fact
    command: sign_guestbook
    emits: [guestbook_signed]

models:
  guestbook:
    description: Stored guestbook signatures
    adapters: [sqla]

projections:
  signature_store:
    description: Persist each signature into the guestbook model
    event: guestbook_signed
    model: guestbook
    adapter: sqla

queries:
  list_signatures:
    description: List all guestbook signatures, newest first
    model: guestbook
    adapter: sqla
```

## The workflow

DIZZY generation is a pipeline with **human-in-the-loop** authoring at each handoff.
Generated interfaces are always overwritten; the files you author (`def/` schemas and
the implementation stubs in `lib/`) are never clobbered.

```bash
# 1. scaffold LinkML schemas + libconfig.yaml from the feat file
dizzy generate definitions  guestbook.feat.yaml ./out

#    ✍️  fill in field-level detail in out/def/*.yaml
#        (attributes on commands/events, model classes, query input/output)

# 2. compile schemas → the gen_def/gen_int type packages under lib/python-uv/
dizzy generate static  guestbook.feat.yaml ./out

# 3. package each element into a redistributable per-runtime library
dizzy generate libraries  guestbook.feat.yaml ./out

#    ✍️  implement the bodies in
#        out/lib/python-uv/{procedure,policy,projection,query}/<name>/src/*.py
```

What lands in `./out`:

```
out/
├── def/                 # YOU author — LinkML schemas (scaffolded, never overwritten)
├── libconfig.yaml       # YOU author — which runtime each element targets
└── lib/                 # generated — one self-contained workspace per runtime
    └── python-uv/
        ├── gen_def/      # generated — Pydantic + SQLAlchemy from your LinkML
        ├── gen_int/      # generated — typed Protocols, contexts, adapters
        └── <kind>/<name>/src/  # YOU implement — stubs (never overwritten)
```

Each runtime tree is a self-contained workspace: `gen_def` and `gen_int` are
installable packages, and every element package depends on them — so a generated
`lib/python-uv/` can be lifted out and shipped on its own.

> **Naming:** you write `snake_case` element names; LinkML compiles them to
> `PascalCase` Pydantic classes (`sign_guestbook` → `SignGuestbook`). Generated code
> imports the class but keeps snake_case for runtime accessors like
> `context.emit.guestbook_signed(...)`.

## See it run

The [`examples/guestbook/`](examples/guestbook/) directory has this feature fully
generated **and** implemented, with a `demo.py` that wires it together. The generated
`lib/python-uv/` is a uv workspace, so sync it once and run the demo inside it:

```bash
uv sync --project examples/guestbook/lib/python-uv
uv run --project examples/guestbook/lib/python-uv python examples/guestbook/demo.py
# Guestbook (newest first):
#   - Edsger: Goto considered harmful
#   - Grace: Compiled it
#   - Ada: Hello from 1843
```

See [`examples/`](examples/) for the full walkthrough.

## For AI agents

Dizzy ships its reference documentation in the CLI (the analog of `sd prime`):

```bash
dizzy docs            # CLI manpage + roadmap (canonical: docs/cli.md)
dizzy docs authoring  # agent guide: components, .feat.yaml shape, authoring surface
```

The `authoring` page explains every component, the `.feat.yaml` shape, the authoring
surface, and the generated layout in one pass. Point an agent at it before asking it
to write a feature. The `cli` page (the default) doubles as the project roadmap: each
unbuilt command's section is its requirements document.

## Project layout

This is a **uv monorepo**:

- **`dizzy/`** — the core package and generators (`dizzy/src/dizzy/`).
- **`examples/`** — worked examples.
- **`docs/`** — specification, whitepaper, and design notes (Typst sources + PDFs).

Common commands live in the [`justfile`](justfile) (`just test`, `just check`,
`just whitepaper`). Configuration is documented via `dizzy config`.

## Issue tracking

This project uses [Seeds](https://github.com/jayminwest/seeds) for git-native issue
tracking. Run `sd ready` to find unblocked work; see [`CLAUDE.md`](CLAUDE.md).

## Use of AI

Portions of the code and commit history in this repository may be generated or
assisted by AI tools, reviewed before inclusion.

The whitepaper and other written documents under `docs/` are **authored and edited by
the maintainer**. AI may be used there only for review, fact-checking, and feedback —
not for authorship.
