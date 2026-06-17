# PLAN — executors & emitters (the virtual/real matrix)

How the harness runs a component and represents a payload are **two independent dials**.
Keeping them orthogonal is what lets a single scenario mix LLM-played components with
real compiled handlers, and string payloads with schema-backed ones — and migrate one
piece at a time from virtual to real without rewriting the loop.

This doc plans the `try_*` spikes that prove each dial before the real harness
(`point/sim.py`) is built. It extends `point/PLAN.md` (the loop) and `point/PROVIDER.md`
(the agent-subprocess provider).

## The dials

Three independent dials. Executor and emitter are the write side (run a component, shape
its output); querier is the read side. Each flips sim→real per element, independently.

### Axis 1 — Executor (how a component runs)

A component (procedure or policy) is activated by an **executor**. Both honor the *same*
contract — the duality from PLAN's "mirror rule" means one contract covers procedure and
policy alike:

```
execute(component, trigger) -> ActivationResult(emissions=[...], findings=[...])
```

- **sim_executor** — spawn an LLM agent that *plays* the component from its description
  and acts via tool calls. This is `point/sim_executor.py`. Cheap to author (no code), the
  whole point of level-0 design validation.
- **lib_executor** — run the component's **real handler code** (generated or
  hand-written; Python, TypeScript, Rust, or any compiled artifact). The trigger goes in,
  the handler runs its actual logic, and its `emit`/`dispatch` calls are captured as
  emissions. No LLM. This is `lib_executor.py`.

Both produce the identical `ActivationResult`, so the harness loop never branches on which
executor ran a component.

### Axis 2 — Emitter (how a command/event payload is represented & validated)

A **command or event is constructed and validated by an emitter** — this is PLAN's
`command_factory` / `event_factory` hook, named:

- **sim_emitter** — the payload is a **narrative string**. No schema. Identity wrapper.
  Level 0. What every payload is today.
- **lib_emitter** — the payload is a **typed object validated against the real dizzy
  schema** (the generated LinkML/Pydantic contract for that message type). Constructing
  one with the wrong shape fails here, exactly as it would in production. Level ≥ 1.

The emitter is chosen **per message type** (per command/event name), not per run: any one
event can be schema-real while its neighbor is still a string.

### Axis 3 — Querier (how a component reads state)

Procedures and policies read state through **queries** (`context.query.<q>` in the
generated lib; a `query_<q>` tool in the sim path). A query is answered by a **querier**,
the read-side counterpart to the executor — and it has the same sim/real split:

- **sim_querier** (the jmQ collapse, PLAN rule 10) — when a run is all-simulated, there
  are no projections and no models; the event store *is* the state. So the querier is an
  LLM sub-activation: feed it the query description + args + the **full emitted event
  stream**, and it answers from the stream. Its tool stack is `answer` + `report_finding`,
  and a turn that calls **neither** (a NULL response) is itself synthesized into a
  `null-query-response` finding — a query must always resolve to an answer or a finding
  (proven necessary by the spike: an LLM tends to explain-in-prose instead of signalling
  "unanswerable"; PLAN § Query evaluation). On the sim_executor path this is the inline
  `query_<q>` round-trip (seed dizzy-6018): the MCP handler runs the sub-activation and
  returns the answer inline to the component.
- **lib_querier** — the real data loop: `Events → Projections → Models → Queries`. The
  generated query handler reads a **materialized Model** through its adapter (e.g. sqla),
  not the raw stream. That requires a **deployment** (a database), projection handlers run
  over the event history to build the model, and only then the query handler executes.

The querier is chosen per run/component the same way the executor is: a component run
under sim_executor uses sim_querier; under lib_executor it uses lib_querier.

### lib_querier needs deployment planning (deferred — not priority yet)

lib_querier is heavier than emit/dispatch and must be **planned before it's built**,
because a query reads a *model*, not the event stream, and the model only exists once a
deployment materializes it:

1. **A model store / DB** — the deployment characteristic. The demos use in-memory
   SQLite via `SqlaAdapter`; a real run might use a persistent adapter. The querier is
   meaningless without one.
2. **Projection application** — events must be folded into the model first (the data
   loop). Open question: does the lib_executor own running projections over the event
   history, or is there a separate **projection_executor** that builds model state which
   the querier then reads? (Mirrors the executor/emitter split — likely its own dial.)
3. **The read path** — the generated query handler + its read adapter, given a populated
   model, returning a typed `Output`. Then `context.query.<q>` in lib_executor is
   backed by this instead of being unwired.

