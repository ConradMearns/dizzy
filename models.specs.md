# Models Adapter Specification

## Overview

This spec extends the DIZZY feature model to support **adapters** on `ModelDef`. An adapter
represents a concrete persistence or I/O strategy for a model schema (e.g., SQLAlchemy session,
relative filesystem path). Queries and projections that reference a model must also declare which
adapter they use. The generator produces a shared adapter class per adapter type, and injects it
into the context class of any query or projection that uses it.

---

## 1. feat.yaml schema changes

### 1.1 `models` — object form required

The simple `name: description` shorthand is **removed**. Every model must use the full object form
declaring both `description` and `adapters`. The `adapters` list must be non-empty.

```yaml
models:
  recipes:
    description: Full recipe database — recipes, steps, and ingredients
    adapters:
      - sqla
      - relative_filesystem
```

### 1.2 `queries` — `adapter` field added

A query that references a `model` must also declare `adapter`. A query with no `model` must omit
`adapter`. There is no default — the binding must be explicit.

```yaml
queries:
  get_recipe_text:
    description: Retrieves raw recipe text given a source reference
    model: recipes
    adapter: relative_filesystem

  llm_completion:
    description: Retrieve an LLM completion
    # no model, no adapter — context will be empty
```

### 1.3 `projections` — singular `model` + `adapter`

Projections change from `models: list[str]` (plural) to `model: str` (singular) + `adapter: str`.
A projection may reference only one model.

```yaml
projections:
  recipe_library:
    description: Adds ingested recipe to the recipe library
    event: recipe_ingested
    model: recipes
    adapter: sqla
```

---

## 2. Data model changes (`feat.py`)

### 2.1 New `ModelDef` dataclass

```python
@dataclass
class ModelDef:
    description: str
    adapters: list[str]
```

`FeatureDefinition.models` changes from `dict[str, str]` to `dict[str, ModelDef]`.

### 2.2 `QueryDef` — `adapter` field added

```python
@dataclass
class QueryDef:
    description: str
    model: str | None = None
    adapter: str | None = None
```

### 2.3 `ProjectionDef` — singular model

```python
@dataclass
class ProjectionDef:
    description: str
    event: str
    model: str | None = None   # singular; None only if no model needed
    adapter: str | None = None
```

`models: list[str]` is removed entirely.

---

## 3. Validation changes (`validate_feat`)

The following checks are added. All produce error strings (not warnings) in the returned list.

| Rule | Error message pattern |
|------|-----------------------|
| Query declares `model` without `adapter` | `query '{name}': model declared without adapter` |
| Query declares `adapter` without `model` | `query '{name}': adapter declared without model` |
| Query adapter not in model's declared adapters | `query '{name}': adapter '{adapter}' not declared on model '{model}'` |
| Projection declares `model` without `adapter` | `projection '{name}': model declared without adapter` |
| Projection declares `adapter` without `model` | `projection '{name}': adapter declared without model` |
| Projection adapter not in model's declared adapters | `projection '{name}': adapter '{adapter}' not declared on model '{model}'` |
| Projection references unknown model | (existing check, unchanged) |
| Query references unknown model | (existing check, unchanged) |

Unknown adapter names (not in the registry) produce a **warning** at generation time, not a
validation error, so that new adapters can be introduced without breaking the validator.

---

## 4. Adapter registry

The known adapter identifiers and their corresponding Python types are:

| Adapter identifier    | Adapter class name            | Injected field | Field type              | Import |
|-----------------------|-------------------------------|----------------|-------------------------|--------|
| `sqla`                | `SqlaAdapter`                 | `session`      | `Session`               | `from sqlalchemy.orm import Session` |
| `relative_filesystem` | `RelativeFilesystemAdapter`   | `root`         | `Path`                  | `from pathlib import Path` |

Adapter class names are derived by converting the adapter identifier from `snake_case` to
`PascalCase` and appending `Adapter`.

---

## 5. Generated adapter classes

