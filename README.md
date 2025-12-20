# DIZZY

dizzy is a methodology for writing software

Built out of, composable pieces:
2 types of data: commands and events. 
2 types of functions: procedures and policies.

Procedures do all of the work.
Anytime they do any effect based code, they write events.
Anytime they do anything that we wanna record as a fact, they write events.
And anytime there is a, like, business level error, they record events. 

All of these events get put into an event sourcing database. 
Which we use as our source of truth for all procedures in the future.

Can query from this event source database efficiently. 
In order to learn information about our system over time as it evolves.

The goal of dizzy is to create reproducible redistributable software.

So there's an emphasis on not defining architecture and not defining databases, and a flexibility code. 

## GOALS
- dizzy dedupe app
2 features
- [ ] data upload
- [ ] data retrieval (web)

2 deployment methods
- [ ] pulumi
- [ ] docker compose

- [ ] chaos testing

## Action plan

We can take a *.feat.yaml and generate the component environment - 
a collection of folders that organize our components

it's okay if we don't generate the LinkML from scratch right now either... 
perhaps let's skip that step again



## Current Efforts:

- DIZZY STORM (V->P): A handbook for Software Development
- DIZZY DISCO (N->V): A DIZZY infrastructure compiler

Current DIZZY apps:

- DIZZY DEDUPE: An example application
- DIZZY TODO: An example application for observing UI interactions

## Project Structure

This is a **monorepo** organized as follows:

- **`dizzy/`** - Core DIZZY package and framework
- **`app/`** - Test applications demonstrating DIZZY patterns

The project uses a **uv monorepo** for packaging and **justfiles** to record common commands.

## DIZZY Program Schema

DIZZY applications are structured around **4 Flow Components** that form a continuous cycle:

**Commands → Procedures → Events → Policies → Commands**

This architecture leverages **CQRS (Command Query Responsibility Segregation)**:

- **Commands**: Trigger actions in the system
- **Procedures**: Execute business logic and emit Events
- **Events**: Capture state changes
- **Policies**: React to Events and may trigger new Commands

## Developer Setup

This is a **uv monorepo** with multiple packages and applications managed as a workspace.

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- [just](https://github.com/casey/just) command runner (optional, for convenience)


### Documentation

View and edit documentation using MkDocs:

```bash
# Serve docs locally
uv run mkdocs serve
```
