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
├── Harness        — main loop: phased drain, activation dispatch, budget, quiescence
├── Activation     — one exchange: prompt shape, tool list, validate, execute
├── QueryEvaluator — jmQ collapse: sub-activation over event store for each query
└── CLI (typer)    — `load` (from scratch) and `resume` (from session file)
```

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

## Session log format (JSONL)

Every line is `{id, parentId, type, ...}`. Entry types from the roleplay:

| Type | When | Key fields |
|---|---|---|
| `header` | Run start | `format_version`, `feat`, `scenario`, `level`, `query_mode`, `step_budget` |
| `context` | After header | `givens`, `materialized` — scenario context entering the event store |
| `injection` | Scenario command injected | `queue`, `message`, `narrative` |
| `activation` | Component activated | `step`, `component`, `kind`, `trigger`, `tools`, `played_by` |
| `tool_call` | Component calls a tool | `component`, `tool`, `args`, `verdict` |
| `query_answer` | Querier answers | `query`, `answer`, `provenance` |
| `emission` | Event emitted or command dispatched | `step`, `event`/`command`, `narrative`, `queued` |
| `finding` | report_finding called | `step`, `component`, `category`, `summary`, `status` |
| `ruling` | Director decides protocol question | `by`, `question`, `decision` |
| `resolution` | Director resolves a finding | `resolves`, `by`, `category`, `decision`, `argument_as_stated` |
| `branch` | Counterfactual fork | `reason`, `feat_revision`, `scenario_revision`, parentId points at fork node |
| `activation_end` | Activation finishes | `step`, `component`, `emissions`, `outcome` |
| `halt` | Run ends | `reason`, `steps_used`, `event_store`, `findings` |

Tree invariant: every entry (except header) has a `parentId` pointing at the entry
that caused it. This gives us the execution DAG for free.

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

```
load(feat, scenario):
    session = SessionLog(session_path)
    write header
    materialize context → event_store
    budget = step_budget
    cmd_queue = []       # scenario commands not yet injected
    evt_queue = []       # emitted events waiting for policy drain
    pending_cmds = []    # remaining scenario commands

    while budget > 0:
        # Phase 1: drain events through policies
        while evt_queue:
            event = evt_queue.pop(0)
            for policy in feat.policies_for_event(event.name):
                if budget <= 0: break
                result = activate_policy(policy, event)
                for emission in result.emissions:
                    if emission.kind == EVENT:
                        evt_queue.append(emission)   # may trigger more policies
                    elif emission.kind == COMMAND:
                        cmd_queue.append(emission)
                budget -= 1

        # Phase 2: drain commands through procedures
        while cmd_queue:
            command = cmd_queue.pop(0)
            proc = feat.procedure_for_command(command.name)
            if proc is None:
                # Undeclared command → finding
                log finding, continue
            result = activate_procedure(proc, command)
            for emission in result.emissions:
                if emission.kind == EVENT:
                    evt_queue.append(emission)
                elif emission.kind == COMMAND:
                    cmd_queue.append(emission)
            budget -= 1

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

```
activate(component, trigger):
    # Rule 11: first-execution gate
    if execution_count[component.name] == 0:
        pause → Director reviews description
        if amended:
            record ruling + feat revision
        # proceed

    # Synthesize tool list from wiring (rule 2)
    tools = []
    for query in component.queries:     tools.append(f"query_{query}")
    for emit  in component.emits:       tools.append(f"emit_{emit}")
    for cmd   in component.dispatches:  tools.append(f"dispatch_{cmd}")
    tools.append("report_finding")      # always available (rule 3)

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

At level 0, all queries are answered by a querier sub-activation:

```
evaluate_query(query_name, args, event_store):
    query_def = feat.queries[query_name]
    querier_prompt = f"""
      Query: {query_def.description}
      Arguments: {args}
      Event stream (all facts to date):
      {event_store.dump()}

      Answer the query from the stream. If the stream cannot answer →
      respond with "report_finding".
    """
    answer = llm_activation(querier_prompt)
    # In virtual mode: LLM reads the stream and answers
    # In real mode later: run the projection + model query
    return answer
```

No projections are applied, no models are materialized — the event store *is* the
state (rule 10). This means feature-files may omit `j`/`m`/`Q` early in design and
declare only `q`.

## Scenario format

```yaml
description: >
  What this scenario exercises and what outcome is expected.

context:
  - Givens: things a technician set up before the story.
  - These are materialized as pre-existing events in the store.
  - Example: Minting Server codes, pre-existing Test User.

commands:
  - command_name: narrative payload
  - command_name: narrative payload
```

The `context` section is materialized into the event store before the first command.
Commands are injected one at a time (ruling, run 1) — run to quiescence before the
next.

The `point/` scenario copy added an `events:` key (structured pre-existing facts) —
this is a possible evolution for when events have definitions. For now the virtual
path uses `context:` only (narrative givens).

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
