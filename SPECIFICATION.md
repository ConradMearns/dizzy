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
Domain data shapes — value objects, entities, or shared types referenced by commands, events, queries.

```yaml
models:
  Recipe:
    description: A structured recipe with ingredients and steps
    attributes:
      title:
        type: string
        required: true
      ingredients:
        type: string        # scalar type or reference to another model
        multivalued: true
      estimated_minutes:
        type: integer
      cost_estimate:
        type: float
```

**Generates:** `def/models.yaml` (LinkML), `gen/models.py` (Pydantic)

---

### `queries`
Named read operations, each with an input and output type.

```yaml
queries:
  get_recipe_text:
    description: Retrieves raw recipe text given a source reference
    input: source_ref        # name of input field (scalar) or model reference
    output: raw_text         # name of output field (scalar) or model reference
```

For richer queries, `input` and `output` can be inline attribute maps:

```yaml
queries:
  search_recipes:
    description: Search recipes by keyword
    input:
      keyword: string
      max_results:
        type: integer
        required: false
    output:
      results:
        type: Recipe
        multivalued: true
```

**Generates:** `def/queries.yaml` (LinkML), `gen/queries.py` (Pydantic), `gen/query_interfaces.py` (Protocol)

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

**Generates:** `def/commands.yaml` (LinkML), `gen/commands.py` (Pydantic)

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

**Generates:** `def/events.yaml` (LinkML), `gen/events.py` (Pydantic)

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

**Generates:** `gen/procedure/py/<procedure_name>_context.py`, `gen/procedure/py/<procedure_name>_protocol.py`

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

**Generates:** `gen/policy/py/<policy_name>_protocol.py`

---

### `projections`
Build queryable read models from a stream of events.

```yaml
projections:
  recipe_library:
    description: Maintains a searchable list of all ingested recipes
    events:
      - recipe_ingested
    output: Recipe      # model reference for the projected state shape
```

Fields:
- `events` (required): list of event names that update this projection
- `output` (required): model name representing the projected read shape

**Generates:** `gen/projection/py/<projection_name>_projection.py` (Protocol)

---

## Full Example

```yaml
description: Recipe App

models:
  Recipe:
    description: A structured recipe
    attributes:
      title:
        type: string
        required: true
      ingredients:
        type: string
        multivalued: true
      steps:
        type: string
        multivalued: true
      estimated_minutes:
        type: integer
      cost_usd:
        type: float

queries:
  get_recipe_text:
    description: Retrieves raw recipe text given a source identifier
    input: source_ref
    output: raw_text

  get_recipe:
    description: Retrieves a structured recipe by ID
    input: recipe_id
    output: Recipe

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
    description: Maintains a searchable collection of all ingested recipes
    events:
      - recipe_ingested
    output: Recipe
```

---

## Generator Output Layout

Given a feature at `app/my_feature/my_feature.feat.yaml`, the generator produces:

```
app/my_feature/
  def/
    models.yaml
    commands.yaml
    events.yaml
    queries.yaml
  gen_def/
    pydantic/
      models.py
      commands.py
      events.py
      queries.py
  gen_int/
    python/
      query/
        recipes_with_ingredients.py
        all_recipes.py
      procedure/
        extract_and_transform_recipe_context.py
        extract_and_transform_recipe_protocol.py
      policy/
        index_recipe_on_ingest_protocol.py
      projection/
        recipe_library_projection.py
```

def: definitions
gen_def: generated definitions
gen_int: generated interfaces

Sections with no content in the feat file produce no output.
