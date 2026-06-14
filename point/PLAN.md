# PLAN — `point/sim.py`

Simulator harness for `dizzy simulate`. Reads a `.feat.yaml` + scenario, runs the
phased loop, and produces a JSONL session file of findings and rulings. The session
file doubles as crash-resume state.

Based on the manual roleplay in `sim/PLAYBOOK.md` — the contract discovered there is
the spec.

## Architecture

```
point/sim.py
├── SessionLog     — JSONL writer + reader (crash-resume), entry constructors
├── EventStore     — append-only stream; queriers answer from it
├── FeatFile       — parsed feat with lookup helpers
├── Scenario       — parsed scenario; context materialization; one-at-a-time injection
├── Levers         — resolve sim-vs-real per element (emitter implicit, executor/querier explicit)
├── Executor       — run a component: sim (LLM via Provider) | lib (real handler). One contract.
├── Emitter        — build a payload: sim (string) | lib (schema-validated). One factory.
├── Querier        — answer a query: sim (jmQ over EventStore) | lib (read a Model)
├── ModelStore     — the real read-side state (e.g. sqlite); OFF at level 0 (jmQ collapse)
├── ProjectionExecutor — fold events → Model deltas to materialize ModelStore (level ≥ 2)
├── Harness        — main loop: phased drain, activation dispatch, budget, quiescence
├── Activation     — one exchange: prompt shape, tool list, validate, execute
└── CLI (typer)    — `load` (from scratch) and `resume` (from session file)
```

`Executor`/`Emitter`/`Querier`/`ProjectionExecutor` are the seams proven by the `try_*`
spikes (`point/EXECUTORS.md`); `Levers` decides which side of each is live per element.

## Virtual-first, real-later

At this stage everything is **virtual** — level-0 narrative payloads only. No schemas,
no typed contracts, no generated code. The feat file carries prose descriptions of
commands, events, procedures, policies, and queries — the harness treats them all as
narrative blobs.

| Layer | Virtual (now) | Real (later) | Hook |
|---|---|---|---|
| **Commands** | Narrative string in scenario | Generated Pydantic/typed payload | `command_factory(name, narrative)` → `Command` — returns narrative wrapper now, typed instance later |
| **Events** | Narrative string in emission | Generated Pydantic/typed payload | `event_factory(name, narrative)` → `Event` — same pattern |
| **Procedures** | Harness prompt + LLM activation | Real procedure handler (imported/generated) | `activate_procedure(component, trigger)` — dispatches to LLM now, calls handler later |
| **Policies** | Harness prompt + LLM activation | Real policy handler | `activate_policy(component, trigger)` — same dispatch point |
| **Queries** | Querier sub-activation over event store | Generated projection + model query | `evaluate_query(name, args, event_store)` — LLM-subactivation now, model query later |
| **Projections** | Skipped (rule 10: jmQ collapse) | Apply event → model delta | `apply_projection(event)` — no-op now, real projection later |

**The contract**: every hook point takes the same inputs and returns the same output
shape whether virtual or real. The harness loop doesn't care which side of the hook
is active — it just calls `activate_procedure(...)` and gets back emissions or findings.

**How a virtual activation is driven**: by spawning a Claude that plays the component
and lets it *call tools* against an ad-hoc MCP server the harness stands up — emissions,
dispatches, queries, and findings are all tool calls. This is abstracted behind a
**Provider** seam (default = `claude` CLI subprocess). See `point/PROVIDER.md` for the
full design; the rest of this plan treats `activate(...)` as a black box that returns an
`ActivationResult`.

**Two dials behind the hook table** — `point/EXECUTORS.md`: the *executor* (how a
component runs: `sim_executor` = LLM agent, today's `sim_executor.py`; `lib_executor` = real
compiled handler) and the *emitter* (how a payload is represented: `sim_emitter` =
narrative string, `lib_emitter` = schema-validated dizzy payload). They are orthogonal
and chosen per-element, so one scenario can mix real and faked commands/events. The
`Commands`/`Events`/`Procedures`/`Policies` rows above are emitter and executor seams
respectively. We prove each dial with `try_*` spikes before building `sim.py` proper.

## Levers & levels (selecting sim vs real per element)

Fidelity is not one global knob — each dial is set **per element**, and the *control* for
each lever differs by what information is actually available:

