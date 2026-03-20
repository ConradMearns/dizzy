Consider this example - which is not strictly DIZZY but merges Procedure and Projection code to illustrate 2 different projection paths (file and sql)

```py
import os

import yaml
from rich.console import Console
from rich.syntax import Syntax
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from gen_def.pydantic.models.recipes import Recipe
from gen_def.sqla.models.recipes import (
    Base,
    Ingredient as IngredientRow,
    Recipe as RecipeRow,
    RecipeSteps,
)

from gen_int.python.procedure.extract_and_transform_recipe_context import extract_and_transform_recipe_context
from gen_def.pydantic.commands import IngestRecipeText
from gen_def.pydantic.query.get_recipe_text import GetRecipeTextInput
from gen_def.pydantic.query.llm_completion import LlmCompletionInput


console = Console()

from gen_int.python.query.get_recipe_text import get_recipe_text_context
from gen_int.python.query.llm_completion import llm_completion_context

def extract_and_transform_recipe(
    context: extract_and_transform_recipe_context,
    command: IngestRecipeText,
) -> None:

    # procedure code

    query_result = context.query.get_recipe_text(
        input = GetRecipeTextInput(source_ref = command.source_ref),
        context=get_recipe_text_context(),
    )

    # command query was good - this should always be the case,
    # so don't really care about logging to an immutable event store
    # we would likely care more about logging for telemetry though!

    llm_response = context.query.llm_completion(
        input = LlmCompletionInput(raw_text = query_result.raw_text),
        context=llm_completion_context()
    )

    # logging the llm response to the event store is a good idea because
    # it enables naive caching of what otherwise might be expensive,
    # allows us to track changes to this output if no idempotent
    # trigger projections - though we may want to enforce a retry / validation step here

    yaml_text = llm_response.raw_text

    console.print(Syntax(yaml_text, "yaml", theme="monokai", line_numbers=False))

    # projection code

    data = yaml.safe_load(yaml_text)
    for ing in data.get("ingredients") or []:
        if ing.get("quantity") is not None:
            ing["quantity"] = str(ing["quantity"])
    known_fields = Recipe.model_fields.keys()
    data = {k: v for k, v in data.items() if k in known_fields}
    recipe = Recipe.model_validate(data)

    output_path = f"{command.source_ref}.recipe.json"
    with open(output_path, "w") as f:
        f.write(recipe.model_dump_json(indent=2))

    console.print(f"[green]Saved recipe to {output_path}[/green]")

    # save to sqlite
    engine = create_engine("sqlite:///recipes.db")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        recipe_row = RecipeRow(
            title=recipe.title,
            servings=recipe.servings,
            time_estimate=recipe.time_estimate,
            ingredients=[
                IngredientRow(quantity=i.quantity, unit=i.unit, item=i.item)
                for i in (recipe.ingredients or [])
            ],
            steps=[s for s in (recipe.steps or [])],
        )
        session.add(recipe_row)
        session.commit()
        console.print(f"[green]Saved recipe id={recipe_row.id} to recipes.db[/green]")
```

and consider this query, which only works for text files

```python
from pathlib import Path

from gen_int.python.query.get_recipe_text import get_recipe_text_query, get_recipe_text_context
from gen_def.pydantic.query.get_recipe_text import GetRecipeTextInput, GetRecipeTextOutput


def get_recipe_text(input: GetRecipeTextInput, context: get_recipe_text_context) -> GetRecipeTextOutput:
    raw_text = Path(input.source_ref).read_text(encoding="utf-8")
    return GetRecipeTextOutput(raw_text=raw_text)
```

The problem is as follows:

we must support many model systems. in the feat file - given by `dizzy/def/feat.yaml`, we can expect each `model` to be KV pairs of names and descriptions, like in

```yaml
commands:
  ingest_recipe_text: Initiates ingestion of a recipe from a raw text source

models:
  recipes: Schema for recipes

queries:
  get_recipe_text:
    description: Retrieves raw recipe text given a source identifier (URL, file path, or inline text)
    input: source_ref
    output: raw_text
  llm_completion:
    description: Retrieve an LLM completion
    input: raw_text
    output: raw_text

procedures:
  extract_and_transform_recipe:
    description: >
      Queries raw recipe text via source_ref, then uses an LLM to extract a structured recipe
      (title, ingredients with quantities, steps, time estimate, cost estimate),
      validated against the recipe model schema.
    command: ingest_recipe_text
    queries:
      - get_recipe_text
      - llm_completion
```

the problem here is that we don't actually know what projections / queries are okay to use for each model. The model _mainly_ represents schemas that we need. But the insight here is that even though we have 1 schema, there are an endless number of ways to deploy the schema. Illustrated in the code above is a Filesystem method, and a SQL ALchemy method.

We must see that in queries and projections - model access specific imports are NOT included in the query / projection code

```python
# not in the projection python!
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from gen_def.pydantic.models.recipes import Recipe
from gen_def.sqla.models.recipes import (
    Base,
    Ingredient as IngredientRow,
    Recipe as RecipeRow,
    RecipeSteps,
)
```

projection code and query code is specific to the model method - so we almost want something like

```yaml
models:
  recipes:
    description: Schema for recipes
    adapters:
        - sqla
        - relative_filesystem
```

---

## Disambiguations

### [MUST] Adapters are declared on ModelDef

A model declares the set of adapters it supports. The generator runs the appropriate linkml
codegen tool (e.g. `gen-pydantic`, `gen-sqla`) for each declared adapter, producing adapter-specific
artifacts under `gen_def/<adapter>/models/<name>.py`.

```yaml
models:
  recipes:
    description: Schema for recipes
    adapters:
      - sqla
      - relative_filesystem
```

### [MUST] Queries and projections declare their adapter explicitly

A query or projection that references a model must also specify which adapter it uses for that
model. There is no defaulting to the first adapter — the binding must be unambiguous.

```yaml
queries:
  get_recipe_text:
    description: Retrieves raw recipe text given a source identifier
    model: recipes
    adapter: relative_filesystem

projections:
  save_recipe_to_db:
    description: Persists a parsed recipe to the database
    event: recipe_parsed
    models:
      - recipes
    adapter: sqla
```

Queries that do not reference any model (see SHOULD NOT below) omit `adapter` entirely.

### [MUST] One stub is generated per adapter

The generator produces separate query and projection stubs for each adapter declared on the
referenced model. A query bound to `model: recipes, adapter: sqla` gets a different context
class and implementation stub than one bound to `adapter: relative_filesystem`. These are
distinct generated files — they are not merged.

The context class field type is driven by the adapter:

| adapter               | context field type         |
|-----------------------|----------------------------|
| `sqla`                | `Session` (SQLAlchemy)     |
| `relative_filesystem` | `Path` (directory root)    |

### [SHOULD] Adapter names come from a known registry

The supported adapter identifiers are: `sqla`, `relative_filesystem`. Using an unrecognised
adapter name should produce a warning at generation time. The registry is expected to grow;
new adapters may be added without breaking existing ones.

### [SHOULD NOT] Queries must always have a model and adapter

Some query systems do not read from a model at all — for example, a query that reads directly
from a hardware source (ADC, sensor stream, message bus) has no schema-backed model to bind
to. Such queries declare neither `model` nor `adapter`, and their generated context is empty
(`pass`). This is a valid and intentional case, not an omission to be warned about.