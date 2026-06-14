# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp>=1.2", "pyyaml>=6.0"]
# ///
"""sim_executor spike — spawn an agent subprocess that PLAYS one component of a
feature-file and acts by calling tools on an ad-hoc FastMCP server.

The component (procedure or policy), its description, and its wiring are read from the
feat; tools are synthesized per the mirror rule (point/PLAN.md):
  procedure: trigger = command, tools = query_<q>* + emit_<event>*   + report_finding
  policy:    trigger = event,   tools = query_<q>* + dispatch_<cmd>* + report_finding
A procedure never gets a dispatch_ tool; a policy never gets an emit_ tool.

Two modes:
  * `serve` — run the stdio FastMCP server the agent launches (via its MCP config). The
              tool set is passed in via $SIM_TOOLS; handlers append each call to
              $SIM_CALLS and return an ack/answer to the agent.
  * (default) — synthesize tools from the feat, spawn the agent (`claude -p`/`pi -p`)
              pointed at this script in serve mode, then print the recorded tool calls.

Run:  uv run point/try_sim_executor.py                              # claude, haiku, catalog_book
      uv run point/try_sim_executor.py --component lend_book --trigger "Ada asks to borrow SICP"
      uv run point/try_sim_executor.py --engine pi                  # pi (requires pi-mcp extension)
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

SERVER_NAME = "sim"
DEFAULT_FEAT = Path(__file__).resolve().parent / "library.feat.yaml"

# Default models per engine. Haiku for the main component call — cheap + fast; the
# component is following a narrow procedure, not doing open-ended reasoning.
DEFAULT_MODELS = {
    "claude": "claude-haiku-4-5-20251001",
    "pi": "anthropic/claude-haiku-4.5",  # via pi's default openrouter provider
}

# How each engine names an MCP tool once registered. claude: mcp__<server>__<tool>;
# pi (scaryrawr/pi-mcp extension): <server>_<tool>.
TOOL_PREFIX = {"claude": f"mcp__{SERVER_NAME}__", "pi": f"{SERVER_NAME}_"}


# ================================================================================
# tool synthesis from the feat (the mirror rule, point/PLAN.md)
# ================================================================================
def load_component(feat_path: Path, name: str) -> dict:
    """Find a component in the feat and return {name, kind, description, trigger_kind,
    trigger_name, queries, emits} — kind is 'procedure' or 'policy'."""
    feat = yaml.safe_load(feat_path.read_text())
    if name in feat.get("procedures", {}):
        c = feat["procedures"][name]
        return {
            "name": name, "kind": "procedure", "description": c.get("description", ""),
            "trigger_kind": "command", "trigger_name": c.get("command"),
            "queries": c.get("queries", []), "emits": c.get("emits", []),
        }
    if name in feat.get("policies", {}):
        c = feat["policies"][name]
        return {
            "name": name, "kind": "policy", "description": c.get("description", ""),
            "trigger_kind": "event", "trigger_name": c.get("event"),
            "queries": c.get("queries", []), "emits": c.get("emits", []),
        }
    raise SystemExit(f"component {name!r} not found in {feat_path} (procedures/policies)")


def synthesize_tools(component: dict) -> list[dict]:
    """The tool specs for this activation. Each: {name, kind}. kind in
    emit|dispatch|query|finding. Procedures emit; policies dispatch; never both."""
    tools = [{"name": f"query_{q}", "kind": "query"} for q in component["queries"]]
    out_kind = "emit" if component["kind"] == "procedure" else "dispatch"
    tools += [{"name": f"{out_kind}_{e}", "kind": out_kind} for e in component["emits"]]
    tools.append({"name": "report_finding", "kind": "finding"})
    return tools


def allowed_tools(engine: str, tools: list[dict]) -> list[str]:
    """The engine-prefixed allowlist (rule 2: tools from wiring only)."""
    return [TOOL_PREFIX[engine] + t["name"] for t in tools]


# ================================================================================
# serve mode — the ad-hoc FastMCP server (child process launched by the agent)
# ================================================================================
def serve() -> None:
    from mcp.server.fastmcp import FastMCP

    calls_path = os.environ.get("SIM_CALLS")
    tools = json.loads(os.environ.get("SIM_TOOLS", "[]"))

    def record(tool: str, args: dict) -> None:
        if calls_path:
            with open(calls_path, "a") as fh:
                fh.write(json.dumps({"tool": tool, "args": args}) + "\n")

    # Tool-handler factories. FastMCP introspects the returned function's signature for
    # the input schema, so handlers must expose ONLY the tool's real fields (no closure
    # params — and none may start with '_'); names/kind are captured by closure instead.
    def make_emission(name: str, ack: str):
        def handler(narrative: str) -> str:
            record(name, {"narrative": narrative})
            return f"{ack}: {name}"
        return handler

    def make_query(name: str):
        def handler(narrative: str) -> str:
            record(name, {"narrative": narrative})
            # Real querier sub-activation is spike dizzy-6018; stub for now.
            return "(querier not wired in this spike — treat answer as unknown)"
        return handler

    def make_finding(name: str):
        def handler(category: str, summary: str, detail: str) -> str:
            record(name, {"category": category, "summary": summary, "detail": detail})
            return "finding recorded; end your turn without emitting unless the outcome is logically deducible"
        return handler

    mcp = FastMCP(SERVER_NAME)

    for spec in tools:
        name, kind = spec["name"], spec["kind"]
        if kind in ("emit", "dispatch"):
            verb = "Emit" if kind == "emit" else "Dispatch"
            handler = make_emission(name, "recorded" if kind == "emit" else "queued")
            desc = f"{verb} {name}. `narrative`: free-text payload describing the fact/intent."
        elif kind == "query":
            handler = make_query(name)
            desc = f"Run {name}. `narrative`: what you need to know from the event stream."
        else:  # finding
            handler = make_finding(name)
            desc = "Report a design/protocol gap instead of healing it. End your turn after this."
        mcp.add_tool(handler, name=name, description=desc)

    mcp.run(transport="stdio")


# ================================================================================
# prompt + per-engine spawn setup
# ================================================================================
SYSTEM_PROMPT = (
    "You are playing a SINGLE component in an event-sourced system. You see only "
    "this component's description and the triggering message — no other domain "
    "knowledge. Act by calling exactly one of your available tools. If the "
    "description tells you what fact to record, emit it. If something is missing or "
    "ambiguous, call report_finding instead of guessing. Do not narrate; just call "
    "the tool."
)


def build_user_prompt(component: dict, trigger: str, tools: list[dict]) -> str:
    tool_names = ", ".join(t["name"] for t in tools)
    return (
        f"component: {component['name']} ({component['kind']})\n"
        f"description:\n{component['description']}\n\n"
        f"trigger ({component['trigger_kind']} {component['trigger_name']}): {trigger}\n\n"
        f"available tools: {tool_names}"
    )


def server_entry(script: Path, calls_file: Path, tools: list[dict]) -> dict:
    """The ad-hoc MCP server: launch this script in `serve` mode over stdio, passing
    the synthesized tool set and the calls-recording path through the environment."""
    return {
        "command": "uv",
        "args": ["run", str(script), "serve"],
        "env": {"SIM_CALLS": str(calls_file), "SIM_TOOLS": json.dumps(tools)},
    }


def claude_setup(script, calls_file, model, component, trigger, tools) -> tuple[list[str], Path]:
    # claude takes the MCP config inline as {"mcpServers": {...}}.
    config = {"mcpServers": {SERVER_NAME: server_entry(script, calls_file, tools)}}
    cmd = [
        "claude", "-p",
        "--model", model,
        "--output-format", "json",
        "--strict-mcp-config",  # ignore any other configured MCP servers
        "--mcp-config", json.dumps(config),
        "--allowedTools", *allowed_tools("claude", tools),
        "--append-system-prompt", SYSTEM_PROMPT,
        build_user_prompt(component, trigger, tools),
    ]
    # Run from a clean temp dir: no project CLAUDE.md / .claude settings/hooks to
    # auto-discover (the cache-creation cost driver). Keeps OAuth auth, unlike --bare.
    return cmd, Path(tempfile.mkdtemp(prefix="sim_claude_"))


def pi_setup(script, calls_file, model, component, trigger, tools) -> tuple[list[str], Path]:
    # pi (scaryrawr/pi-mcp) reads .mcp.json from the project cwd — a flat {server: entry}
    # map, no wrapper. So we drop one in a temp dir and run pi from there.
    workdir = Path(tempfile.mkdtemp(prefix="sim_pi_"))
    entry = {**server_entry(script, calls_file, tools), "tools": [t["name"] for t in tools]}
    (workdir / ".mcp.json").write_text(json.dumps({SERVER_NAME: entry}))
    cmd = [
        "pi", "-p",
        "--model", model,
        "--mode", "json",
        "--tools", ",".join(allowed_tools("pi", tools)),
        "--append-system-prompt", SYSTEM_PROMPT,
        build_user_prompt(component, trigger, tools),
    ]
    return cmd, workdir


SETUPS = {"claude": claude_setup, "pi": pi_setup}


# ================================================================================
# parent mode — spawn the agent pointed at the server above
# ================================================================================
def drive(engine: str, model: str, feat: Path, component_name: str, trigger: str) -> None:
    script = Path(__file__).resolve()
    component = load_component(feat, component_name)
    tools = synthesize_tools(component)

    calls_file = Path(tempfile.mkstemp(prefix="sim_calls_", suffix=".jsonl")[1])
    calls_file.write_text("")  # truncate

    cmd, cwd = SETUPS[engine](script, calls_file, model, component, trigger, tools)

    print(f"=== {component['name']} ({component['kind']}) via {engine} (model: {model}) ===", file=sys.stderr)
    print(f"=== synthesized tools: {[t['name'] for t in tools]} ===", file=sys.stderr)
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=cwd)

    print(f"=== {engine} stdout ===")
    print(proc.stdout.strip() or "(empty)")
    if proc.stderr.strip():
        print(f"=== {engine} stderr ===", file=sys.stderr)
        print(proc.stderr.strip(), file=sys.stderr)

    print("\n=== recorded tool calls ===")
    recorded = calls_file.read_text().strip()
    print(recorded or f"(none — {engine} did not call a tool)")
    calls_file.unlink(missing_ok=True)

    sys.exit(0 if recorded else 1)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        serve()
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("--engine", choices=SETUPS, default="claude")
        parser.add_argument("--model", default=None, help="override the per-engine default model")
        parser.add_argument("--feat", type=Path, default=DEFAULT_FEAT)
        parser.add_argument("--component", default="catalog_book")
        parser.add_argument(
            "--trigger",
            default='One copy of "Structure and Interpretation of Computer Programs" arrives',
            help="narrative payload of the triggering command (procedure) or event (policy)",
        )
        args = parser.parse_args()
        drive(args.engine, args.model or DEFAULT_MODELS[args.engine],
              args.feat, args.component, args.trigger)
