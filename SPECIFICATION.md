# Dizzy Feature File Specification

## Overview

A `.feat.yaml` file is the primary authoring surface in Dizzy. It describes a single feature's
domain model and processing logic at a high level of abstraction — without specifying databases,
frameworks, or infrastructure.

The generator pipeline reads a `.feat.yaml` and produces:
- LinkML schema files (`def/`) for each section
- Generated Python models and interfaces (`gen/`)

---

## Top-Level Structure

```yaml
description: <string>   # Human-readable description of the feature (optional)

models:      <map>       # Domain value objects / data shapes
queries:     <map>       # Read interfaces (input + output)
commands:    <map>       # Write intents
events:      <map>       # Immutable facts (what happened)
procedures:  <map>       # Command handlers (do work, emit events)
policies:    <map>       # Event handlers (react, issue commands)
projections: <map>       # Read-model builders (event → queryable state)
```

All sections are optional. The generator skips sections not present.

---

## Section Definitions

### `models`
Named database schemas — each entry represents a logical grouping of related classes (tables)
for a single database. The feat file declares schema names and optional descriptions only.
The actual classes are defined in the corresponding `def/models/<schema_name>.yaml` LinkML file,
which is authored separately and may grow over time without touching the feat file.

The generator creates a stub `def/models/<schema_name>.yaml` if one does not already exist, then
generates one output file per schema per target backend. Use plural, lowercase names.

```yaml
models:
  recipes: Full recipe database — recipes, steps, and ingredients
```

`def/models/recipes.yaml` (hand-authored) then defines all classes in that schema:

```yaml
classes:
  Recipe:
    attributes:
      title: ...
  Step:
    attributes:
      body: ...
  Ingredient:
    attributes:
      name: ...
      quantity: ...
```

**Generates (per schema):**
- `def/models/<schema_name>.yaml` — stub LinkML schema (only if file does not exist)
- `gen_def/pydantic/<schema_name>.py` — Pydantic models for all classes in the schema
- `gen_def/sqla/<schema_name>.py` — SQLAlchemy models for all classes in the schema

---

### `queries`
Named read operations. Each query must declare the single model schema it reads from, but IO
types are not specified in the feat file — those are defined in authored LinkML stubs and
fleshed out when the implementation is written.

Each query decomposes into **three composable elements**:

- **`QueryInput`** — a LinkML-defined data shape for the query's input parameters
- **`QueryOutput`** — a LinkML-defined data shape for the query's return value
- **`QueryProcess`** — a Protocol for the callable that accepts a `QueryInput` and a context
  (holding a SQLAlchemy session for the referenced model schema) and returns a `QueryOutput`

```yaml
queries:
  get_recipe_text:
    description: Retrieves raw recipe text given a source reference
    model: recipes
  get_recipe:
    description: Retrieves a structured recipe by ID
    model: recipes
```

Fields:
- `description` (required): what this query does
- `model` (required): the schema name from `models` that this query reads from

**Scaffold generates** (stubs, never overwritten):
- `def/queries/<query_name>_input.yaml` — LinkML stub for `QueryInput`
- `def/queries/<query_name>_output.yaml` — LinkML stub for `QueryOutput`

**Gen generates** (from the authored def stubs):
- `gen_def/pydantic/query/<query_name>_input.py` — Pydantic model for `QueryInput`
- `gen_def/pydantic/query/<query_name>_output.py` — Pydantic model for `QueryOutput`
- `gen_int/python/query/<query_name>.py` — `QueryProcess` Protocol + context dataclass:

```python
# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol, Any

from gen_def.pydantic.query.get_recipe_text_input import get_recipe_text_input
from gen_def.pydantic.query.get_recipe_text_output import get_recipe_text_output


@dataclass
class get_recipe_text_context:
    """SQLAlchemy session for the schema read by this query."""
    recipes: Any  # SQLAlchemy session for the recipes schema


class get_recipe_text_query(Protocol):
    """Retrieves raw recipe text given a source reference"""

    def __call__(
        self, input: get_recipe_text_input, context: get_recipe_text_context
    ) -> get_recipe_text_output:
        ...
```

Queries declared in a procedure's `queries:` list are injected into that procedure's
`_queries` context dataclass as typed fields:

```python
@dataclass
class extract_and_transform_recipe_queries:
    get_recipe_text: get_recipe_text_query
```

The implementor passes in a concrete callable (e.g. a SQLAlchemy-backed function) when
constructing the procedure context.

---

### `commands`
Named write intents. Value is either a short description string, or a map with description and optional attributes.

```yaml
commands:
  ingest_recipe_text: Initiates ingestion of a recipe from a raw text source

  upload_blob_using_manifest:
    description: Uploads a blob using manifest information
    attributes:
      manifest_id:
        type: string
        required: true
```

