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

## Project Structure

This is a **monorepo** organized as follows:

- **`dizzy/`** - Core DIZZY package and framework
- **`app/`** - Test applications demonstrating DIZZY patterns

The project uses a **uv monorepo** for packaging and **justfiles** to record common commands.
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
