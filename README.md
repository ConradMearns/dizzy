# DIZZY

## Overview

DIZZY is an opinionated software development philosophy and accompanying toolkit for writing software that scales.

Current Efforts:

- DIZZY STORM (V->P): A handbook for Software Development
- DIZZY DISCO (N->V): A DIZZY infrastructure compiler

Current DIZZY projects:

- DIZZY DEDUPE: An example application

## Developer Setup

This is a **uv monorepo** with multiple packages and applications managed as a workspace.

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- [just](https://github.com/casey/just) command runner (optional, for convenience)

### Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/ConradMearns/dizzy.git
   cd dizzy
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Activate the virtual environment**
   ```bash
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate  # Windows
   ```

### Documentation

View and edit documentation using MkDocs:

```bash
# Serve docs locally
uv run mkdocs serve
```

### Using Justfiles

This project uses `justfiles` for common tasks. Run `just` in any directory to see available commands.