**Generates:** `def/commands.yaml` (LinkML), `gen_def/pydantic/commands.py` (Pydantic)

---

### `events`
Immutable domain facts. Value is either a description string, or a map with description and optional attributes.

```yaml
events:
  recipe_ingested: A recipe was successfully ingested and validated

  scan_item_found:
    description: Found a file while scanning
    attributes:
      file_path:
        type: string
        required: true
      file_hash:
        type: string
```

**Generates:** `def/events.yaml` (LinkML), `gen_def/pydantic/events.py` (Pydantic)

---

### `procedures`
Command handlers. Each procedure is bound to one command, declares queries it uses, and events it may emit.

```yaml
procedures:
  extract_and_transform_recipe:
    description: >
      Queries raw recipe text via source_ref, then uses an LLM to extract a structured
      recipe, validated against the recipe model schema.
    command: ingest_recipe_text
    queries:
      - get_recipe_text
    emits:
      - recipe_ingested
```

Fields:
- `command` (required): the command this procedure handles
- `queries` (optional): list of query names this procedure needs access to
- `emits` (optional): list of event names this procedure may emit

**Generates:** `gen_int/python/procedure/<procedure_name>_context.py`, `gen_int/python/procedure/<procedure_name>_protocol.py`

---

### `policies`
Event-driven reaction handlers. Each policy listens to one event and optionally emits commands.

```yaml
policies:
  trigger_priority_manifest:
    description: Issues command to create image priority manifest when scan completes
    event: scan_complete
    emits:
      - create_image_priority_manifest
```

Fields:
- `event` (required): the event that triggers this policy
- `emits` (optional): list of command names this policy may dispatch

**Generates:** `gen_int/python/policy/<policy_name>_protocol.py`

---

### `projections`
Build queryable read models in response to a single event. Each projection listens to exactly
one event and may update one or more model schemas.

A projection is structurally similar to a procedure: it receives an **event** and a **context**
object, then uses SQLAlchemy to persist state into the referenced model schemas. One SQLAlchemy
session is injected per declared model schema.

```yaml
projections:
  recipe_library:
    description: Adds ingested recipe to the recipe library
    event: recipe_ingested
    models:
      - recipes
```

Fields:
- `description` (required): what this projection does
- `event` (required): the single event that triggers this projection
- `models` (required): list of schema names from `models` that this projection writes into

**Generates:** `gen_int/python/projection/<projection_name>_projection.py` — a context dataclass
and a Protocol stub:

```python
# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol, Any

from ..events import recipe_ingested


@dataclass
class recipe_library_context:
    """SQLAlchemy sessions for schemas written by this projection."""
    recipes: Any  # SQLAlchemy session for the recipes schema


class recipe_library_projection(Protocol):
    """Adds ingested recipe to the recipe library"""

    def __call__(self, event: recipe_ingested, context: recipe_library_context) -> None:
        """Apply the projection — mutate model state in response to the event."""
        ...
```

The `Any` session type is a placeholder; the implementor binds it to a concrete SQLAlchemy
`Session` when wiring up the projection.

---

## Full Example

```yaml
description: Recipe App

models:
  recipes: Full recipe database — recipes, steps, and ingredients

queries:
  get_recipe_text:
    description: Retrieves raw recipe text given a source reference
    model: recipes
  get_recipe:
    description: Retrieves a structured recipe by ID
    model: recipes

commands:
  ingest_recipe_text: Initiates ingestion of a recipe from a raw text source

events:
  recipe_ingested:
    description: A recipe was successfully extracted and validated
    attributes:
      recipe_id:
        type: string
        required: true
      source_ref:
        type: string
        required: true

procedures:
  extract_and_transform_recipe:
    description: >
      Queries raw recipe text via source_ref, then uses an LLM to extract a structured
      recipe (title, ingredients, steps, time, cost), validated against the recipe model.
    command: ingest_recipe_text
    queries:
      - get_recipe_text
    emits:
      - recipe_ingested

policies:
  index_recipe_on_ingest:
    description: Adds recipe to the library projection when ingested
    event: recipe_ingested

projections:
  recipe_library:
    description: Adds ingested recipe to the recipe library
    event: recipe_ingested
    models:
      - recipes
```

---

## Generator Output Layout

Given a feature at `app/my_feature/my_feature.feat.yaml`, the generator produces:

