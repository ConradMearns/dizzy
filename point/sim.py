# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0", "typer>=0.12"]
# ///
"""point/sim.py — the simulate harness (driven by a wrapper agent).

Executes a `.feat.yaml` + scenario as `session = system(session)` over a single Session
object (PLAN.md § "The session as state"), producing an append-only JSONL session file
that is BOTH the human-readable trace and the crash-resume checkpoint.

This tool does NOT try to be the Director. It runs autonomously until it reaches a point
that needs human judgement — a **first-execution review gate** (rule 11): a procedure or
policy that has never been simulated. There it records a `gate` entry, checkpoints, prints
`STATUS: GATE` with the component's description + instructions, and **exits**. A wrapping
claude/pi agent asks the user to confirm or amend, records the decision with the `gate`
command, and re-runs `load` to continue. We only proceed automatically on `confirm`.

  load   <feat> <scenario> <session.jsonl>          — run; CONTINUES if the session exists
  resume <session.jsonl>                             — alias for continuing an existing session
  gate   <session.jsonl> <component> --confirm       — Director approves a first-execution gate
  gate   <session.jsonl> <component> --modified "…"   — Director amended the description (edit feat first)

Exit status: 0 = halted (quiescence/budget), 10 = paused at a gate (needs Director), 1 = error.
"""

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import typer
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import agent          # noqa: E402  — the shared Provider
import sim_executor as ex  # noqa: E402  — find_component / synthesize_tools / build_user_prompt / SYSTEM_PROMPT

app = typer.Typer(add_completion=False)
FORMAT_VERSION = 0
REPETITION_LIMIT = 3   # rule 5: same component + message shape this many times → livelock halt
EXIT_HALT, EXIT_GATE = 0, 10


# ================================================================================
# SessionLog — append-only JSONL writer (the trace + the serialized session)
# ================================================================================
class SessionLog:
    """Writes `{id, parentId, type, ...}` lines. `id` is sequential; the caller threads
    `parentId` via the session cursor so the file is a tree (the execution DAG)."""

    def __init__(self, path: Path, *, resume: bool = False):
        self.path = path
        self._n = 0
        if resume:
            self._n = max((self._seq(json.loads(l)["id"]) for l in path.read_text().splitlines() if l.strip()),
                          default=0)
        else:
            path.write_text("")

    @staticmethod
    def _seq(entry_id: str) -> int:
        return int(entry_id[1:]) if entry_id[1:].isdigit() else 0

    def append(self, type: str, parent_id: str | None, **fields) -> dict:
        self._n += 1
        entry = {"id": f"s{self._n}", "parentId": parent_id, "type": type, **fields}
        with open(self.path, "a") as fh:
            fh.write(json.dumps(entry) + "\n")
        return entry


# ================================================================================
# Session — the single state object the loop advances
# ================================================================================
@dataclass
class Session:
    feat_path: str
    scenario_path: str
    session_path: str
    level: int
    engine: str
    model: str | None
    step_budget: int

    feat: dict
    scenario: dict

    givens: list[str] = field(default_factory=list)         # context: non-event setup
    event_store: list[dict] = field(default_factory=list)   # [{name, narrative}] facts to date
    evt_queue: list[dict] = field(default_factory=list)     # events awaiting commit + policy expansion
    policy_queue: list[dict] = field(default_factory=list)  # [{event, policy}] ready policy activations
    cmd_queue: list[dict] = field(default_factory=list)     # commands awaiting procedure drain
    pending_cmds: list[dict] = field(default_factory=list)  # scenario commands not yet injected

    step: int = 0
    budget: int = 30
    findings: list[dict] = field(default_factory=list)
    exec_counts: dict = field(default_factory=dict)         # component → activation count (rules 5/11)
    reviewed: dict = field(default_factory=dict)            # component → "confirm"|"modified" (rule-11 gate cleared)
    rep_counts: dict = field(default_factory=dict)          # (component, msg) → count (rule 5)
    cursor: str | None = None                               # parentId for the next entry = last non-halted node
    halted: bool = False
    halt_reason: str | None = None
    gate: dict | None = None                                # transient: set when paused at a first-execution gate

    def stream_dump(self) -> list[str]:
        """The stream a sim_querier reasons over: givens + facts to date."""
        return list(self.givens) + [f"{e['name']}: {e['narrative']}" for e in self.event_store]

    def needs_gate(self, name: str) -> bool:
        """Rule 11: a component never simulated and not yet Director-reviewed."""
        return self.exec_counts.get(name, 0) == 0 and name not in self.reviewed

    def checkpoint(self) -> dict:
        return {
            "givens": self.givens, "event_store": self.event_store, "evt_queue": self.evt_queue,
            "policy_queue": self.policy_queue, "cmd_queue": self.cmd_queue, "pending_cmds": self.pending_cmds,
            "step": self.step, "budget": self.budget, "findings": self.findings,
            "exec_counts": self.exec_counts, "reviewed": self.reviewed,
            "rep_counts": {f"{k[0]}|{k[1]}": v for k, v in self.rep_counts.items()},
            "cursor": self.cursor, "halted": self.halted, "halt_reason": self.halt_reason,
        }

    def restore(self, cp: dict) -> None:
        for k in ("givens", "event_store", "evt_queue", "policy_queue", "cmd_queue", "pending_cmds",
                  "step", "budget", "findings", "exec_counts", "reviewed", "cursor", "halted", "halt_reason"):
            setattr(self, k, cp[k])
        self.rep_counts = {tuple(k.split("|", 1)): v for k, v in cp.get("rep_counts", {}).items()}


