# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0", "typer>=0.12"]
# ///
"""point/sim.py — the simulate harness.

Executes a `.feat.yaml` + scenario as `session = system(session)` over a single Session
object (PLAN.md § "The session as state"), producing an append-only JSONL session file
that is BOTH the human-readable trace and the crash-resume checkpoint.

Level 0: components are played by an LLM (point/agent.py Provider), queries answered by
the inline jmQ querier, payloads are narrative strings, no models/projections. The dials
(executor/emitter/querier sim-vs-real) are seams already proven by the spikes; this wires
them into the phased drain.

  load   <feat> <scenario> <session.jsonl>   — run from scratch
  resume <session.jsonl>                      — continue from the last checkpoint
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
REPETITION_LIMIT = 3  # rule 5: same component + message shape this many times → livelock halt


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

    givens: list[str] = field(default_factory=list)        # context: non-event setup
    event_store: list[dict] = field(default_factory=list)   # [{name, narrative}] facts to date
    evt_queue: list[dict] = field(default_factory=list)     # events awaiting drain
    cmd_queue: list[dict] = field(default_factory=list)     # commands awaiting drain
    pending_cmds: list[dict] = field(default_factory=list)  # scenario commands not yet injected

    step: int = 0
    budget: int = 30
    findings: list[dict] = field(default_factory=list)
    exec_counts: dict = field(default_factory=dict)         # component → activation count (rule 11)
    rep_counts: dict = field(default_factory=dict)          # (component, msg) → count (rule 5)
    cursor: str | None = None                               # parentId for the next entry = last non-halted node
    halted: bool = False
    halt_reason: str | None = None

    # ---- querier context: the stream a sim_querier reasons over ----
    def stream_dump(self) -> list[str]:
        return list(self.givens) + [f"{e['name']}: {e['narrative']}" for e in self.event_store]

    # ---- live-state checkpoint (for resume): the serialized session ----
    def checkpoint(self) -> dict:
        return {
            "givens": self.givens, "event_store": self.event_store,
            "evt_queue": self.evt_queue, "cmd_queue": self.cmd_queue, "pending_cmds": self.pending_cmds,
            "step": self.step, "budget": self.budget, "findings": self.findings,
            "exec_counts": self.exec_counts, "rep_counts": {f"{k[0]}|{k[1]}": v for k, v in self.rep_counts.items()},
            "cursor": self.cursor, "halted": self.halted, "halt_reason": self.halt_reason,
        }

    def restore(self, cp: dict) -> None:
        for k in ("givens", "event_store", "evt_queue", "cmd_queue", "pending_cmds",
                  "step", "budget", "findings", "exec_counts", "cursor", "halted", "halt_reason"):
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
def activate(session: Session, log: SessionLog, component: dict, trigger: dict) -> tuple[list[dict], list[dict]]:
    """Play `component` against `trigger` (a {name, narrative} command/event). Returns
    (emissions, findings). Emissions are {name, narrative, kind: event|command}."""
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

    user_prompt = ex.build_user_prompt(
        {**component, "trigger_name": trigger["name"]}, trigger_narr, tools)
    if session.givens:  # context givens are available to ANY activation (ruling c2)
        givens = "\n".join(f"  - {g}" for g in session.givens)
        user_prompt += f"\n\ncontext (technician setup available to all activations):\n{givens}"
    result = agent.run_activation(
        engine=session.engine, model=session.model, system_prompt=ex.SYSTEM_PROMPT,
        user_prompt=user_prompt, tools=tools, event_store=session.stream_dump())

    emissions, findings = [], []
    for call in result.calls:
        kind = call.get("kind")
        if kind in ("emit", "dispatch"):
            ev = call["tool"].split("_", 1)[1]
            emitted = {"name": ev, "narrative": call["args"].get("narrative", ""),
                       "kind": "event" if kind == "emit" else "command"}
            e = log.append("emission", session.cursor, step=session.step,
                           **{("event" if kind == "emit" else "command"): ev},
                           emitter="sim", narrative=emitted["narrative"],
                           queued=emitted["kind"])
            session.cursor = e["id"]
            emissions.append(emitted)
        elif kind == "query":
            t = log.append("tool_call", session.cursor, component=name, tool=call["tool"],
                           kind="query", args=call["args"], verdict="valid")
            session.cursor = t["id"]
        elif kind == "query_answer":
            qa = log.append("query_answer", session.cursor, query=call["args"]["query"],
                            querier="sim", outcome=call["args"]["outcome"],
                            answer=call["args"].get("answer"), provenance=["event stream"])
            session.cursor = qa["id"]
        elif kind == "finding":
            f = log.append("finding", session.cursor, step=session.step, component=name,
                           source="reported", **call["args"], status="open")
            session.cursor = f["id"]
            findings.append(call["args"])
            session.findings.append({"id": f["id"], **call["args"]})

    end = log.append("activation_end", session.cursor, step=session.step, component=name,
                     emissions=[e["name"] for e in emissions],
                     outcome="fact(s) recorded" if emissions else "no fact produced")
    session.cursor = end["id"]
    return emissions, findings


# ================================================================================
# system(session) — one advance of the phased drain
# ================================================================================
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
    """Advance the phased drain by one unit; append to the log; return the session."""
    if session.budget <= 0:
        return _halt(session, log, "budget exhausted")

    # Phase 1: drain one event — (projections: no-op at level 0) then policies
    if session.evt_queue:
        event = session.evt_queue.pop(0)
        session.event_store.append({"name": event["name"], "narrative": event["narrative"]})
        for policy in policies_for_event(session.feat, event["name"]):
            if session.budget <= 0:
                break
            if _repetition_halt(session, log, policy["name"], event["name"]):
                return session
            emissions, _ = activate(session, log, policy, event)
            for em in emissions:  # policies dispatch commands
                session.cmd_queue.append(em)
        return session

    # Phase 2: drain one command through its procedure
    if session.cmd_queue:
        command = session.cmd_queue.pop(0)
        proc = procedure_for_command(session.feat, command["name"])
        if proc is None:
            f = log.append("finding", session.cursor, step=session.step, component=command["name"],
                           source="reported", category="undeclared-command",
                           summary=f"no procedure handles command {command['name']!r}", status="open")
            session.cursor = f["id"]
            session.findings.append({"id": f["id"], "category": "undeclared-command"})
            return session
        if _repetition_halt(session, log, proc["name"], command["name"]):
            return session
        emissions, _ = activate(session, log, proc, command)
        for em in emissions:  # procedures emit events
            session.evt_queue.append(em)
        return session

    # Phase 3: inject the next scenario command (one at a time)
    if session.pending_cmds:
        cmd = session.pending_cmds.pop(0)
        inj = log.append("injection", session.cursor, queue="command",
                         message=cmd["name"], narrative=cmd["narrative"], emitter="sim")
        session.cursor = inj["id"]
        session.cmd_queue.append(cmd)
        return session

    # Quiescence
    return _halt(session, log, "quiescence — scenario exhausted, both queues empty")


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
    """A scenario list item is a single-key mapping {name: narrative|object}."""
    (name, value), = item.items()
    return name, value


def _narrative(value) -> str:
    return value if isinstance(value, str) else json.dumps(value)


def materialize(session: Session, log: SessionLog) -> None:
    """Context givens + pre-existing events enter the store; commands queue as pending."""
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
    while not session.halted:
        session = system(session, log)
        log.append("checkpoint", None, state=session.checkpoint())  # serialized session for resume
    return session


def _summary(session: Session) -> None:
    print(f"\n=== halt: {session.halt_reason} ===")
    print(f"steps used: {session.step}/{session.step_budget}")
    print("event store:")
    for e in session.event_store:
        print(f"  - {e['name']}: {e['narrative']}")
    print(f"findings: {len(session.findings)}")
    for f in session.findings:
        print(f"  - {f.get('id')} {f.get('category')}: {f.get('summary', '')}")


# ================================================================================
# CLI
# ================================================================================
@app.command()
def load(feat_file: Path, scenario_file: Path,
         session_path: Path = typer.Argument(Path("point/session.jsonl")),
         level: int = 0, engine: str = "claude", model: str = typer.Option(None), budget: int = 30):
    """Run a feature-file + scenario from scratch into a fresh session file."""
    feat = yaml.safe_load(feat_file.read_text())
    scenario = yaml.safe_load(scenario_file.read_text())
    session = Session(feat_path=str(feat_file), scenario_path=str(scenario_file),
                      session_path=str(session_path), level=level, engine=engine, model=model,
                      step_budget=budget, budget=budget, feat=feat, scenario=scenario)
    log = SessionLog(session_path)
    h = log.append("header", None, format_version=FORMAT_VERSION, feat=str(feat_file),
                   scenario=str(scenario_file), level=level, step_budget=budget,
                   engine=engine, model=model)
    session.cursor = h["id"]
    materialize(session, log)
    run(session, log)
    _summary(session)


@app.command()
def resume(session_path: Path):
    """Continue a run from the last checkpoint in its session file."""
    lines = [json.loads(l) for l in session_path.read_text().splitlines() if l.strip()]
    header = next(e for e in lines if e["type"] == "header")
    checkpoints = [e for e in lines if e["type"] == "checkpoint"]
    if not checkpoints:
        raise SystemExit("no checkpoint to resume from")
    feat = yaml.safe_load(Path(header["feat"]).read_text())
    scenario = yaml.safe_load(Path(header["scenario"]).read_text())
    session = Session(feat_path=header["feat"], scenario_path=header["scenario"],
                      session_path=str(session_path), level=header["level"], engine=header["engine"],
                      model=header.get("model"), step_budget=header["step_budget"],
                      feat=feat, scenario=scenario)
    session.restore(checkpoints[-1]["state"])
    if session.halted:
        print(f"session already halted: {session.halt_reason}")
        return
    log = SessionLog(session_path, resume=True)
    run(session, log)
    _summary(session)


if __name__ == "__main__":
    app()