### 5.1 Location

Adapter classes are **shared** — one file per adapter, not per model or per query:

```
gen_int/python/adapters/<adapter_name>.py
```

Examples:
- `gen_int/python/adapters/sqla.py`
- `gen_int/python/adapters/relative_filesystem.py`

These files are **always overwritten** by the generator (same as protocol files).

### 5.2 Generated content — `sqla`

```python
# AUTO-GENERATED — do not edit
from dataclasses import dataclass

from sqlalchemy.orm import Session


@dataclass
class SqlaAdapter:
    """Adapter providing a SQLAlchemy session."""

    session: Session
```

### 5.3 Generated content — `relative_filesystem`

```python
# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RelativeFilesystemAdapter:
    """Adapter providing a root path for relative filesystem access."""

    root: Path
```

### 5.4 When adapter files are generated

An adapter file is generated whenever at least one model in the feat declares that adapter. If no
model uses `sqla`, `gen_int/python/adapters/sqla.py` is not written.

---

## 6. Context class changes

### 6.1 Query context

When a query has `model` + `adapter`, the context dataclass gains a single `adapter` field typed
to the appropriate adapter class. When a query has no model/adapter, the context body remains
`pass`.

**With adapter (`relative_filesystem`):**
```python
# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.query.get_recipe_text import GetRecipeTextInput, GetRecipeTextOutput
from gen_int.python.adapters.relative_filesystem import RelativeFilesystemAdapter


@dataclass
class get_recipe_text_context:
    adapter: RelativeFilesystemAdapter


class get_recipe_text_query(Protocol):
    """Retrieves raw recipe text given a source reference."""

    def __call__(
        self, input: GetRecipeTextInput, context: get_recipe_text_context
    ) -> GetRecipeTextOutput:
        ...
```

**Without adapter:**
```python
@dataclass
class llm_completion_context:
    pass
```

### 6.2 Projection context

Same pattern — a single `adapter` field when `model` + `adapter` are declared.

```python
# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.events import recipe_ingested
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class recipe_library_context:
    adapter: SqlaAdapter


class recipe_library_projection(Protocol):
    """Adds ingested recipe to the recipe library."""

    def __call__(self, event: recipe_ingested, context: recipe_library_context) -> None:
        """Apply the projection — mutate model state in response to the event."""
        ...
```

---

## 7. Scaffold model generator — unchanged

`write_scaffold_model` and `render_scaffold_model` are **not changed** by this spec. The `adapters`
list on a `ModelDef` does not affect the LinkML scaffold stub written to `def/models/<name>.yaml`.
The separate `linkml_runner` step (running `gen-pydantic`, `gen-sqla`, etc.) is also out of scope
for this spec.

---

## 8. Summary of file changes

| File | Change |
|------|--------|
| `dizzy/src/dizzy/feat.py` | Add `ModelDef`; update `FeatureDefinition.models`; add `adapter` to `QueryDef`; replace `models: list` with `model + adapter` on `ProjectionDef`; update parsers and `validate_feat` |
| `dizzy/src/dizzy/generators/queries.py` | Import and reference adapter class in `render_gen_query_protocol`; remove `Any` placeholder |
| `dizzy/src/dizzy/generators/projections.py` | Import and reference adapter class; update to singular `model`; remove loop over `models` list |
| `dizzy/src/dizzy/generators/adapters.py` | **New file** — `render_adapter` and `write_adapter` functions, one per known adapter |
| `dizzy/tests/fixtures/recipe.feat.yaml` | Migrate to new schema: models with `adapters`, queries with `adapter`, projections with singular `model` + `adapter` |
| `dizzy/tests/generators/test_models.py` | Update for `ModelDef` |
| `dizzy/tests/generators/test_queries.py` | Update context assertions to use adapter class |
| `dizzy/tests/generators/test_projections.py` | Update for singular model and adapter class |
| `dizzy/tests/test_validation.py` | Add cases for new validation rules |
