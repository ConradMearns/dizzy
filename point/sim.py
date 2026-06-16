import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import typer
import yaml

app = typer.Typer(add_completion=False)

class Session:
    def __init__(self):
        self._session = []

    def load(self, session_path: Path):
        if not session_path.exists():
            raise NotImplementedError()

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

        events = self.get_latest_scenario()['events']

        for event in events:
            self.log("emitted_event", event)


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

    def event_store(self):
        return [n['log'] for n in self._session if n['type'] == "emitted_event"]

    def event_queue(self):
        # emitted but not consumed ?
        pass


    def command_queue(self):
        pass

    def step(self) -> 'Session':
        if self.is_empty():
            raise NotImplementedError()

        for event in self.event_store():
            print(event)
        
        
        # print(events)

        # load command from scenario

        return self

        
        

@app.command()
def devtest():
    session = Session()
    session.begin_scenario(Path("point/scenarios/borrow_available_book.scenario.yaml"))
    # session.begin_scenario(Path("point/scenarios/catalog_one.scenario.yaml"))
    session.step()
    print('ah')

@app.command()
def new(
    feat_file: Path,
    scenario_file: Path,
    session_path: Path = typer.Argument(Path("point/session.jsonl")),
):
    
    session = Session().load(session_path)

@app.command()
def run(session_path: Path):
    pass

if __name__ == "__main__":
    app()
