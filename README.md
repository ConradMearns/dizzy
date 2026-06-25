# DIZZY

> ⚠️ **Research code.**
> DIZZY is a work in progress.
> The Python (`python-uv`) path is the most complete;
>  the `rust-cargo` and `typescript-npm` runtimes are experimental.

A business Domain can be expressed a single artifact that is the litare design and source of implementation.
Readable as prose, but precise enough to generate a checkable implementation against.
As the entry point of change - the system stays tractable as the domain grows.

DIZZY defines a single feature-file that declares every component of the domain: 
commands, procedures, events, policies, projections, models, queries and queriers.

Code, typed contracts, deployment, stubs and tests are generated from the feature file as redistributable libraries in multiple languages.

The goal is **reproducible, redistributable and literate software**: features defined as data,
with no architecture or database baked in,
so the same definition can target different runtimes and deployments.


## Why DIZZY ?

The core hypothesis is that programs built to service DIZZY features will serve all libraries implemented in DIZZY.

If and when built for DIZZY, each additional system applies to all DIZZY libraries.

- A deployment for k8s; reducing the upfront cost of deployment for new projects.
- Telemetry - metrics and traces; ensuring deployed systems are transparent to operators without bespoke integration.

## Install

Requires **Python 3.11+**, [uv](https://docs.astral.sh/uv/), and (optionally)
[just](https://github.com/casey/just).

```bash
uv tool install --editable .   # or: just install
dizzy --help
```

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

#        fill in field-level detail in out/def/*.yaml
#        (attributes on commands/events, model classes, query input/output)

# 2. compile schemas → the gen_def/gen_int type packages under lib/python-uv/
dizzy generate static  guestbook.feat.yaml ./out

# 3. package each element into a redistributable per-runtime library
dizzy generate libraries  guestbook.feat.yaml ./out

#        implement the bodies in
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

The **[Build a guestbook tutorial](docs/tutorials/guestbook.md)** takes this feature from
an empty directory all the way to a running demo — describe it, generate and fill in the
schemas, implement the stubs, and wire up a `demo.py` that prints the signatures back out:

```text
Guestbook (newest first):
  - Edsger: Goto considered harmful
  - Grace: Compiled it
  - Ada: Hello from 1843
```

Every command, edit, and output in that tutorial is executed and checked by
`just tutorials-check`. For more committed examples, see [`examples/`](examples/).

See [`examples/`](examples/) for the full walkthrough.

## For AI agents

DIZZY ships a reference document tuned for LLM agents (the analog of `sd prime`):

```bash
dizzy docs            # CLI manpage + roadmap (ships in dizzy/src/dizzy/docs/cli.md)
dizzy docs authoring  # agent guide: components, .feat.yaml shape, authoring surface
```

The `authoring` page explains every component, the `.feat.yaml` shape, the authoring
surface, and the generated layout in one pass. Point an agent at it before asking it
to write a feature. The `cli` page (the default) doubles as the project roadmap: each
unbuilt command's section is its requirements document.

## Project layout

This is a **uv monorepo**:

- **`dizzy/`** — the core package and generators (`dizzy/src/dizzy/`). The CLI's own
  docs ship here (`dizzy/src/dizzy/docs/`) and print via `dizzy docs` / `dizzy onboard`.
- **`examples/`** — worked examples.
- **`docs/`** — the [mkdocs](https://www.mkdocs.org/) documentation site, organized by
  [Diátaxis](https://diataxis.fr/) (tutorials / how-to / reference / explanation), plus
  the maintainer whitepaper (Typst source + PDF). Run `just docs-serve` to preview it.

Common commands live in the [`justfile`](justfile) (`just test`, `just check`,
`just docs-serve`, `just whitepaper`). Configuration is documented via `dizzy config`.

## Issue tracking

This project uses [Seeds](https://github.com/jayminwest/seeds) for git-native issue
tracking. Run `sd ready` to find unblocked work; see [`CLAUDE.md`](CLAUDE.md).

## Use of AI

Portions of the code and commit history in this repository may be generated or
assisted by AI tools, reviewed before inclusion.

The whitepaper and other written documents under `docs/` are **authored and edited by
the maintainer**. AI may be used there only for review, fact-checking, and feedback —
not for authorship.

---

# License

See the [license](LICENSE) for more details.

```
This material was prepared as an account of work sponsored by an agency of the
United States Government.  Neither the United States Government nor the United
States Department of Energy, nor Battelle, nor any of their employees, nor any
jurisdiction or organization that has cooperated in the development of these
materials, makes any warranty, express or implied, or assumes any legal
liability or responsibility for the accuracy, completeness, or usefulness or
any information, apparatus, product, software, or process disclosed, or
represents that its use would not infringe privately owned rights.
 
Reference herein to any specific commercial product, process, or service by
trade name, trademark, manufacturer, or otherwise does not necessarily
constitute or imply its endorsement, recommendation, or favoring by the United
States Government or any agency thereof, or Battelle Memorial Institute. The
views and opinions of authors expressed herein do not necessarily state or
reflect those of the United States Government or any agency thereof.
 
                PACIFIC NORTHWEST NATIONAL LABORATORY
                             operated by
                               BATTELLE
                               for the
                  UNITED STATES DEPARTMENT OF ENERGY
                   under Contract DE-AC05-76RL01830
```
