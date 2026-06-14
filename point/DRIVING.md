# Driving `point/sim.py` (for a claude/pi wrapper agent)

`sim.py` is a **stepper**, not an autonomous Director. You — the wrapping agent — drive it
and act as the Director's interface to the human. The loop is small:

```
run:   uv run point/sim.py load <feat> <scenario> <session.jsonl>
        ├─ exit 0  + "STATUS: HALT" → done: review findings with the user (below)
        └─ exit 10 + "STATUS: GATE" → a never-simulated component needs review (below)
```

`load` **continues** an existing `<session.jsonl>` (it never overwrites), so re-running the
same command after a gate or a crash resumes from the last checkpoint.

## On `STATUS: GATE` (first-execution review, rule 11)

sim.py paused *before* running a procedure/policy that has never been simulated, and
printed its verbatim description + wired tools. Do this:

1. Show the user the component name and its description. Ask: **does this description have
   real executable substance** — a concrete action, the facts it should emit, the branches
   it decides? (The point is to catch an empty/wrong description before it accumulates
   facts in the event log.)
2. Record the decision, then continue:
   - **User approves as-is:**
     `uv run point/sim.py gate <session.jsonl> <component> --confirm`
   - **User wants changes:** edit the description in `<feat>` yourself per their guidance,
     then `uv run point/sim.py gate <session.jsonl> <component> --modified "<what changed>"`
3. Re-run the same `load …` command. Repeat until `STATUS: HALT`.

Only proceed automatically on `--confirm`. On `--modified`, make the feat edit first.

## On `STATUS: HALT`

The run reached quiescence or the step budget. sim.py prints the final event store and the
**findings list** — that is the product of the run. For each finding, review it with the
user and (when the design/protocol question is settled) record the resolution and its
*argument as stated* (rule 9 — record, don't design). Resolution categories:
`design-change` (amend the feat, re-run to verify), `insufficient-context` (amend the
scenario's `context`), `unreviewed-component` (the gate above).

## Notes

- Each component activation shells out to the `claude`/`pi` CLI; `borrow_book`-style
  components fan out to a querier sub-activation per query, so full runs take real
  time/money. Start a new feat with a cheap one-command scenario.
- The session file is the single source of truth: the human-readable trace **and** the
  resume checkpoint. `tail -f <session.jsonl>` to watch a run live.
- `--engine pi`, `--model <id>`, `--budget N` are available on `load`.