# ================================================================================
# feat lookups (by trigger, not by component name)
# ================================================================================
def procedure_for_command(feat: dict, cmd_name: str) -> dict | None:
    for name, c in feat.get("procedures", {}).items():
        if c.get("command") == cmd_name:
            return ex.find_component(feat, name)
    return None


def policies_for_event(feat: dict, evt_name: str) -> list[dict]:
    return [ex.find_component(feat, name)
            for name, c in feat.get("policies", {}).items() if c.get("event") == evt_name]


# ================================================================================
# activation — run one component, route its emissions/findings (the Executor seam)
# ================================================================================
def activate(session: Session, log: SessionLog, component: dict, trigger: dict) -> list[dict]:
    """Play `component` against `trigger` (a {name, narrative} command/event). Returns
    emissions ({name, narrative, kind: event|command})."""
    name = component["name"]
    tools = ex.synthesize_tools(component, session.feat.get("queries", {}))
    trigger_narr = trigger["narrative"]

    session.step += 1
    session.budget -= 1
    session.exec_counts[name] = session.exec_counts.get(name, 0) + 1
    act = log.append("activation", session.cursor, step=session.step, component=name,
                     kind=component["kind"], executor="sim", trigger=f"{trigger['name']}: {trigger_narr}",
                     tools=[t.name for t in tools], played_by=session.engine)
    session.cursor = act["id"]

    user_prompt = ex.build_user_prompt({**component, "trigger_name": trigger["name"]}, trigger_narr, tools)
    if session.givens:  # context givens are available to ANY activation (ruling c2)
        user_prompt += "\n\ncontext (technician setup available to all activations):\n" + \
                       "\n".join(f"  - {g}" for g in session.givens)
    result = agent.run_activation(
        engine=session.engine, model=session.model, system_prompt=ex.SYSTEM_PROMPT,
        user_prompt=user_prompt, tools=tools, event_store=session.stream_dump())

    emissions = []
    for call in result.calls:
        kind = call.get("kind")
        if kind in ("emit", "dispatch"):
            ev = call["tool"].split("_", 1)[1]
            emitted = {"name": ev, "narrative": call["args"].get("narrative", ""),
                       "kind": "event" if kind == "emit" else "command"}
            e = log.append("emission", session.cursor, step=session.step,
                           **{("event" if kind == "emit" else "command"): ev},
                           emitter="sim", narrative=emitted["narrative"], queued=emitted["kind"])
            session.cursor = e["id"]
            emissions.append(emitted)
        elif kind == "query":
            t = log.append("tool_call", session.cursor, component=name, tool=call["tool"],
                           kind="query", args=call["args"], verdict="valid")
            session.cursor = t["id"]
        elif kind == "query_answer":
            qa = log.append("query_answer", session.cursor, query=call["args"]["query"], querier="sim",
                            outcome=call["args"]["outcome"], answer=call["args"].get("answer"),
                            provenance=["event stream"])
            session.cursor = qa["id"]
        elif kind == "finding":
            f = log.append("finding", session.cursor, step=session.step, component=name,
                           source="reported", **call["args"], status="open")
            session.cursor = f["id"]
            session.findings.append({"id": f["id"], **call["args"]})

    end = log.append("activation_end", session.cursor, step=session.step, component=name,
                     emissions=[e["name"] for e in emissions],
                     outcome="fact(s) recorded" if emissions else "no fact produced")
    session.cursor = end["id"]
    return emissions


