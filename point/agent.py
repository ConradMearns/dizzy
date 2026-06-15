# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp>=1.2"]
# ///
"""point/agent.py — the shared agent Provider for the simulate spikes.

Two faces, one file:

  * Imported as a module — exposes `run_activation(...)`: stand up an ad-hoc MCP server,
    spawn an agent (`claude -p` or `pi -p`) that acts by calling the synthesized tools,
    and return what it did (recorded tool calls + final text). This is the Provider seam
    from point/PROVIDER.md; sim_executor and sim_querier both drive through it.

  * Run as `uv run agent.py serve` — IS the ad-hoc MCP server (the process the agent
    launches via its MCP config). Tools are synthesized from $SIM_TOOLS; every call is
    appended to $SIM_CALLS as {tool, kind, args} and answered with an ack/stub.

Engine differences (claude vs pi) and the clean-cwd cost trick are encapsulated here so
the spikes stay tiny. The current recording is out-of-process (a temp file the parent
reads after the run); the inline query round-trip (seed dizzy-6018 half 2) will replace
the query stub with a real sub-activation without changing this interface.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path

AGENT_SCRIPT = Path(__file__).resolve()
SERVER_NAME = "sim"

# Per-engine MCP tool name prefix. claude: mcp__<server>__<tool>; pi (scaryrawr/pi-mcp): <server>_<tool>.
TOOL_PREFIX = {"claude": f"mcp__{SERVER_NAME}__", "pi": f"{SERVER_NAME}_"}

# Haiku default for both — cheap/fast; activations follow narrow instructions.
DEFAULT_MODELS = {"claude": "claude-haiku-4-5-20251001", "pi": "anthropic/claude-haiku-4.5"}


@dataclass
class ToolSpec:
    """One synthesized tool. kind ∈ emit|dispatch|query|answer|finding.
    For a query tool, `meta` carries {"query": <name>, "description": <feat desc>} so the
    serve-side handler can run the querier sub-activation (inline round-trip)."""
    name: str
    kind: str
    meta: dict | None = None


@dataclass
class ActivationResult:
    calls: list[dict]      # recorded tool calls: {tool, kind, args}, in order
    result_text: str       # the agent's final assistant text (json result field)
    raw_stdout: str

    def of_kind(self, kind: str) -> list[dict]:
        return [c for c in self.calls if c.get("kind") == kind]


# ================================================================================
# serve mode — the ad-hoc FastMCP server (child process launched by the agent)
# ================================================================================
def serve() -> None:
    from mcp.server.fastmcp import FastMCP

    calls_path = os.environ.get("SIM_CALLS")
    specs = json.loads(os.environ.get("SIM_TOOLS", "[]"))
    # Context for inline querier sub-activations (the query_<q> round-trip):
    event_store = json.loads(os.environ.get("SIM_EVENT_STORE", "[]"))
    sub_engine = os.environ.get("SIM_ENGINE", "claude")
    sub_model = os.environ.get("SIM_MODEL") or None

    def record(tool: str, kind: str, args: dict) -> None:
        if calls_path:
            with open(calls_path, "a") as fh:
                fh.write(json.dumps({"tool": tool, "kind": kind, "args": args}) + "\n")

    # Factories: FastMCP infers the input schema from the returned function's signature,
    # so handlers expose ONLY the tool's real fields (and no param may start with '_').
    def make_emission(name: str, kind: str, ack: str):
        def handler(narrative: str) -> str:
            record(name, kind, {"narrative": narrative})
            return f"{ack}: {name}"
        return handler

    def make_query(name: str, meta: dict | None):
        qname = (meta or {}).get("query", name)
        qdesc = (meta or {}).get("description", "")

        def handler(narrative: str) -> str:
            # Inline round-trip (dizzy-6018): run a querier sub-activation over the event
            # store and return its answer INLINE. agent.py is both server and provider, so
            # the handler simply calls run_querier (which spawns its own agent) — no bridge
            # back to the parent harness is needed.
            record(name, "query", {"narrative": narrative})
            res = run_querier(query_name=qname, description=qdesc, args=narrative,
                              event_store=event_store, engine=sub_engine, model=sub_model)
            record(name, "query_answer", {"query": qname, "outcome": res["outcome"],
                                          "answer": res.get("answer"), "finding": res.get("finding")})
            if res["outcome"] == "answered":
                return res["answer"]
            if res["outcome"] == "finding":
                return f"UNANSWERABLE — finding filed: {res['finding'].get('summary', '')}"
            return "UNANSWERABLE — querier returned nothing (null-query-response finding filed)"
        return handler

    def make_answer(name: str):
        def handler(answer: str) -> str:
            record(name, "answer", {"answer": answer})
            return "answer recorded; end your turn"
        return handler

    def make_finding(name: str):
        def handler(category: str, summary: str, detail: str) -> str:
            record(name, "finding", {"category": category, "summary": summary, "detail": detail})
            return "finding recorded; end your turn without emitting unless the outcome is logically deducible"
        return handler

    mcp = FastMCP(SERVER_NAME)
    for spec in specs:
        name, kind = spec["name"], spec["kind"]
        if kind in ("emit", "dispatch"):
            verb = "Emit" if kind == "emit" else "Dispatch"
            handler = make_emission(name, kind, "recorded" if kind == "emit" else "queued")
            desc = f"{verb} {name}. `narrative`: free-text payload describing the fact/intent."
        elif kind == "query":
            handler, desc = make_query(name, spec.get("meta")), f"Run {name}. `narrative`: what you need to know from the event stream."
        elif kind == "answer":
            handler, desc = make_answer(name), "Return the query result. `answer`: the concise, direct answer derived from the event stream."
        else:  # finding
            handler, desc = make_finding(name), "Report a gap instead of healing it (missing/ambiguous/unanswerable). End your turn after."
        mcp.add_tool(handler, name=name, description=desc)

    mcp.run(transport="stdio")


# ================================================================================
# provider API — run one activation through an agent subprocess
# ================================================================================
def allowed_tools(engine: str, tools: list[ToolSpec]) -> list[str]:
    """Engine-prefixed allowlist (rule 2: tools from wiring only)."""
    return [TOOL_PREFIX[engine] + t.name for t in tools]


def _server_entry(calls_file: Path, tools: list[ToolSpec], ctx: dict) -> dict:
    return {
        "command": "uv", "args": ["run", str(AGENT_SCRIPT), "serve"],
        "env": {"SIM_CALLS": str(calls_file), "SIM_TOOLS": json.dumps([asdict(t) for t in tools]),
                **ctx},  # SIM_EVENT_STORE / SIM_ENGINE / SIM_MODEL for inline queriers
    }


def _claude_setup(model, calls_file, tools, system_prompt, user_prompt, ctx) -> tuple[list[str], Path]:
    config = {"mcpServers": {SERVER_NAME: _server_entry(calls_file, tools, ctx)}}
    cmd = [
        "claude", "-p", "--model", model, "--output-format", "json",
        "--strict-mcp-config", "--mcp-config", json.dumps(config),
        "--allowedTools", *allowed_tools("claude", tools),
        "--append-system-prompt", system_prompt, user_prompt,
    ]
    # Clean temp cwd: skip CLAUDE.md/.claude auto-discovery (halves cost), keeps OAuth.
    return cmd, Path(tempfile.mkdtemp(prefix="sim_claude_"))


def _pi_setup(model, calls_file, tools, system_prompt, user_prompt, ctx) -> tuple[list[str], Path]:
    workdir = Path(tempfile.mkdtemp(prefix="sim_pi_"))
    entry = {**_server_entry(calls_file, tools, ctx), "tools": [t.name for t in tools]}
    (workdir / ".mcp.json").write_text(json.dumps({SERVER_NAME: entry}))
    cmd = [
        "pi", "-p", "--model", model, "--mode", "json",
        "--tools", ",".join(allowed_tools("pi", tools)),
        "--append-system-prompt", system_prompt, user_prompt,
    ]
    return cmd, workdir


_SETUPS = {"claude": _claude_setup, "pi": _pi_setup}


def _result_text(engine: str, stdout: str) -> str:
    """The agent's final assistant text. claude: the json `result` field. pi: best-effort
    (its --mode json is a verbose stream; the answer tool carries the payload anyway)."""
    if not stdout.strip():
        return ""
    if engine == "claude":
        try:
            return (json.loads(stdout).get("result") or "").strip()
        except json.JSONDecodeError:
            return stdout.strip()
    return ""


def run_activation(
    *, engine: str, model: str | None, system_prompt: str, user_prompt: str,
    tools: list[ToolSpec], event_store: list[str] | None = None,
    on_call=None, timeout: int = 300,
) -> ActivationResult:
    """Spawn the agent to play one activation; return its recorded tool calls + final text.
    `event_store` (narrative facts) is passed through to the serve process so query_<q>
    tools can answer inline via a querier sub-activation (dizzy-6018).

    `on_call(call)` — if given, is invoked LIVE for each tool call as the serve process
    records it (the calls file is tailed while the subprocess runs), giving real-time
    visibility into an otherwise silent multi-second activation."""
    if engine not in _SETUPS:
        raise ValueError(f"unknown engine {engine!r} (have {list(_SETUPS)})")
    model = model or DEFAULT_MODELS[engine]

    ctx = {"SIM_EVENT_STORE": json.dumps(event_store or []), "SIM_ENGINE": engine, "SIM_MODEL": model}
    calls_file = Path(tempfile.mkstemp(prefix="sim_calls_", suffix=".jsonl")[1])
    calls_file.write_text("")
    out_file = Path(tempfile.mkstemp(prefix="sim_out_", suffix=".txt")[1])
    cmd, cwd = _SETUPS[engine](model, calls_file, tools, system_prompt, user_prompt, ctx)
    env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}

    # Popen + tail the calls file so on_call sees each tool call live. stdout → a temp file
    # (not PIPE) so a verbose stream can't deadlock the buffer while we poll.
    seen, deadline = 0, time.monotonic() + timeout
    with open(out_file, "w") as out:
        proc = subprocess.Popen(cmd, stdout=out, stderr=subprocess.DEVNULL, cwd=cwd, env=env, text=True)
        while True:
            rc = proc.poll()
            if on_call:
                lines = calls_file.read_text().splitlines()
                for line in lines[seen:]:
                    if line.strip():
                        on_call(json.loads(line))
                seen = len(lines)
            if rc is not None:
                break
            if time.monotonic() > deadline:
                proc.kill()
                break
            time.sleep(0.12)

    stdout = out_file.read_text()
    calls = [json.loads(line) for line in calls_file.read_text().splitlines() if line.strip()]
    calls_file.unlink(missing_ok=True)
    out_file.unlink(missing_ok=True)
    return ActivationResult(calls=calls, result_text=_result_text(engine, stdout), raw_stdout=stdout)


# ================================================================================
# querier sub-activation (jmQ collapse, rule 10) — the read side
# ================================================================================
QUERIER_SYSTEM_PROMPT = (
    "You are a QUERIER in an event-sourced system (the jmQ collapse). Answer the query "
    "using ONLY the event stream provided — it is the single source of truth; there are "
    "no other facts and no database. Do not invent or assume anything not derivable from "
    "the stream. Call exactly one tool: `answer` with a concise, direct result derived "
    "from the stream, or `report_finding` if the stream genuinely cannot answer. Do not "
    "reply in prose — always call a tool."
)


def build_querier_prompt(query_name: str, description: str, args: str, event_store: list[str]) -> str:
    dump = "\n".join(f"  - {e}" for e in event_store) if event_store else "  (empty — no facts yet)"
    return (
        f"query: {query_name}\n"
        f"description: {description}\n"
        f"arguments: {args}\n\n"
        f"event stream (all facts to date):\n{dump}\n\n"
        f"Answer the query from the stream above by calling `answer` or `report_finding`."
    )


def run_querier(
    *, query_name: str, description: str, args: str, event_store: list[str],
    engine: str = "claude", model: str | None = None,
) -> dict:
    """Run a querier sub-activation over the event stream. Returns
    {outcome: answered|finding|null, answer?, finding?} per the resolved querier protocol
    (PLAN § Query evaluation): a NULL turn (no tool) is itself the null outcome."""
    tools = [ToolSpec("answer", "answer"), ToolSpec("report_finding", "finding")]
    result = run_activation(
        engine=engine, model=model, system_prompt=QUERIER_SYSTEM_PROMPT,
        user_prompt=build_querier_prompt(query_name, description, args, event_store), tools=tools,
    )
    answers, findings = result.of_kind("answer"), result.of_kind("finding")
    if answers:
        return {"outcome": "answered", "answer": answers[0]["args"]["answer"]}
    if findings:
        return {"outcome": "finding", "finding": findings[0]["args"]}
    return {"outcome": "null"}


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        serve()
    else:
        print("point/agent.py is a library + an MCP server. Use `serve`, or import run_activation.",
              file=sys.stderr)
        sys.exit(2)
