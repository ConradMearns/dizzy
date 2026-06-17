"""Concrete executor implementations backed by agent.run_activation (sim path).

SimProcedureExecutor  — plays a procedure component via an LLM agent; returns emitted events.
SimPolicyExecutor     — plays a policy component via an LLM agent; returns dispatched commands.

Both accept engine ("claude" | "pi") and an optional model override at construction time.
The feat dict is required so tools can be synthesized per the mirror rule.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import agent

from executor import ProcedureResult, PolicyResult

SYSTEM_PROMPT = (
    "You are playing a SINGLE component in an event-sourced system. You see only "
    "this component's description and the triggering message — no other domain "
    "knowledge. Act by calling exactly one of your available tools. If the "
    "description tells you what fact to record, emit it. If something is missing or "
    "ambiguous, call report_finding instead of guessing. Do not narrate; just call "
    "the tool."
)


def _find_component(feat: dict, name: str, kind: str) -> dict:
    section = feat.get(f"{kind}s", {})
    if name not in section:
        raise KeyError(f"{kind} {name!r} not found in feature")
    c = section[name]
    trigger_key = "command" if kind == "procedure" else "event"
    return {
        "name": name, "kind": kind,
        "description": c.get("description", ""),
        "trigger_kind": trigger_key, "trigger_name": c.get(trigger_key),
        "queries": c.get("queries", []), "emits": c.get("emits", []),
    }


def _synthesize_tools(component: dict, query_defs: dict) -> list[agent.ToolSpec]:
    tools = [
        agent.ToolSpec(f"query_{q}", "query",
                       meta={"query": q, "description": (query_defs.get(q, {}).get("description") or "").strip()})
        for q in component["queries"]
    ]
    out_kind = "emit" if component["kind"] == "procedure" else "dispatch"
    tools += [agent.ToolSpec(f"{out_kind}_{e}", out_kind) for e in component["emits"]]
    tools.append(agent.ToolSpec("report_finding", "finding"))
    return tools


def _build_user_prompt(component: dict, trigger, tools: list[agent.ToolSpec]) -> str:
    trigger_str = trigger if isinstance(trigger, str) else str(trigger)
    return (
        f"component: {component['name']} ({component['kind']})\n"
        f"description:\n{component['description']}\n\n"
        f"trigger ({component['trigger_kind']} {component['trigger_name']}): {trigger_str}\n\n"
        f"available tools: {', '.join(t.name for t in tools)}"
    )


class SimProcedureExecutor:
    def __init__(
        self,
        feat: dict,
        engine: str = "pi",
        model: str | None = None,
        event_store: list[str] | None = None,
    ):
        self._feat = feat
        self._engine = engine
        self._model = model
        self._event_store = event_store or []

    def execute(self, component: str, trigger: str | dict) -> ProcedureResult:
        comp = _find_component(self._feat, component, "procedure")
        tools = _synthesize_tools(comp, self._feat.get("queries", {}))
        result = agent.run_activation(
            engine=self._engine, model=self._model,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=_build_user_prompt(comp, trigger, tools),
            tools=tools, event_store=self._event_store,
        )
        events = [
            {call["tool"].removeprefix("emit_"): call["args"]["narrative"]}
            for call in result.of_kind("emit")
        ]
        findings = [call["args"] for call in result.of_kind("finding")]
        return ProcedureResult(events=events, findings=findings)


class SimPolicyExecutor:
    def __init__(
        self,
        feat: dict,
        engine: str = "pi",
        model: str | None = None,
        event_store: list[str] | None = None,
    ):
        self._feat = feat
        self._engine = engine
        self._model = model
        self._event_store = event_store or []

    def execute(self, component: str, trigger: str | dict) -> PolicyResult:
        comp = _find_component(self._feat, component, "policy")
        tools = _synthesize_tools(comp, self._feat.get("queries", {}))
        result = agent.run_activation(
            engine=self._engine, model=self._model,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=_build_user_prompt(comp, trigger, tools),
            tools=tools, event_store=self._event_store,
        )
        commands = [
            {call["tool"].removeprefix("dispatch_"): call["args"]["narrative"]}
            for call in result.of_kind("dispatch")
        ]
        findings = [call["args"] for call in result.of_kind("finding")]
        return PolicyResult(commands=commands, findings=findings)
