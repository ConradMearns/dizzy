

from dataclasses import dataclass
from typing import Literal
import typer

app = typer.Typer()

"""
dizzy is a methodology for writing software.
Built out of, composable pieces. 
Two types of data, commands and events. 
And 2 types of functions, procedures and policies.
Procedures do all of the work.
Anytime they do any effect based code, they write events.
Anytime they do anything that we wanna record as a fact, they write events.
And anytime there is a, like, business level error, they record events. 
All of these events get put into an event sourcing database. 
Which we use as our source of truth for all procedures in the future.
Can query from this event source database efficiently. 
In order to learn information.
About our system over time as it evolves.
The goal of dizzy is to create reproducible redistributable software.
So there's an emphasis on not defining architecture and not defining databases,
and a flexibility code. 
"""

"""
# GOALS
- dizzy dedupe app
2 features
- [ ] data upload
- [ ] data retrieval (web)

2 deployment methods
- [ ] pulumi
- [ ] docker compose

- [ ] chaos testing

# Action plan

We can take a *.feat.yaml and generate the component environment - 
a collection of folders that organize our components

it's okay if we don't generate the LinkML from scratch right now either... 
perhaps let's skip that step again

"""



@dataclass
class DizzyDataPath:
    root: Literal["commands", "events"]
    data_name: str
    data_id: str
    # schema ?
    # pydantic ?
    # impl ?


@dataclass
class DizzyProcessPath:
    root: Literal["procedures", "policies"]
    process_name: str
    process_id: str
    # protocol?
    # impl ?

@app.command()
def hh():
    pass

@app.command()
def hello():
    """Print hello from dizzy."""
    print("hello from dizzy!")


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