- **Emitter (events & commands) — IMPLICIT, from the scenario data shape.** A scenario
  `events:`/`commands:` entry is either a **string** (narrative → `sim_emitter`) or a
  **mapping/object** (structured → `lib_emitter`, validated against the `def/` schema for
  that name). The harness picks the emitter by `isinstance(value, str)` vs `dict` at
  materialization/injection — no extra config. One scenario can carry both forms for the
  same message type (the `point/` scenario already does). For payloads *emitted during a
  run*, the producing executor decides: a `lib_executor` yields a typed object, a
  `sim_executor` a string (or a schema-conformant object at level 1).
- **Executor (procedures & policies) — EXPLICIT, from a lib manifest.** The scenario
  carries triggers, never handler code, so the executor lever can't be inferred from it.
  It is set by **whether real lib code is wired** for that component (the `libconfig.yaml`
  / generated `lib/<runtime>/<kind>/<name>` package, plus an implemented handler). Wired ⇒
  `lib_executor`; absent ⇒ `sim_executor` (LLM plays it). Default is sim; you opt a
  component into real code by implementing it. This is the project's progress bar.
- **Querier (queries) — EXPLICIT, same basis as the executor.** A real model + projection
  + query handler (lib) ⇒ `lib_querier` (reads the Model); otherwise `sim_querier` (jmQ
  collapse over the EventStore). Default sim.

### Fidelity levels, restated as lever combinations

- **Level 0** — all sim. Strings everywhere; `sim_executor`, `sim_querier`; **no models,
  no projections** (rule 10). The EventStore is the only state. A bare feat (no `def/`)
  supports only this.
- **Level 1** — schema-conformant payloads. `lib_emitter` validates emissions against
  `def/` schemas, but execution may still be sim. Gated on authored `def/`.
- **Level 2** — stateful / real read side. `lib_querier` + a live `ModelStore`:
  projections materialize models so queries read real state (below). Requires the data
  loop to be wired.

### Model construction (projection → model → querier)

At level 0 this subsystem is **entirely off** — the jmQ collapse means the minimal model
*is* the event store, so we never build one. It switches on only when a **`lib_querier`**
is selected, and then the real data loop must be materialized:

1. **A `ModelStore`** — a real database the host owns (the demos use in-memory SQLite via
   `SqlaAdapter`; a run could use a persistent one). Meaningless to query without it.
2. **`ProjectionExecutor`** — projections are pure `event → model delta` (they emit
   nothing). When an event is committed to the EventStore, the harness folds it through
   the projections subscribed to it, mutating the `ModelStore`. This is a *third* kind of
   activation, parallel to procedure/policy but writing to models, not the queues. It runs
   in the event-drain phase (below), gated by level.
3. **`lib_querier` reads** — the generated query handler + its read adapter answer from the
   now-materialized `ModelStore`, returning a typed `Output`.

So a real `projection → model → querier` path over SQLite is: events land in the store →
`ProjectionExecutor` updates SQLite tables → `lib_querier` runs the query against them.
The same query under `sim_querier` skips all of that and reads the raw event stream. Both
satisfy the identical `answer_query(name, args)` contract — the Querier lever swaps which
runs. (Full deployment design: `point/EXECUTORS.md` § lib_querier; seed dizzy-4ed2.)

## Session log format (JSONL)

Every line is `{id, parentId, type, ...}`. Entry types from the roleplay:

| Type | When | Key fields |
|---|---|---|
| `header` | Run start | `format_version`, `feat`, `scenario`, `level`, `step_budget`, `engine`/`model`, `levers` (per-element sim/lib manifest) |
| `context` | After header | `givens`, `materialized` — scenario context entering the event store |
| `injection` | Scenario command injected | `queue`, `message`, `narrative`/`payload`, `emitter` (sim/lib) |
| `activation` | Component activated | `step`, `component`, `kind`, `executor` (sim/lib), `trigger`, `tools`, `played_by` |
| `tool_call` | Component calls a tool | `component`, `tool`, `kind` (emit/dispatch/query/answer/finding), `args`, `verdict` |
| `query_answer` | Querier resolves a query | `query`, `querier` (sim/lib), `outcome` (`answered`/`finding`/`null`), `answer`, `provenance` |
| `emission` | Event emitted or command dispatched | `step`, `event`/`command`, `emitter` (sim/lib), `narrative` *or* `payload`, `queued` |
| `finding` | report_finding (or synthesized) | `step`, `component`, `category`, `summary`, `status`, `source` (`reported`/`null-query-response`/…) |
| `ruling` | Director decides protocol question | `by`, `question`, `decision` |
| `resolution` | Director resolves a finding | `resolves`, `by`, `category`, `decision`, `argument_as_stated` |
| `branch` | Counterfactual fork | `reason`, `feat_revision`, `scenario_revision`, parentId points at fork node |
| `activation_end` | Activation finishes | `step`, `component`, `emissions`, `outcome` |
| `halt` | Run ends | `reason`, `steps_used`, `event_store`, `findings` |
| `projection` | *(level ≥ 2, deferred)* event folded into a model | `step`, `projection`, `event`, `model`, `delta` |
| `model_state` | *(level ≥ 2, deferred)* model snapshot | `model`, `state` (one JSON blob per Model) |

