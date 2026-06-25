"""dizzy.simulate.session — append-only JSONL session log for a simulate run."""

import json
from pathlib import Path

import yaml

from dizzy.simulate import executor


class Session:
    def __init__(self, session_path: Path | None = None):
        self._session = []
        self._feature = {}
        self._session_path = session_path

    def _append(self, entry: dict) -> int:
        self._session.append(entry)
        if self._session_path:
            with open(self._session_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        return entry["id"]

    def load_features(self, feature_path: Path) -> "Session":
        if not feature_path.exists():
            raise FileNotFoundError(f"feature file not found: {feature_path}")
        self._feature = yaml.safe_load(feature_path.read_text())
        return self

    def load_session(self, session_path: Path) -> "Session":
        if not session_path.exists():
            raise FileNotFoundError(f"session file not found: {session_path}")
        self._session_path = session_path
        lines = session_path.read_text().splitlines()
        self._session = [json.loads(line) for line in lines]
        return self

    def is_empty(self) -> bool:
        return len(self._session) <= 0

    def current_id(self) -> int:
        if self.is_empty():
            return 1
        return max(x["id"] for x in self._session)

    def next_id(self) -> int:
        return self.current_id() + 1

    def log(self, log_type: str, data: dict, parent_id: int | None = None) -> int:
        return self._append(
            {
                "id": self.next_id(),
                "parent_id": parent_id if parent_id is not None else self.current_id(),
                "type": log_type,
                "log": data,
            }
        )

    def resolve(self, finding_id: int, decision: str, argument: str) -> int:
        return self.log(
            "resolution",
            {
                "finding_id": finding_id,
                "decision": decision,
                "argument": argument,
            },
            parent_id=finding_id,
        )

    def branch(self, from_id: int, reason: str, **meta) -> int:
        return self._append(
            {
                "id": self.next_id(),
                "parent_id": from_id,
                "type": "branch",
                "log": {"from_id": from_id, "reason": reason, **meta},
            }
        )

    def get_latest_scenario(self) -> dict:
        scenarios = [n for n in self._session if n["type"] == "scenario"]
        return max(scenarios, key=lambda x: x["id"])["scenario"]

    def _unwrap_event_log(self, log: dict) -> tuple[str, object]:
        if log["type"] != "event_emitted":
            raise ValueError(f"expected event_emitted, got {log['type']!r}")
        for event_key, event_data in log["log"].items():
            return event_key, event_data
        raise ValueError("empty event log")

    def _unwrap_command_log(self, log: dict) -> tuple[str, object]:
        if log["type"] != "command_emitted":
            raise ValueError(f"expected command_emitted, got {log['type']!r}")
        for command_key, command_data in log["log"].items():
            return command_key, command_data
        raise ValueError("empty command log")

    def _policies_for_event_log(self, event: dict) -> list[tuple[str, dict]]:
        event_name, _ = self._unwrap_event_log(event)
        return [
            (name, defn)
            for name, defn in self._feature.get("policies", {}).items()
            if defn["event"] == event_name
        ]

    def _procedures_for_command_log(self, command: dict) -> list[tuple[str, dict]]:
        command_name, _ = self._unwrap_command_log(command)
        return [
            (name, defn)
            for name, defn in self._feature.get("procedures", {}).items()
            if defn["command"] == command_name
        ]

    def _log_tool_calls(self, tool_calls: list[dict], activation_id: int) -> None:
        last_query_id: int | None = None
        for call in tool_calls:
            kind = call.get("kind")
            if kind == "query":
                last_query_id = self.log(
                    "query_call",
                    {"tool": call["tool"], "args": call["args"]},
                    parent_id=activation_id,
                )
            elif kind == "query_answer":
                parent = last_query_id if last_query_id is not None else activation_id
                self.log("query_response", call["args"], parent_id=parent)
                last_query_id = None

    def event_store(self) -> list[dict]:
        return [x["log"] for x in self._session if x["type"] == "event_emitted"]

    def event_queue(self) -> list[dict]:
        emitted = {x["id"] for x in self._session if x["type"] == "event_emitted"}
        consumed = {
            x["log"]["event_id"]
            for x in self._session
            if x["type"] == "policy_started" and "event_id" in x["log"]
        }
        pending = [x for x in self._session if x["id"] in (emitted - consumed)]
        return [x for x in pending if self._policies_for_event_log(x)]

    def command_queue(self) -> list[dict]:
        emitted = {x["id"] for x in self._session if x["type"] == "command_emitted"}
        consumed = {
            x["log"]["command_id"]
            for x in self._session
            if x["type"] == "procedure_started" and "command_id" in x["log"]
        }
        pending = [x for x in self._session if x["id"] in (emitted - consumed)]
        return [x for x in pending if self._procedures_for_command_log(x)]

    def is_quiescent(self) -> bool:
        return not (self.event_queue() or self.command_queue())

    def step(
        self,
        procedure_executor: executor.ProcedureExecutor,
        policy_executor: executor.PolicyExecutor,
    ) -> "Session":
        if self.is_empty():
            raise RuntimeError("cannot step an empty session")

        es = self.event_store()

        for event in self.event_queue():
            for policy_name, _ in self._policies_for_event_log(event):
                activation_id = self.log(
                    "policy_started", {"procedure": policy_name, "event_id": event["id"]}
                )
                result = policy_executor.execute(policy_name, event, es)
                self._log_tool_calls(result.tool_calls, activation_id)
                for cmd in result.commands:
                    self.log("command_emitted", cmd)
                for finding in result.findings:
                    self.log("finding", finding)

        for command in self.command_queue():
            for procedure_name, _ in self._procedures_for_command_log(command):
                activation_id = self.log(
                    "procedure_started", {"procedure": procedure_name, "command_id": command["id"]}
                )
                result = procedure_executor.execute(procedure_name, command, es)
                self._log_tool_calls(result.tool_calls, activation_id)
                for evt in result.events:
                    self.log("event_emitted", evt)
                for finding in result.findings:
                    self.log("finding", finding)

        return self

    def run_scenario(
        self,
        scenario_path: Path,
        procedure_executor: executor.ProcedureExecutor,
        policy_executor: executor.PolicyExecutor,
    ) -> "Session":
        scenario_data = yaml.safe_load(scenario_path.read_text())
        self._append(
            {
                "id": self.next_id(),
                "parent_id": None,
                "type": "scenario",
                "scenario": scenario_data,
            }
        )
        for event in scenario_data.get("events", []):
            self.log("event_emitted", event)
        for command in scenario_data.get("commands", []):
            self.log("command_emitted", command)
            while not self.is_quiescent():
                self.step(procedure_executor, policy_executor)
        return self