**Boundary today:** `lib_executor` wires `context.emit` only. Query-bearing
components (e.g. `library.notify_next_on_return`, whose context has a `query` field)
cannot run yet — the executor reports a clean finding rather than crashing, pending
lib_querier. The all-emit components (lib_min, guestbook, library `record_hold`) run fully.

## The matrix

Executor (per component) × emitter (per message type) — both dials are per-element, so a
run is a *mixture*, not a single cell:

```
                    sim_emitter (string)        lib_emitter (schema)
                 ┌────────────────────────────┬────────────────────────────┐
 sim_executor    │ level 0: LLM plays it,      │ level 1: LLM plays it, but  │
 (LLM agent)     │ emits narrative strings     │ its emissions are validated │
                 │ (sim_executor today)             │ against real schemas        │
                 ├────────────────────────────┼────────────────────────────┤
 lib_executor    │ real handler, but fed/emit  │ real handler on real        │
 (compiled lib)  │ string payloads (bridging   │ payloads — production-      │
                 │ a half-migrated design)     │ faithful execution          │
                 └────────────────────────────┴────────────────────────────┘
```

The migration story: a design starts entirely in the **top-left** (all sim/sim). As it is
built out, individual components flip sim→lib executor and individual message types flip
sim→lib emitter — independently. The harness keeps running the whole time on whatever
mixture currently exists. That mixture *is* the project's progress bar.

## Routing (what makes a mixed run work)

The harness needs, per element, to know which side of each dial it's on:

- **Per message type** → emitter: does this command/event have a real dizzy schema?
  If yes → `lib_emitter` (validate); if no → `sim_emitter` (string). Drawn from whether
  the feat's `def/` schema exists for that name (or an explicit scenario annotation).
- **Per component** → executor: is there real handler code wired for this procedure/
  policy? If yes → `lib_executor`; if no → `sim_executor`. Drawn from a lib manifest /
  config the run is given.

Scenarios may therefore carry **both** real and faked commands/events at once (the user's
requirement). `events:` and `commands:` entries that name schema-real types are
materialized/injected as validated payloads; the rest stay narrative strings. Expectations
are routed the same way: a real emission can be asserted structurally; a string emission
is asserted narratively (shape/topology, per PLAN's testing strategy).

## The spikes (build order)

1. **`sim_executor.py`** (done) — spawn agent (claude or pi) → ad-hoc MCP → record tool
   calls; reads the component from the feat and synthesizes tools per the mirror rule.
   Provider/MCP plumbing now factored into `point/agent.py`. (Originally `try_mcp.py`.)
2. **`lib_executor.py`.** Mirror `sim_executor`'s shape, but instead of an LLM,
   invoke real handler code. Open a local **emit endpoint** (FastAPI/HTTP — the
   cross-language lingua franca, the same role the MCP server plays for the LLM path); the
   handler subprocess `POST`s its emissions/dispatches back, the harness records them.
   Prove it with a trivial hand-written handler in **one** language first (Python), then
   confirm the same HTTP contract works for a compiled artifact (TS/Rust) — the language
   is behind the subprocess boundary, so the executor stays language-agnostic.
3. **`sim_emitter` + `lib_emitter`.** Factor payload construction out of both executors
   into an emitter interface. `sim_emitter` = today's string wrap; `lib_emitter` =
   construct + validate against the dizzy-generated schema for the named type. A per-type
   registry picks the emitter.
4. **Matrix wiring.** Feed both executors through both emitters; add the per-type /
   per-component routing above; run a **mixed** scenario (some real commands/events, some
   faked) end-to-end and route expectations accordingly. This is the deliverable that
   justifies the whole two-axis design.

Querier spikes sit alongside these (read side):
- **`sim_querier`** — the inline `query_<q>` round-trip on `sim_executor` (seed
  dizzy-6018): the MCP handler runs an LLM sub-activation over the emitted event stream
  and returns the answer inline. Proves the riskiest unproven sim piece.
- **`lib_querier`** — deferred (seed dizzy-…, low priority): needs the deployment plan in
  "lib_querier needs deployment planning" above (DB, projection application, read adapter)
  before any code. Until then, `lib_executor` reports a clean finding for
  query-bearing components.

Only after the matrix is proven do we return to the main `point/sim.py` architecture in
PLAN — now with executor, emitter, and querier as settled seams rather than guesses.

## Why HTTP for lib_executor (and MCP for sim_executor)

Both executors need the component to *call back out* to record an emission. The LLM path
needs tool-calling semantics → MCP. The lib path just needs an RPC the handler can make in
any language → plain HTTP (FastAPI). They are the same idea (an emit sink the component
posts to, recorded harness-side) at two fidelities; keeping the transports separate avoids
forcing a Rust/TS handler to speak MCP just to emit an event.