Tree invariant: every entry (except header) has a `parentId` pointing at the entry
that caused it. This gives us the execution DAG for free.

**Provenance of the lever** is now a first-class field on the entries that have a
sim/real choice (`activation.executor`, `emission.emitter`, `query_answer.querier`,
`injection.emitter`). This is what lets the session honestly record a *mixed* run — a
`lib_executor` activation next to a `sim_executor` one — and lets a reader see which
facts came from real code vs an LLM. A `narrative` (string) emission is a `sim_emitter`
fact; a `payload` (object) emission is a `lib_emitter` fact — the field present *is* the
lever, mirroring the implicit emitter-selection rule.

### Readiness — what's specified vs deferred

Enough to build the **SessionLog + a level-0 run today**: the table, the tree invariant,
the crash-resume reconstruction below, and a complete worked example
(`sim/sessions/borrow_available_book__1.jsonl`, 60+ lines covering header→halt, two
findings, seven rulings, a branch, and verification) pin the level-0 shape concretely.
The lever-provenance and querier-`outcome` fields above are small, additive, and known
now (we just built the executors/querier), so they go in from the first version. The
`projection`/`model_state` entries are **deferred** to the projection-executor /
lib_querier work (seeds dizzy-9d88, dizzy-4ed2) — they only exist at level ≥ 2, and
`format_version` lets us add them without breaking level-0 logs. So: yes for level 0/1,
with the level-2 entries blocked on the same work that produces them.

## Crash-resume

The session file is the resume checkpoint. `resume` replays the JSONL to reconstruct:

1. **Event store** — every `emission` with `queued: event` whose event has been fully
   drained (no pending policy activations are mid-flight)
2. **Command queue** — every `emission` with `queued: command` + remaining scenario
   `injection`s not yet issued
3. **Event queue** — events emitted but not yet drained through policies
4. **Step count** — max `step` seen so far
5. **Budget remaining** — `step_budget - steps_used`
6. **Findings** — accumulated `finding` entries
7. **Execution counts** — per-component activation count (for rule-11 gate)
8. **Current phase** — are we draining events, draining commands, or waiting for next injection?

The harness picks up exactly where it left off.

## Harness loop (the phased drain)

```py
load(feat, scenario):
    session = SessionLog(session_path)
    write header
    materialize context → event_store
    budget = step_budget
    cmd_queue = []       # scenario commands not yet injected
    evt_queue = []       # emitted events waiting for policy drain
    pending_cmds = []    # remaining scenario commands

    while budget > 0:
        budget -= 1

        # Phase 1: drain events — materialize models, then react via policies
        while evt_queue:
            event = evt_queue.pop(0)
            event_store.append(event)
            # 1a. Projection drain (model construction). No-op at level 0 (jmQ collapse,
            #     rule 10); at level ≥ 2 folds the event into the ModelStore so lib_queriers
            #     read real state. Projections emit nothing — they only update models.
            for projection in feat.projections_for_event(event.name):
                apply_projection(projection, event, model_store)   # gated by level
            # 1b. Policy drain (reactivity). Policies dispatch commands (never events).
            for policy in feat.policies_for_event(event.name):
                result = activate_policy(policy, event)
                for emission in result.emissions:
                    cmd_queue.append(emission)

        # Phase 2: drain commands through procedures
        while cmd_queue:
            command = cmd_queue.pop(0)
            for proc in feat.procedure_for_command(command.name)
                result = activate_procedure(proc, command)
                for emission in result.emissions:
                    evt_queue.append(emission)

        # Phase 3: inject next scenario command
        if not evt_queue and not cmd_queue and pending_cmds:
            cmd = pending_cmds.pop(0)
            log injection
            cmd_queue.append(cmd)
            continue

        # Quiescence check
        if not evt_queue and not cmd_queue and not pending_cmds:
            log halt (quiescence)
            break

    if budget <= 0:
        log halt (budget exhausted)

    session.close()
```

### Resume loop

```
resume(session_path, feat, scenario):
    session = SessionLog(session_path)
    state = session.replay()   # reconstruct queues, store, budget, phase
    # Continue the main loop from state.phase with state.queues, state.budget
```

