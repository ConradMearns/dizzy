import yaml
from pathlib import Path
import typer

app = typer.Typer()

def init_commands(scenario):
    commands = scenario['commands']
    return commands

def init_events(scenario):
    events = scenario['events']
    return events

def verify_scenario(feat, scenario):
    errors = []
    for event in scenario['events']:
        for event_key in event.keys():
            if not event_key in feat['events'].keys():
                errors.append(f"Scenario called event that does not exist: {event_key}")
    for command in scenario['commands']:
        for command_key in command.keys():
            if not command_key in feat['commands'].keys():
                errors.append(f"Scenario called command that does not exist: {command_key}")

    if errors:
        print()
        for error in errors:
            print("ERR", error)
        exit()
    print("scenario validation passed")


@app.command()
def load(feat_file: Path, scenario_file: Path, session_path: Path = Path("sim/test_session.jsonl")):
    print(feat_file)
    print(scenario_file)
    print(session_path)

    scenario = yaml.full_load(scenario_file.open())
    feat = yaml.full_load(feat_file.open())
    session = []

    main(feat, scenario, session)

def quiescent(commands, events):
    return (len(commands) <= 0) and (len(events) <= 0)

def do_event(event):
    key, value = list(event.items())[0]
    print(key)
    print(value)
    if isinstance(value, str):
        print("string")
    if isinstance(value, dict):
        print("dict")

    print("EVNT", event)
    # key, value = 

def do_command(command):
    print("CMND", command)

def main(feat, scenario, session):
    verify_scenario(feat, scenario)
    commands = init_commands(scenario)
    events = init_events(scenario)

    budget = 30

    while not quiescent(commands, events) or budget <= 0:
        print(len(commands), len(events), budget)

        while len(events)>0:
            event = events.pop()
            do_event(event)

        while len(commands)>0:
            command = commands.pop()
            do_command(command)
            
        budget -= 1

    print("quiescence reached")



if __name__=="__main__":
    app()