# ================================================================================
# system(session) — one advance of the phased drain (≤ one activation per call)
# ================================================================================
def _open_gate(session: Session, log: SessionLog, component: dict, trigger: dict) -> Session:
    """Rule 11: pause before a never-simulated component. Record + set the transient gate;
    the run loop prints STATUS: GATE and exits. The queue is NOT advanced, so re-running
    after `gate --confirm`/`--modified` re-enters here and (now reviewed) proceeds."""
    g = log.append("gate", session.cursor, step=session.step + 1, component=component["name"],
                   kind=component["kind"], trigger=f"{trigger['name']}: {trigger['narrative']}",
                   description=component["description"], tools=[
                       t.name for t in ex.synthesize_tools(component, session.feat.get("queries", {}))],
                   status="pending")
    session.cursor = g["id"]
    session.gate = {"component": component["name"], "kind": component["kind"],
                    "description": component["description"], "trigger": g["trigger"],
                    "tools": g["tools"], "entry": g["id"]}
    return session


def _repetition_halt(session: Session, log: SessionLog, component: str, msg: str) -> bool:
    key = (component, msg)
    session.rep_counts[key] = session.rep_counts.get(key, 0) + 1
    if session.rep_counts[key] >= REPETITION_LIMIT:
        f = log.append("finding", session.cursor, step=session.step, component=component,
                       source="repetition-guard", category="possible-livelock",
                       summary=f"{component} activated on the same message {REPETITION_LIMIT}× — halting",
                       status="open")
        session.cursor = f["id"]
        session.findings.append({"id": f["id"], "category": "possible-livelock"})
        return True
    return False


def system(session: Session, log: SessionLog) -> Session:
    """Advance the phased drain by ≤ one activation; append to the log; return the session."""
    if session.budget <= 0:
        return _halt(session, log, "budget exhausted")

    # EVENT PHASE — policy activations first, then commit the next event.
    if session.policy_queue:
        item = session.policy_queue[0]
        policy, event = item["policy"], item["event"]
        if session.needs_gate(policy["name"]):
            return _open_gate(session, log, policy, event)
        session.policy_queue.pop(0)
        if _repetition_halt(session, log, policy["name"], event["name"]):
            return session
        for em in activate(session, log, policy, event):   # policies dispatch commands
            session.cmd_queue.append(em)
        return session

    if session.evt_queue:
        event = session.evt_queue.pop(0)
        session.event_store.append({"name": event["name"], "narrative": event["narrative"]})
        # (projections: no-op at level 0 — jmQ collapse, rule 10)
        for policy in policies_for_event(session.feat, event["name"]):
            session.policy_queue.append({"event": event, "policy": policy})
        return session

    # COMMAND PHASE — one command through its procedure.
    if session.cmd_queue:
        command = session.cmd_queue[0]
        proc = procedure_for_command(session.feat, command["name"])
        if proc is None:
            session.cmd_queue.pop(0)
            f = log.append("finding", session.cursor, step=session.step, component=command["name"],
                           source="reported", category="undeclared-command",
                           summary=f"no procedure handles command {command['name']!r}", status="open")
            session.cursor = f["id"]
            session.findings.append({"id": f["id"], "category": "undeclared-command"})
            return session
        if session.needs_gate(proc["name"]):
            return _open_gate(session, log, proc, command)
        session.cmd_queue.pop(0)
        if _repetition_halt(session, log, proc["name"], command["name"]):
            return session
        for em in activate(session, log, proc, command):   # procedures emit events
            session.evt_queue.append(em)
        return session

    # INJECT the next scenario command, else QUIESCE.
    if session.pending_cmds:
        cmd = session.pending_cmds.pop(0)
        inj = log.append("injection", session.cursor, queue="command",
                         message=cmd["name"], narrative=cmd["narrative"], emitter="sim")
        session.cursor = inj["id"]
        session.cmd_queue.append(cmd)
        return session

    return _halt(session, log, "quiescence — scenario exhausted, all queues empty")


