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
    """One synthesized tool. kind ∈ emit|dispatch|query|answer|finding."""
    name: str
    kind: str


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

    def make_query(name: str):
        def handler(narrative: str) -> str:
            record(name, "query", {"narrative": narrative})
            return "(querier not wired in this spike — treat answer as unknown; seed dizzy-6018)"
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
            handler, desc = make_query(name), f"Run {name}. `narrative`: what you need to know from the event stream."
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


def _server_entry(calls_file: Path, tools: list[ToolSpec]) -> dict:
    return {
        "command": "uv", "args": ["run", str(AGENT_SCRIPT), "serve"],
        "env": {"SIM_CALLS": str(calls_file), "SIM_TOOLS": json.dumps([asdict(t) for t in tools])},
    }


def _claude_setup(model, calls_file, tools, system_prompt, user_prompt) -> tuple[list[str], Path]:
    config = {"mcpServers": {SERVER_NAME: _server_entry(calls_file, tools)}}
    cmd = [
        "claude", "-p", "--model", model, "--output-format", "json",
        "--strict-mcp-config", "--mcp-config", json.dumps(config),
        "--allowedTools", *allowed_tools("claude", tools),
        "--append-system-prompt", system_prompt, user_prompt,
    ]
    # Clean temp cwd: skip CLAUDE.md/.claude auto-discovery (halves cost), keeps OAuth.
    return cmd, Path(tempfile.mkdtemp(prefix="sim_claude_"))


def _pi_setup(model, calls_file, tools, system_prompt, user_prompt) -> tuple[list[str], Path]:
    workdir = Path(tempfile.mkdtemp(prefix="sim_pi_"))
    entry = {**_server_entry(calls_file, tools), "tools": [t.name for t in tools]}
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
    tools: list[ToolSpec], timeout: int = 300,
) -> ActivationResult:
    """Spawn the agent to play one activation; return its recorded tool calls + final text."""
    if engine not in _SETUPS:
        raise ValueError(f"unknown engine {engine!r} (have {list(_SETUPS)})")
    model = model or DEFAULT_MODELS[engine]

    calls_file = Path(tempfile.mkstemp(prefix="sim_calls_", suffix=".jsonl")[1])
    calls_file.write_text("")
    cmd, cwd = _SETUPS[engine](model, calls_file, tools, system_prompt, user_prompt)

    env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd, env=env)

    calls = [json.loads(line) for line in calls_file.read_text().splitlines() if line.strip()]
    calls_file.unlink(missing_ok=True)
    return ActivationResult(calls=calls, result_text=_result_text(engine, proc.stdout), raw_stdout=proc.stdout)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        serve()
    else:
        print("point/agent.py is a library + an MCP server. Use `serve`, or import run_activation.",
              file=sys.stderr)
        sys.exit(2)