## Activation protocol

The mechanics below (tool synthesis, validation, the call loop) are realized through
the **Provider + ad-hoc MCP** described in `point/PROVIDER.md`: "await_component_response"
is the Provider streaming the next tool call from the spawned Claude, and each
`emit_/dispatch_/query_/report_finding` branch is the matching MCP tool *handler*.

```py
activate(component, trigger):
    # Rule 11: first-execution gate
    if execution_count[component.name] == 0:
        pause → Director reviews description
        if amended:
            record ruling + feat revision
        # proceed

    # Synthesize tool list from wiring (rule 2). Procedures and policies are MIRRORS
    # (see "Procedure/policy duality" below) and NEVER mix output kinds:
    #   procedure: trigger = command, outputs = events only   → emit_<event>
    #   policy:    trigger = event,   outputs = commands only  → dispatch_<command>
    # A procedure gets no dispatch_ tool; a policy gets no emit_ tool. The wiring
    # graph cannot express a mixed-output component, so the gap is structural.
    tools = []
    for query in component.queries:       tools.append(f"query_{query}")
    if component.kind == PROCEDURE:
        for event in component.emits:     tools.append(f"emit_{event}")
    elif component.kind == POLICY:
        for command in component.emits:   tools.append(f"dispatch_{command}")  # policy.emits names commands
    tools.append("report_finding")        # always available (rule 3)

    # Present activation
    record activation entry
    step += 1
    execution_count[component.name] += 1

    # Component responds (in virtual mode: LLM call)
    while True:
        call = await_component_response()
        if not call: break  # activation ended

        validate_tool(call.tool, tools)  # rule 2
        record tool_call entry

        if call.tool == "report_finding":
            record finding entry
            pause → Director ruling (rule 6)
            if ruling says stop: break   # rule 7: no speculative emits
            continue

        if call.tool.startswith("query_"):
            answer = evaluate_query(call.tool, call.args, event_store)
            record query_answer entry
            # answer is returned inline to the component (sync sub-activation)
            continue

        if call.tool.startswith("emit_"):
            event = event_factory(call.tool, call.args)
            record emission entry (queued: event)
            emissions.append(event)
            continue

        if call.tool.startswith("dispatch_"):
            command = command_factory(call.tool, call.args)
            record emission entry (queued: command)
            emissions.append(command)
            continue

    record activation_end entry
    return ActivationResult(emissions=emissions, findings=findings)
```

## Procedure/policy duality (the mirror rule)

Procedures and policies are the **same machine reflected**. One activation protocol
serves both; only the trigger source and the output kind flip:

| | Procedure | Policy |
|---|---|---|
| Triggered by | a **command** (from the command queue) | an **event** (from the event queue) |
| May query | yes (`query_<name>`) | yes (`query_<name>`) |
| Output kind | **events** (`emit_<event>`) | **commands** (`dispatch_<command>`) |
| Output queue | emissions → **event** queue | emissions → **command** queue |
| May report a finding | yes | yes |

**Outputs never mix.** A procedure cannot dispatch a command; a policy cannot emit an
event. This is enforced *structurally*, not by prompt: tool synthesis (above) hands a
procedure only `emit_` tools and a policy only `dispatch_` tools, so the disallowed call
has no tool to call (rule 2). In the feat schema both declare their outputs under
`emits:` — for a procedure those names resolve to events, for a policy to commands; the
harness reads the names through the component's `kind`. The phased loop is the same
symmetry seen from the scheduler: Phase 1 drains events through policies into the command
queue, Phase 2 drains commands through procedures into the event queue.

This duality is why a single `activate(component, trigger)` covers both, and why the
later `lib_executor` (real handlers) needs only one execution contract, not two.

## Termination & safety

- **Step budget** (default 30): each activation (procedure, policy, or querier) costs 1
- **Repetition guard**: same component activated on same message shape 3× → halt with
  `possible-livelock` finding (rule 5)
- **report_finding pauses** (rule 6): every finding checkpoints to Director before
  proceeding — never build on wrong assumption
- **No speculative emits** (rule 7): can't logically deduce → end activation without
  emitting; emits alongside findings allowed only for deducible branches
- **A finding ends an activation, not the run** (rule 8): collect all findings,
  resolve at run end

## Query evaluation (jmQ collapse, rule 10)

At level 0, a query is answered by a querier sub-activation over the EventStore. The
querier is an activation **like any other** (PROVIDER.md): it acts by calling tools, and
its tool stack is exactly two —