```
app/my_feature/
  def/
    models/
      recipes.yaml
    queries/
      get_recipe_text_input.yaml
      get_recipe_text_output.yaml
      get_recipe_input.yaml
      get_recipe_output.yaml
    commands.yaml
    events.yaml
  gen_def/
    pydantic/
      models/
        recipes.py
      query/
        get_recipe_text_input.py
        get_recipe_text_output.py
        get_recipe_input.py
        get_recipe_output.py
      commands.py
      events.py
    sqla/
      models/
        recipes.py
  gen_int/
    python/
      query/
        get_recipe_text.py
        get_recipe.py
      procedure/
        extract_and_transform_recipe_context.py
        extract_and_transform_recipe_protocol.py
      policy/
        index_recipe_on_ingest_protocol.py
      projection/
        recipe_library_projection.py
  src/
    query/
      get_recipe_text.py
      get_recipe.py
    procedure/
      extract_and_transform_recipe.py
    policy/
      index_recipe_on_ingest.py
    projection/
      recipe_library.py
```

def: definitions
gen_def: generated definitions
gen_int: generated interfaces

Sections with no content in the feat file produce no output.

---

## Import Path Convention

All generated files use **relative Python imports**. The intent is that the entire output
directory is portable — it can be copied or symlinked into any project structure without
changing import paths.

Generated files assume the feature output directory is a Python package root (i.e. there is
an `__init__.py` at each level). Imports between generated layers use dot-notation relative
to that root:

| From | Importing | Import |
|------|-----------|--------|
| `gen_int/python/procedure/` | Pydantic events | `from gen_def.pydantic.events import ...` |
| `gen_int/python/procedure/` | Pydantic commands | `from gen_def.pydantic.commands import ...` |
| `gen_int/python/procedure/` | Query Protocols | `from gen_int.python.query import ...` |
| `gen_int/python/projection/` | Pydantic events | `from gen_def.pydantic.events import ...` |
| `src/procedure/` | Procedure Protocol + context | `from gen_int.python.procedure.<name>_protocol import ...` |
| `src/projection/` | Projection Protocol + context | `from gen_int.python.projection.<name>_projection import ...` |

The feature output directory must be on `sys.path` (or be a package reachable from it) for
these imports to resolve at runtime.

---

## CLI Workflow

Dizzy is a two-step generator. The split exists because `def/` files require human authorship
between the two steps — they cannot be fully derived from the feat file alone.

### Step 1 — Author the feat file

Write `my_feature.feat.yaml` by hand. Declare models, commands, events, procedures, policies,
and projections at the intent level. No types, no schemas, no implementation details yet.

---

### Step 2 — Scaffold definition stubs

```
dizzy scaffold <feat_file> <output_dir> [--todos]
```

Reads the feat file and generates empty `def/` stub files for everything that requires
human schema authorship before code can be generated:

- `def/models/<schema_name>.yaml` — stub LinkML schema per model (skipped if already exists)
- `def/commands.yaml` — stub LinkML schema listing all commands
- `def/events.yaml` — stub LinkML schema listing all events

After running, Dizzy prints:

```
Scaffolded def/ stubs. Next steps:
  1. Fill in class definitions in def/models/*.yaml
  2. Add attributes to def/commands.yaml and def/events.yaml
  3. Run: dizzy gen <feat_file> <output_dir>
```

With `--todos`, also writes `def/TODO.md` describing what needs to be authored in each stub file.

---

### Step 3 — Author the definition files

Edit the generated `def/` stubs:
- Add classes, attributes, and relationships to each model schema
- Add typed attributes to commands and events as needed

These files are yours — Dizzy will never overwrite them.

---

### Step 4 — Generate interfaces and source stubs

```
dizzy gen <feat_file> <output_dir> [--todos]
```

Reads both the feat file and the authored `def/` files, then generates:

**`gen_def/`** — derived from `def/` schemas (Pydantic models, SQLAlchemy models)

**`gen_int/`** — Protocol stubs derived from the feat file structure (queries, procedures,
policies, projections)

**`src/`** — empty implementation stubs, one per interface, for the developer to fill in:

```
src/
  query/
    <query_name>.py
  procedure/
    <procedure_name>.py
  policy/
    <policy_name>.py
  projection/
    <projection_name>.py
```

Source stubs are only created if the file does not already exist, so they are safe to
re-run after editing.

After running, Dizzy prints a per-section summary and:

```
Generated interfaces and source stubs. Next steps:
  Implement the src/ files to complete your feature.
```

With `--todos`, also writes `src/TODO.md` listing each unimplemented stub with a brief
description of what it should do (derived from the feat file descriptions).

---

### Summary

| Step | Command | You do next |
|------|---------|-------------|
| 1 | — | Write `my_feature.feat.yaml` |
| 2 | `dizzy scaffold` | Edit `def/` schema stubs |
| 3 | — | Author class definitions and attributes |
| 4 | `dizzy gen` | Implement `src/` stubs |
