# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
"""sim_executor spike — spawn an agent that PLAYS one component of a feature-file and
acts by calling tools (point/EXECUTORS.md). The agent-spawn + ad-hoc MCP plumbing lives
in point/agent.py (the shared Provider); this file only reads the component from the
feat, synthesizes its tools per the mirror rule, and presents the result.

  procedure: trigger = command, tools = query_<q>* + emit_<event>*   + report_finding
  policy:    trigger = event,   tools = query_<q>* + dispatch_<cmd>* + report_finding

Run:  uv run point/sim_executor.py                              # claude, haiku, catalog_book
      uv run point/sim_executor.py --component lend_book --trigger "Ada asks to borrow SICP"
      uv run point/sim_executor.py --engine pi                  # pi (requires pi-mcp extension)
"""

import argparse
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import agent  # noqa: E402  (point/agent.py — the shared Provider)

DEFAULT_FEAT = Path(__file__).resolve().parent / "library.feat.yaml"


def load_component(feat_path: Path, name: str) -> dict:
    """Find a component and return its kind, description, trigger, and wiring."""
    feat = yaml.safe_load(feat_path.read_text())
    if name in feat.get("procedures", {}):
        c = feat["procedures"][name]
        return {"name": name, "kind": "procedure", "description": c.get("description", ""),
                "trigger_kind": "command", "trigger_name": c.get("command"),
                "queries": c.get("queries", []), "emits": c.get("emits", [])}
    if name in feat.get("policies", {}):
        c = feat["policies"][name]
        return {"name": name, "kind": "policy", "description": c.get("description", ""),
                "trigger_kind": "event", "trigger_name": c.get("event"),
                "queries": c.get("queries", []), "emits": c.get("emits", [])}
    raise SystemExit(f"component {name!r} not found in {feat_path} (procedures/policies)")


def synthesize_tools(component: dict) -> list[agent.ToolSpec]:
    """Tools per the mirror rule: procedures emit; policies dispatch; never both."""
    tools = [agent.ToolSpec(f"query_{q}", "query") for q in component["queries"]]
    out_kind = "emit" if component["kind"] == "procedure" else "dispatch"
    tools += [agent.ToolSpec(f"{out_kind}_{e}", out_kind) for e in component["emits"]]
    tools.append(agent.ToolSpec("report_finding", "finding"))
    return tools


SYSTEM_PROMPT = (
    "You are playing a SINGLE component in an event-sourced system. You see only "
    "this component's description and the triggering message — no other domain "
    "knowledge. Act by calling exactly one of your available tools. If the "
    "description tells you what fact to record, emit it. If something is missing or "
    "ambiguous, call report_finding instead of guessing. Do not narrate; just call "
    "the tool."
)


def build_user_prompt(component: dict, trigger: str, tools: list[agent.ToolSpec]) -> str:
    return (
        f"component: {component['name']} ({component['kind']})\n"
        f"description:\n{component['description']}\n\n"
        f"trigger ({component['trigger_kind']} {component['trigger_name']}): {trigger}\n\n"
        f"available tools: {', '.join(t.name for t in tools)}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", choices=list(agent.DEFAULT_MODELS), default="claude")
    parser.add_argument("--model", default=None)
    parser.add_argument("--feat", type=Path, default=DEFAULT_FEAT)
    parser.add_argument("--component", default="catalog_book")
    parser.add_argument("--trigger",
                        default='One copy of "Structure and Interpretation of Computer Programs" arrives')
    args = parser.parse_args()

    component = load_component(args.feat, args.component)
    tools = synthesize_tools(component)

    print(f"=== {component['name']} ({component['kind']}) via {args.engine} ===", file=sys.stderr)
    print(f"=== synthesized tools: {[t.name for t in tools]} ===", file=sys.stderr)

    result = agent.run_activation(
        engine=args.engine, model=args.model, system_prompt=SYSTEM_PROMPT,
        user_prompt=build_user_prompt(component, args.trigger, tools), tools=tools,
    )

    print("=== recorded tool calls ===")
    if result.calls:
        for call in result.calls:
            print(json.dumps(call))
    else:
        print(f"(none — {args.engine} did not call a tool)")
    sys.exit(0 if result.calls else 1)


if __name__ == "__main__":
    main()
