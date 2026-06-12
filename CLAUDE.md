# DIZZY — project guide

DIZZY is a methodology + code generator for event-sourced software. A feature is
declared in a single `.feat.yaml` file (the **feature-file** — the API of the whole
ecosystem); `dizzy generate` turns it into LinkML schemas, typed contracts, and
per-runtime implementation-stub packages. Two loops define the model:

```
Commands → Procedures → Events → Policies  → Commands   (reactivity loop)
Events   → Projections → Models → Queries  → Procedures (data loop)
```

Core thesis: the design lives in the artifact, never in an LLM context window.

## Tree of knowledge

This is a map, not a reading list — pull in only what your task needs. Ordered by
how often a task needs them:

1. **`README.md`** — what/why, install, minimal feature, the three-stage workflow.
2. **`docs/cli.md`** — CLI manpage **and roadmap**. The canonical end-state: every
   command section is the requirements doc for that command. Seeds reference these
   sections. Printed by `dizzy docs`. *Keep this file authoritative — when scope
   changes, change it here first, then update seeds.*
3. **`docs/authoring.md`** — agent guide for writing features: components, `.feat.yaml`
   shape, what you author after each stage, generated layout, import conventions.
   Printed by `dizzy docs authoring`.
4. **`docs/SPECIFICATION.md`** — the `.feat.yaml` format spec.
5. **`examples/guestbook/`** — a fully generated *and implemented* feature with a
   runnable demo.
6. **`dizzy/src/dizzy/`** — implementation: `cli.py` (verbs), `feat_schema.py` /
   `libconfig_schema.py` (generated — edit `dizzy/src/dizzy/def/*.yaml` and run
   `just gen-feat-pydantic` / `just gen-libconfig-pydantic` instead), `generators/`.
7. **`docs/whitepaper.typ`, `docs/architecture.typ`, `docs/PNF.md`** — theory and
   rationale. Maintainer-authored: AI may review/fact-check these, never author them.

## CLI at a glance

- `dizzy generate definitions|static|libraries <feat> <out>` — the shipped pipeline
  (legacy aliases: `def`/`gen`/`lib`).
- `dizzy docs [cli|authoring]` — print documentation; `dizzy config` — config template.
- Roadmap commands (`lint`, `diff`, `impact`, `simulate`, …) are specified in
  `docs/cli.md` and tracked as seeds.

## Conventions & boundaries

- The two doc pages in `docs/` are symlinked into the package
  (`dizzy/src/dizzy/docs/`) so they ship in the wheel — edit the `docs/` copies.
- Visualization and runtime-observability work (`trace`, `drift`, graph rendering)
  lives in a **separate repo**. Don't build or seed it here.
- Quality gates: `just test` (pytest + syrupy snapshots; `just test-update` to
  re-snapshot intentionally) and `just check` (ty).
- Gotcha: despite the Seeds section below, `sd prime` does **not** accept
  `--format` — run it bare. (`--format` works on `sd list`, `sd show`, etc.)

<!-- seeds:start -->
## Issue Tracking (Seeds)
<!-- seeds-onboard:v0.5.3 -->
<!-- seeds-onboard-schema:7 -->

This project uses [Seeds](https://github.com/jayminwest/seeds) v0.5.3 for git-native issue tracking.

**At the start of every session**, run:
```
sd prime
```

This injects session context: rules, command reference, and workflows. Pass `--format json|compact|markdown|plain|ids` on any command for agent-friendly output.

**Quick reference:**
- `sd ready` — Find unblocked work
- `sd search <query>` — Full-text search across titles + descriptions
- `sd create --title "..." --type task --priority 2` — Create issue
- `sd update <id> --status in_progress` — Claim work
- `sd close <id>` — Complete work
- `sd dep add <id> <depends-on>` — Add dependency between issues
- `sd sync` — Sync with git (run before pushing)

### Planning
Use `sd plan` when work is large or ambiguous enough that an LLM benefits from structured decomposition. Submit spawns one child seed per step; `step.blocks` uses forward semantics (step i with `blocks: [j]` means step i blocks step j, and step j gets step i's id in its `blockedBy`).

- `sd plan templates` — List built-ins (`feature`, `bug`, `refactor`) plus custom templates
- `sd plan prompt <seed-id>` — Emit a structured prompt the LLM fills in
- `sd plan submit <seed-id> --plan <file>` — Validate + spawn child seeds
- `sd plan show <pl-id>` — View sections, children, sub-plans
- `sd plan edit <id> [--name | --section <name> <text> | --step <i> --title/--priority/--type]` — In-place field edits; bumps revision
- `sd plan outcome <pl-id> --result success|partial|failure` — Record outcome (storage-only)
- `sd plan review <pl-id> --by <name>` — Record reviewer (informational)

### Before You Finish
1. Close completed issues: `sd close <id>`
2. File issues for remaining work: `sd create --title "..."`
3. Sync and push: `sd sync && git push`
<!-- seeds:end -->
