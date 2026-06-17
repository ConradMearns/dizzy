"""Executor interfaces — procedures emit events; policies dispatch commands; never both.

execute(component, trigger) -> ProcedureResult | PolicyResult

  component  — name of a procedure or policy in the feature file
  trigger    — the activating input: a natural-language string (sim) or a
               structured dict payload (lib); implementors decide how to use it
"""

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass
class ProcedureResult:
    events: list[dict] = field(default_factory=list)
    findings: list[dict] = field(default_factory=list)


@dataclass
class PolicyResult:
    commands: list[dict] = field(default_factory=list)
    findings: list[dict] = field(default_factory=list)


@runtime_checkable
class ProcedureExecutor(Protocol):
    def execute(self, component: str, trigger: str | dict, event_store: list) -> ProcedureResult:
        ...


@runtime_checkable
class PolicyExecutor(Protocol):
    def execute(self, component: str, trigger: str | dict, event_store: list) -> PolicyResult:
        ...


class ExampleProcedureExecutor:
    """Mirrors the 'example emits' stub in sim.py: emits each declared event with placeholder data."""

    def __init__(self, feat: dict):
        self._feat = feat

    def execute(self, component: str, trigger: str | dict, event_store: list) -> ProcedureResult:
        procedure = self._feat["procedures"][component]
        events = [{name: "example"} for name in procedure.get("emits", [])]
        return ProcedureResult(events=events)


class ExamplePolicyExecutor:
    """Mirrors the 'example emits' stub in sim.py: dispatches each declared command with placeholder data."""

    def __init__(self, feat: dict):
        self._feat = feat

    def execute(self, component: str, trigger: str | dict, event_store: list) -> PolicyResult:
        policy = self._feat["policies"][component]
        commands = [{name: "example"} for name in policy.get("emits", [])]
        return PolicyResult(commands=commands)
