import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import typer
import yaml

import executor
import sim_executors

app = typer.Typer(add_completion=False)



class Session:
    def __init__(self):
        self._session = []
        self._feature = {}

    def load_features(self, feature_path: Path):
        if not feature_path.exists():
            raise NotImplementedError()
            
        self._feature = yaml.safe_load(feature_path.read_text())

        return self

    def load_session(self, session_path: Path):
        if not session_path.exists():
            raise NotImplementedError()

        # read session
        lines = session_path.read_text().splitlines()
        self._session = [json.loads(line) for line in lines]
        
        return self
    
    def is_empty(self):
        return len(self._session) <= 0

    def current_id(self) -> int:
        if self.is_empty():
            return 1
        ids = [x["id"] for x in self._session]
        return max(ids) 

    def next_id(self) -> int:
        return self.current_id() + 1

    def begin_scenario(self, scenario_path):
        scenario_data = yaml.safe_load(scenario_path.read_text())
        self._session.append({
            "id": self.next_id(),
            "parent_id": None,
            "type": "scenario",
            "scenario": scenario_data
        })

        events = scenario_data['events']
        commands = scenario_data['commands']

        for event in events:
            self.log("event_emitted", event)

        for command in commands:
            self.log("command_emitted", command)


    def log(self, log_type: str, data: dict):
        self._session.append({
            "id": self.next_id(),
            "parent_id": self.current_id(),
            "type": log_type,
            "log": data
        })

    def is_data_logged(self, data: dict):
        data in [x['log'] for x in self._session]


    def get_latest_scenario(self):
        scenarios = [n for n in self._session if n['type'] == "scenario"]
        log = max(scenarios, key=lambda x:x["id"])
        scenario = log['scenario']
        return scenario

    # main queries ?

    def _unwrap_event_log(self, log):
        if "event_emitted" != log["type"]:
            raise
        for event_key, event_data in log["log"].items():
            return event_key, event_data

    def _unwrap_command_log(self, log):
        if "command_emitted" != log["type"]:
            raise
        for command_key, command_data in log["log"].items():
            return command_key, command_data

    def _policies_for_event_log(self, event):
        event, data = self._unwrap_event_log(event)
        matching = []
        for policy_name, policy_def in self._feature["policies"].items():
            if policy_def["event"] == event:
                matching.append((policy_name, policy_def))
        return matching

    def _procedures_for_command_log(self, command):
        event, data = self._unwrap_command_log(command)
        matching = []
        for name, data in self._feature["procedures"].items():
            if data["command"] == event:
                matching.append((name, data))
        return matching


    def event_store(self):
        emitted = [x["log"] for x in self._session if x["type"] == "event_emitted"]
        return emitted

    def event_queue(self):
        emitted = {x["id"] for x in self._session if x["type"] == "event_emitted"}
        consumed = {
            x["log"]["event_id"]
            for x in self._session
            if x["type"] == "policy_started" and "event_id" in x["log"]
        }
        pending = [x for x in self._session if x["id"] in (emitted - consumed)]
        return [x for x in pending if self._policies_for_event_log(x)]

    def command_queue(self):
        emitted = {x["id"] for x in self._session if x["type"] == "command_emitted"}
        consumed = {
            x["log"]["command_id"]
            for x in self._session
            if x["type"] == "procedure_started" and "command_id" in x["log"]
        }
        pending = [x for x in self._session if x["id"] in (emitted - consumed)]
        return [x for x in pending if self._procedures_for_command_log(x)]

    def is_quiescent(self):
        has_events = len(self.event_queue()) > 0
        has_commands = len(self.command_queue()) > 0
        # return not has_commands # less strict
        return not (has_commands or has_events)


    def step(
        self,
        procedure_executor: executor.ProcedureExecutor,
        policy_executor: executor.PolicyExecutor,
    ) -> 'Session':
        if self.is_empty():
            raise NotImplementedError()

        print("="*30)
        print("STEP")
        print("="*30)

        es = self.event_store()

        print("EVENTS:")
        for event in es:
            print(es)

        print("EVENT QUEUE:")
        for event in self.event_queue():
            print(event['log'])
            for policy_name, policy in self._policies_for_event_log(event):
                print("do policy:", policy_name)
                self.log('policy_started', {"procedure": policy_name, "event_id": event["id"]})
                result = policy_executor.execute(policy_name, event, es)
                for cmd in result.commands:
                    self.log('command_emitted', cmd)

        print("COMMAND QUEUE:")
        for command in self.command_queue():
            print(command['log'])
            for procedure_name, procedure in self._procedures_for_command_log(command):
                print("do procedure:", procedure_name)
                self.log('procedure_started', {"procedure": procedure_name, "command_id": command["id"]})
                result = procedure_executor.execute(procedure_name, command, es)
                for evt in result.events:
                    self.log('event_emitted', evt)

        return self
    
    

@app.command()
def devtest():
    session = Session().load_features(Path("point/library.feat.yaml"))
    session.begin_scenario(Path("point/scenarios/borrow_available_book.scenario.yaml"))
    
    # session.begin_scenario(Path("point/scenarios/catalog_one.scenario.yaml"))

    # print(session.event_store())
    # [{'member_registered': 'Test User exists with member id 0042-00-00000000'}, {'member_registered': {'name': 'Conrad', 'member_id': '0042-00-00000001'}}]
    # exit()

    procedure_executor = sim_executors.SimProcedureExecutor(session._feature, provider="openrouter", model="anthropic/claude-haiku-4-5", verbose_stream=True)
    policy_executor = sim_executors.SimPolicyExecutor(session._feature, provider="openrouter", model="anthropic/claude-haiku-4-5", verbose_stream=True)

    session.step(procedure_executor, policy_executor)
    exit()
    while not session.is_quiescent():
        session.step(procedure_executor, policy_executor)

@app.command()
def new(
    feat_file: Path,
    scenario_file: Path,
    session_path: Path = typer.Argument(Path("point/session.jsonl")),
):
    
    session = Session().load_session(session_path)

@app.command()
def run(session_path: Path):
    pass

if __name__ == "__main__":
    app()