def _halt(session: Session, log: SessionLog, reason: str) -> Session:
    h = log.append("halt", session.cursor, reason=reason, steps_used=session.step,
                   event_store=[f"{e['name']}: {e['narrative']}" for e in session.event_store],
                   findings=[f.get("id") for f in session.findings])
    session.cursor = h["id"]
    session.halted = True
    session.halt_reason = reason
    return session


# ================================================================================
# materialization (scenario → session) and the run loop
# ================================================================================
def _entry_kv(item) -> tuple[str, object]:
    (name, value), = item.items()
    return name, value


def _narrative(value) -> str:
    return value if isinstance(value, str) else json.dumps(value)


def materialize(session: Session, log: SessionLog) -> None:
    session.givens = [g.strip() for g in session.scenario.get("context", [])]
    events = []
    for item in session.scenario.get("events", []):
        name, value = _entry_kv(item)
        events.append({"name": name, "narrative": _narrative(value),
                       "emitter": "lib" if isinstance(value, dict) else "sim"})
    ctx = log.append("context", session.cursor, givens=session.givens,
                     materialized=[f"{e['name']}: {e['narrative']}" for e in events])
    session.cursor = ctx["id"]
    session.event_store.extend({"name": e["name"], "narrative": e["narrative"]} for e in events)
    for item in session.scenario.get("commands", []):
        name, value = _entry_kv(item)
        session.pending_cmds.append({"name": name, "narrative": _narrative(value)})


def run(session: Session, log: SessionLog) -> Session:
    """Step until a gate (needs Director) or halt. Each advance writes a checkpoint."""
    while not session.halted and session.gate is None:
        session = system(session, log)
        log.append("checkpoint", None, state=session.checkpoint())
    return session


# ================================================================================
# status printing (for the wrapping agent + the human)
# ================================================================================
def _print_gate(session: Session) -> None:
    g = session.gate
    feat, scen, sp = session.feat_path, session.scenario_path, session.session_path
    print("\nSTATUS: GATE")
    print("=" * 72)
    print(f"FIRST-EXECUTION REVIEW GATE (rule 11) — {g['component']} ({g['kind']})")
    print(f"This procedure/policy has NEVER been simulated. Review its description before it")
    print(f"runs and accumulates facts. Triggered by: {g['trigger']}")
    print(f"\nDescription (verbatim from {feat}):\n")
    for line in g["description"].splitlines():
        print(f"    {line}")
    print(f"\nWired tools: {g['tools']}")
    print("\n" + "-" * 72)
    print("DIRECTOR ACTION (the wrapping agent should ask the user, then run ONE of):")
    print(f"  confirm as-is:   uv run point/sim.py gate {sp} {g['component']} --confirm")
    print(f"  amended it:      (edit the description in {feat}, then)")
    print(f"                   uv run point/sim.py gate {sp} {g['component']} --modified \"<what changed>\"")
    print(f"then continue:     uv run point/sim.py load {feat} {scen} {sp}")
    print("=" * 72)


def _print_halt(session: Session) -> None:
    print("\nSTATUS: HALT")
    print(f"reason: {session.halt_reason} | steps used: {session.step}/{session.step_budget}")
    print("event store:")
    for e in session.event_store:
        print(f"  - {e['name']}: {e['narrative']}")
    print(f"findings ({len(session.findings)}):")
    for f in session.findings:
        print(f"  - {f.get('id')} {f.get('category')}: {f.get('summary', '')}")
    if session.findings:
        print("\nThe wrapping agent should review findings with the Director and record")
        print("resolutions (design-change / insufficient-context / unreviewed-component).")