- `answer(result)` — return the query result (a string at level 0; the typed `Output` at
  level ≥ 1). This is the structured success outcome.
- `report_finding` — the stream cannot answer (rule 10 failure mode). Always present,
  same as every other activation.

**A query MUST resolve to one of those two.** Critically, *a query that returns nothing
is itself a problem*: if the querier ends its turn having called **no tool at all** (a
NULL response — neither `answer` nor `report_finding`), the harness synthesizes a
`report_finding` on its behalf (`category: null-query-response`). A silent non-answer is
never allowed to look like an empty answer — it is a finding. (This is the protocol fix
for the spike observation that an LLM tends to *explain in prose* that it can't answer
instead of signalling it; `answer`-vs-`report_finding`-vs-NULL makes the outcome
unambiguous for the calling component. Seed dizzy-6018.)

```py
answer_query(query_name, args):
    query_def = feat.queries[query_name]
    if lever.querier(query_name) == LIB:
        return lib_querier(query_def, args, model_store)   # read materialized Model
    # sim_querier (jmQ): tools = [answer, report_finding]
    result = activate_querier(query_def, args, event_store.dump())
    if result.answered:        return result.answer
    if result.finding:         return Finding(result.finding)
    return Finding(category="null-query-response", query=query_name)  # NULL → finding
```

At level 0 no projections run and no models exist — the event store *is* the state
(rule 10). Feature-files may omit `j`/`m`/`Q` early and declare only `q`; selecting a
`lib_querier` (level ≥ 2) is what brings the ModelStore + ProjectionExecutor online
(see "Model construction" above).

## Scenario format

```yaml
description: >
  What this scenario exercises and what outcome is expected.

context:
  - >
    Givens: things a technician set up before the story.
  - >
    Example: Minting Server codes, pre-existing Test User.

events:
    - event_name: narrative payload - past tense fact
    - event_name: narrative payload - past tense fact

commands:
  - command_name: narrative payload - intent of system or user
  - command_name: narrative payload - intent of system or user
```

Three sections, three jobs — and a deliberate split between them:

- **`events:`** — pre-existing **state**. Anything the story assumes already happened is
  a past-tense fact and is expressed as an event, materialized into the event store
  before the first command. This is the rule: *state is events*. The store is the only
  state (rule 10), so the only honest way to seed state is to seed the facts that
  produced it. Queriers cite these exactly as they cite emitted facts.
- **`context:`** — givens that are **not** events: out-of-model setup a technician
  arranged that the design does not (and should not) model — e.g. the Minting Server SS
  code assignments. If a "given" can be phrased as a past-tense fact about the domain, it
  belongs in `events:`, not here. `context:` is the escape hatch for the genuinely
  un-modeled, kept small on purpose.
- **`commands:`** — the stimulus, injected one at a time (ruling, run 1); run to
  quiescence before the next.

The earlier "pre-existing Test User" given migrates from `context:` to `events:` (a
`member_registered` fact) under this rule; only the non-event SS-code assignment stays
in `context:`. When events gain real schemas (`lib_emitter`), `events:` entries become
schema-backed payloads while still-virtual ones stay strings — see `point/EXECUTORS.md`.

## Building order (this implementation)

1. **SessionLog** — JSONL write + read + replay. The foundational layer; everything
   else writes through it.
2. **EventStore** — append-only stream with provenance tracking. `dump()` for querier
   context, `add(event, provenance)` for emissions.
3. **FeatFile** — parse the `.feat.yaml`, provide lookups: `procedure_for_command(name)`,
   `policies_for_event(name)`, `query_def(name)`, etc.
4. **Scenario** — parse scenario YAML, materialize context → event store entries,
   yield commands one at a time.
5. **Activation + QueryEvaluator** — the virtual activation protocol (LLM call with
   prompt shape from component description). In virtual mode this calls out to an LLM
   (or accepts manual input for now). The hook is clean: `activate(component, trigger)`
   returns `ActivationResult`.
6. **Harness** — the main loop, wired to SessionLog + EventStore + FeatFile + Scenario.
7. **CLI** — `load` and `resume` commands.

## Testing strategy

- Smoke test: `load sim/library.feat.yaml sim/scenarios/borrow_available_book.scenario.yaml`
  should produce a session file matching the shape (entry types, tree structure) of
  `sim/sessions/borrow_available_book__1.jsonl`.
- Resume test: kill a run mid-activation, `resume` from session file, verify it
  continues from the correct point.
- The session file is the snapshot — diff the entry types and tree topology, not the
  LLM-generated narrative content.
