# sim/ — Simulate Roleplay Playbook

We dry-run `dizzy simulate` **by hand** before writing it. Human + agent play the
harness and the component LLMs against a real feature-file, following the rules the
real harness will enforce. The experiment has two products:

1. **Findings about the design** (`library.feat.yaml`) — exactly what a real run would emit.
2. **Findings about simulate itself** — the prompt shape, the tool-call protocol, the
   query semantics, the session-log format. These feed back into plan `pl-f395`.

Requirements being exercised: `docs/cli.md § dizzy simulate`.

## Cast

- **Harness** (Claude): owns the queues, the phased loop, tool synthesis, validation,
  the session log, and the step budget. The harness has no opinions about the domain.
- **Component LLM** (Claude, in role): one activation at a time, sees *only* the
  component's description, the triggering message, and its synthesized tools.
  Plays it straight — no domain knowledge beyond the prompt.
- **Director** (Conrad): picks scenarios, supplies judgment calls when the protocol
  itself is ambiguous (those are findings too), and may take over any role at will.

## Ground rules (the harness contract, enforced socially for now)

1. **Phased loop**: drain the event queue (policies + projections), then the command
   queue (procedures), repeat. One legal interleaving; no concurrency claims.
2. **Tools from wiring only**: an activation may only call tools synthesized from its
   declared wiring — `emit_<event>` per declared emit, `dispatch_<command>` per policy
   emit, `query_<name>` per declared query. No tool, no emission.
3. **`report_finding` always available**: missing slot, ambiguous description,
   undecidable branch, unanswerable query. **Never heal a gap** — report it. The
   deliberate trap in `fulfill_reservation_on_return` is there to be caught.
4. **Level 0 first**: narrative payloads (prose), no schemas. Level 1 (slot-conformant)
   only after a level-0 run completes.
5. **Termination**: step budget **30**; repetition rule — same component activated on
   the same message shape **3** times → stop, record `possible-livelock` finding.
6. **Pause on `report_finding`** (ruling, run 1): every finding checkpoints to the
   Director before the activation proceeds — never build on a wrong assumption.
7. **No speculative emits** (ruling, run 1): an activation that cannot logically deduce
   an outcome ends without emitting — the command was handled, no fact was produced.
   Emitting alongside a finding is allowed only for branches that *are* deducible.
8. **A finding ends an activation, not the run.** The run continues to quiescence /
   budget collecting the full findings list (the product); fixes happen at run end,
   then a branch from the pre-fix node verifies them under the amended feature-file.
9. **The jmQ collapse** (ruling, run 1): at this stage projections **never activate**
   and are never logged — the simplest projection is identity, so the minimal model
   *is* the event store, and we only record events. The j→m→Q chain exists to answer
   questions, so in simulation it collapses into `q`: a query is answered by a
   **querier activation** given the query's description and full read access to the
   simulated event store (a `dj`-style regression over the stream). If the stream
   cannot answer the question → `report_finding`. Feature-files may omit j/m/Q early
   in design and declare only `q`.

## Turn protocol (the draft `--manual` contract)

Each activation is one exchange:

```
HARNESS → component:
  component: lend_book (procedure)
  description: <verbatim from feat-file>
  trigger: <message type + payload narrative>
  tools: [query_get_book_availability, query_get_next_reservation,
          emit_book_borrowed, emit_borrow_rejected, report_finding]

COMPONENT → harness (JSON, one or more calls):
  {"tool": "query_get_book_availability", "args": {...narrative...}}
  ... harness answers queries inline (see open question Q1) ...
  {"tool": "emit_book_borrowed", "args": {...narrative...}}
```

The harness validates every call (declared tool? plausible shape?), appends to the
session log, and schedules consequences.

## Open questions this roleplay must answer

- **Q1 — Query semantics. ANSWERED by the jmQ-collapse ruling (rule 9):** synchronous
  sub-activation (a), with the querier grounded in the full event store rather than
  fabricating — option (b) is moot, (c) survives as the querier's failure mode
  (stream can't answer → finding).
- **Q2 — Projections at level 0/1. ANSWERED (rule 9):** always skipped, never logged.
  Only events are recorded. Open follow-up: what level 2 means now — likely
  "materialize models as caches of the stream" rather than "state appears".
- **Q3 — Prompt sufficiency.** Are the block-scalar descriptions in `library.feat.yaml`
  enough to execute without healing? Every place the component LLM hesitates is a
  description bug — file it.
- **Q4 — Scenario format.** Is `description` + ordered `command: narrative` list enough?
  Does anything need actor identity or timing?
- **Q5 — Session log shape.** We log JSONL with `id`/`parentId` from entry one
  (pi-style tree; see plan notes) — what entry types do we actually need?

## Session logs

One file per run: `sim/sessions/<scenario>__<run>.jsonl`. Every line:
`{id, parentId, type, ...}`. Entry types (amended during run 1):
- `header` — feat-file + scenario + level + query mode + step budget + format version.
- `ruling` — a Director decision on a protocol ambiguity. **The harness stops and asks
  rather than assuming; every ruling is logged.** Rulings are simulate-protocol findings
  with their resolution attached.
- `injection` — a scenario command entering the command queue. Injection rule
  (ruling, run 1): one scenario command at a time; run to quiescence before the next.
- `activation`, `tool_call`, `query_answer`, `emission`, `finding`, `halt`.
- `activation_end` (added run 1) — closes an activation: emissions produced (possibly
  none) and outcome. Needed the moment an activation ended without emitting.

Branching a run = new entries pointing at an earlier `parentId` in the same file.
The format we converge on here seeds `dizzy-e2d4` (session file) — keep it honest.

## Runs

| # | Scenario | Level | Query mode | Status |
|---|---|---|---|---|
| 1 | borrow_available_book | 0 | (a) sub-activation over event store | **complete** — 2 findings (s7, s26), 7 rulings, halted quiescent at step 3 |
| 2 | borrow_available_book | 0 | ~~(b) harness-fabricated~~ | superseded by jmQ ruling |
| 3 | contested_reservation | 0 | (a) per rule 9 | pending |

## Exit criteria

- One scenario completed end-to-end at level 0; `contested_reservation` attempted.
- Q1–Q5 each have a written answer or a filed finding.
- Findings list reviewed; design fixes applied to `library.feat.yaml` (that's the demo:
  the artifact improved before any code existed).
- Learnings folded back into the `pl-f395` child seeds before `dizzy-3c9e` starts.