# ================================================================================
# session (de)serialization helpers shared by the CLI verbs
# ================================================================================
def _load_session(session_path: Path) -> tuple[Session, dict | None]:
    """Reconstruct a Session from an existing file's header + last checkpoint."""
    lines = [json.loads(l) for l in session_path.read_text().splitlines() if l.strip()]
    header = next(e for e in lines if e["type"] == "header")
    checkpoints = [e for e in lines if e["type"] == "checkpoint"]
    feat = yaml.safe_load(Path(header["feat"]).read_text())          # re-read: picks up amendments
    scenario = yaml.safe_load(Path(header["scenario"]).read_text())
    session = Session(feat_path=header["feat"], scenario_path=header["scenario"],
                      session_path=str(session_path), level=header["level"], engine=header["engine"],
                      model=header.get("model"), step_budget=header["step_budget"],
                      feat=feat, scenario=scenario)
    if checkpoints:
        session.restore(checkpoints[-1]["state"])
    return session, (checkpoints[-1] if checkpoints else None)


def _has_run(session_path: Path) -> bool:
    return session_path.exists() and any(
        l.strip() and json.loads(l)["type"] == "header" for l in session_path.read_text().splitlines())


def _finish(session: Session) -> None:
    if session.gate is not None:
        _print_gate(session)
        raise typer.Exit(EXIT_GATE)
    _print_halt(session)
    raise typer.Exit(EXIT_HALT)


# ================================================================================
# CLI
# ================================================================================
@app.command()
def load(feat_file: Path, scenario_file: Path,
         session_path: Path = typer.Argument(Path("point/session.jsonl")),
         level: int = 0, engine: str = "claude", model: str = typer.Option(None), budget: int = 30):
    """Run a feature-file + scenario. CONTINUES an existing session file instead of
    overwriting it (so a crash or gate is resumable by re-running the same command)."""
    if _has_run(session_path):
        session, _ = _load_session(session_path)
        if session.halted:
            print(f"session already halted: {session.halt_reason}")
            raise typer.Exit(EXIT_HALT)
        log = SessionLog(session_path, resume=True)
        _finish(run(session, log))

    feat = yaml.safe_load(feat_file.read_text())
    scenario = yaml.safe_load(scenario_file.read_text())
    session = Session(feat_path=str(feat_file), scenario_path=str(scenario_file),
                      session_path=str(session_path), level=level, engine=engine, model=model,
                      step_budget=budget, budget=budget, feat=feat, scenario=scenario)
    log = SessionLog(session_path)
    h = log.append("header", None, format_version=FORMAT_VERSION, feat=str(feat_file),
                   scenario=str(scenario_file), level=level, step_budget=budget, engine=engine, model=model)
    session.cursor = h["id"]
    materialize(session, log)
    _finish(run(session, log))


@app.command()
def resume(session_path: Path):
    """Continue a run from the last checkpoint in its session file (alias for load-continue)."""
    if not _has_run(session_path):
        raise SystemExit(f"no session to resume at {session_path}")
    session, _ = _load_session(session_path)
    if session.halted:
        print(f"session already halted: {session.halt_reason}")
        raise typer.Exit(EXIT_HALT)
    log = SessionLog(session_path, resume=True)
    _finish(run(session, log))


@app.command()
def gate(session_path: Path, component: str,
         confirm: bool = typer.Option(False, "--confirm"),
         modified: str = typer.Option(None, "--modified")):
    """Record the Director's decision on a first-execution review gate (rule 11), so the
    next `load`/`resume` proceeds past it. `--confirm` approves the description as-is;
    `--modified "<note>"` records that the description was amended (edit the feat first)."""
    if confirm == (modified is not None):
        raise SystemExit("provide exactly one of --confirm or --modified \"<note>\"")
    session, _ = _load_session(session_path)
    decision = "confirmed" if confirm else f"modified: {modified}"
    session.reviewed[component] = "confirm" if confirm else "modified"
    log = SessionLog(session_path, resume=True)
    r = log.append("ruling", session.cursor, by="director",
                   question=f"first-execution review of {component}", decision=decision,
                   category="unreviewed-component")
    session.cursor = r["id"]
    log.append("checkpoint", None, state=session.checkpoint())
    print(f"recorded: {component} {decision}")
    if confirm:
        print(f"continue: uv run point/sim.py load {session.feat_path} {session.scenario_path} {session_path}")
    else:
        print("re-read your feat amendment and continue with the same load command.")


if __name__ == "__main__":
    app()
