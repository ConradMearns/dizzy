"""Wire the generated recipes feature together and run the chained cascade.

This is the glue a host application writes by hand: it owns the database, the
event/command routing, and the wiring. Dizzy generates the typed pieces; this
file connects them.

The point of this example is a POLICY-driven cascade over PROV-style events.
Three recipes chain: each one's output entity is the next one's required input.

    active_starter ─▶ sourdough_loaf ─▶ garlic_croutons

All three batches are opened up front. The loaf and croutons batches open
*blocked*, because the entity they require does not exist yet. We then advance
only the starter batch by hand. Each batch ends by emitting entity_produced
(prov:wasGeneratedBy); the host routes that event to the projections (data loop)
and then to the advance_ready_batches policy (reactivity loop), which asks
find_blocked_batches who was waiting on that entity type and dispatches
advance_batch for them. So finishing the starter cascades through the loaf and
into the croutons from a single trigger.

Run inside the workspace environment (from the repo root):

    uv sync --project examples/recipes/lib/python-uv
    uv run --project examples/recipes/lib/python-uv python examples/recipes/demo.py
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from gen_def.pydantic.commands import (
    RegisterIngredient,
    RegisterTool,
    DefineRecipe,
    AddRecipeStep,
    AddStepInput,
    StartBatch,
    AdvanceBatch,
)
from gen_def.pydantic.events import (
    IngredientRegistered,
    ToolRegistered,
    RecipeDefined,
    RecipeStepAdded,
    StepInputAdded,
    BatchOpened,
    StepPerformed,
    EntityConsumed,
    EntityProduced,
    EntityDerived,
    BatchCompleted,
)
from gen_def.pydantic.query.get_recipe import GetRecipeInput
from gen_def.pydantic.query.get_batch import GetBatchInput
from gen_def.pydantic.query.check_inventory import CheckInventoryInput
from gen_def.pydantic.query.find_blocked_batches import FindBlockedBatchesInput
from gen_def.pydantic.query.trace_provenance import TraceProvenanceInput

# Each model schema declares its own SQLAlchemy Base; create them all.
from gen_def.sqla.models.catalog import Base as CatalogBase
from gen_def.sqla.models.batches import Base as BatchesBase
from gen_def.sqla.models.inventory import Base as InventoryBase
from gen_def.sqla.models.provenance import Base as ProvenanceBase

from gen_int.python.adapters.sqla import SqlaAdapter

# Procedure contexts.
from gen_int.python.procedure.record_ingredient_context import (
    record_ingredient_context,
    record_ingredient_emitters,
)
from gen_int.python.procedure.record_tool_context import (
    record_tool_context,
    record_tool_emitters,
)
from gen_int.python.procedure.record_recipe_context import (
    record_recipe_context,
    record_recipe_emitters,
)
from gen_int.python.procedure.record_step_context import (
    record_step_context,
    record_step_emitters,
)
from gen_int.python.procedure.record_step_input_context import (
    record_step_input_context,
    record_step_input_emitters,
)
from gen_int.python.procedure.open_batch_context import (
    open_batch_context,
    open_batch_emitters,
    open_batch_queries,
)
from gen_int.python.procedure.run_batch_context import (
    run_batch_context,
    run_batch_emitters,
    run_batch_queries,
)

# Policy context.
from gen_int.python.policy.advance_ready_batches_context import (
    advance_ready_batches_context,
    advance_ready_batches_emitters,
    advance_ready_batches_queries,
)

# Projection contexts.
from gen_int.python.projection.ingredient_catalog_projection import ingredient_catalog_context
from gen_int.python.projection.tool_catalog_projection import tool_catalog_context
from gen_int.python.projection.recipe_catalog_projection import recipe_catalog_context
from gen_int.python.projection.step_catalog_projection import step_catalog_context
from gen_int.python.projection.step_input_catalog_projection import step_input_catalog_context
from gen_int.python.projection.batch_store_projection import batch_store_context
from gen_int.python.projection.batch_finalizer_projection import batch_finalizer_context
from gen_int.python.projection.inventory_store_projection import inventory_store_context
from gen_int.python.projection.inventory_consumer_projection import inventory_consumer_context
from gen_int.python.projection.generation_graph_projection import generation_graph_context
from gen_int.python.projection.derivation_graph_projection import derivation_graph_context

# Query contexts.
from gen_int.python.query.get_recipe import get_recipe_context
from gen_int.python.query.get_recipe_steps import get_recipe_steps_context
from gen_int.python.query.get_step_inputs import get_step_inputs_context
from gen_int.python.query.get_batch import get_batch_context
from gen_int.python.query.check_inventory import check_inventory_context
from gen_int.python.query.find_blocked_batches import find_blocked_batches_context
from gen_int.python.query.trace_provenance import trace_provenance_context

# Each element is its own installed package, exposing a top-level module.
from record_ingredient import record_ingredient
from record_tool import record_tool
from record_recipe import record_recipe
from record_step import record_step
from record_step_input import record_step_input
from open_batch import open_batch
from run_batch import run_batch
from advance_ready_batches import advance_ready_batches
from ingredient_catalog import ingredient_catalog
from tool_catalog import tool_catalog
from recipe_catalog import recipe_catalog
from step_catalog import step_catalog
from step_input_catalog import step_input_catalog
from batch_store import batch_store
from batch_finalizer import batch_finalizer
from inventory_store import inventory_store
from inventory_consumer import inventory_consumer
from generation_graph import generation_graph
from derivation_graph import derivation_graph
from get_recipe import get_recipe
from get_recipe_steps import get_recipe_steps
from get_step_inputs import get_step_inputs
from get_batch import get_batch
from check_inventory import check_inventory
from find_blocked_batches import find_blocked_batches
from trace_provenance import trace_provenance


def main() -> None:
    # The host owns persistence. Here: an in-memory SQLite database.
    engine = create_engine("sqlite://")
    for base in (CatalogBase, BatchesBase, InventoryBase, ProvenanceBase):
        base.metadata.create_all(engine)
    session = Session(engine)
    adapter = SqlaAdapter(session=session)

    # --- Queries, each bound to the read adapter ---
    def q_get_recipe(inp):
        return get_recipe(inp, get_recipe_context(adapter=adapter))

    def q_get_recipe_steps(inp):
        return get_recipe_steps(inp, get_recipe_steps_context(adapter=adapter))

    def q_get_step_inputs(inp):
        return get_step_inputs(inp, get_step_inputs_context(adapter=adapter))

    def q_get_batch(inp):
        return get_batch(inp, get_batch_context(adapter=adapter))

    def q_check_inventory(inp):
        return check_inventory(inp, check_inventory_context(adapter=adapter))

    def q_find_blocked_batches(inp):
        return find_blocked_batches(inp, find_blocked_batches_context(adapter=adapter))

    # --- Event routing (the host's reaction wiring) ---
    def on_ingredient_registered(e: IngredientRegistered) -> None:
        ingredient_catalog(e, ingredient_catalog_context(adapter=adapter))

    def on_tool_registered(e: ToolRegistered) -> None:
        tool_catalog(e, tool_catalog_context(adapter=adapter))

    def on_recipe_defined(e: RecipeDefined) -> None:
        recipe_catalog(e, recipe_catalog_context(adapter=adapter))

    def on_recipe_step_added(e: RecipeStepAdded) -> None:
        step_catalog(e, step_catalog_context(adapter=adapter))

    def on_step_input_added(e: StepInputAdded) -> None:
        step_input_catalog(e, step_input_catalog_context(adapter=adapter))

    def on_batch_opened(e: BatchOpened) -> None:
        batch_store(e, batch_store_context(adapter=adapter))
        flag = "" if e.status == "ready" else f" (blocked on {e.requires_type})"
        print(f"  opened batch {e.batch_id} [{e.status}]{flag}")

    def on_batch_completed(e: BatchCompleted) -> None:
        batch_finalizer(e, batch_finalizer_context(adapter=adapter))

    def on_step_performed(e: StepPerformed) -> None:
        tool = f" with {e.tool_id}" if e.tool_id else ""
        print(f"    · {e.batch_id} step {e.step_order}: {e.activity_kind}{tool}")

    def on_entity_consumed(e: EntityConsumed) -> None:
        inventory_consumer(e, inventory_consumer_context(adapter=adapter))

    def on_entity_derived(e: EntityDerived) -> None:
        derivation_graph(e, derivation_graph_context(adapter=adapter))

    def on_entity_produced(e: EntityProduced) -> None:
        # Data loop first: fold the fact into inventory + the provenance graph,
        # so the read state is current before the policy queries it.
        inventory_store(e, inventory_store_context(adapter=adapter))
        generation_graph(e, generation_graph_context(adapter=adapter))
        print(f"  ✓ {e.batch_id} produced {e.entity_type} ({e.entity_id})")
        # Reactivity loop: the policy decides what to do next.
        advance_ready_batches(
            e,
            advance_ready_batches_context(
                emit=advance_ready_batches_emitters(advance_batch=dispatch_advance_batch),
                query=advance_ready_batches_queries(
                    find_blocked_batches=q_find_blocked_batches
                ),
            ),
        )

    # --- Procedure contexts (command -> procedure -> event) ---
    record_ingredient_ctx = record_ingredient_context(
        emit=record_ingredient_emitters(ingredient_registered=on_ingredient_registered)
    )
    record_tool_ctx = record_tool_context(
        emit=record_tool_emitters(tool_registered=on_tool_registered)
    )
    record_recipe_ctx = record_recipe_context(
        emit=record_recipe_emitters(recipe_defined=on_recipe_defined)
    )
    record_step_ctx = record_step_context(
        emit=record_step_emitters(recipe_step_added=on_recipe_step_added)
    )
    record_step_input_ctx = record_step_input_context(
        emit=record_step_input_emitters(step_input_added=on_step_input_added)
    )
    open_batch_ctx = open_batch_context(
        emit=open_batch_emitters(batch_opened=on_batch_opened),
        query=open_batch_queries(
            get_recipe=q_get_recipe, check_inventory=q_check_inventory
        ),
    )
    run_batch_ctx = run_batch_context(
        emit=run_batch_emitters(
            step_performed=on_step_performed,
            entity_consumed=on_entity_consumed,
            entity_produced=on_entity_produced,
            entity_derived=on_entity_derived,
            batch_completed=on_batch_completed,
        ),
        query=run_batch_queries(
            get_batch=q_get_batch,
            get_recipe=q_get_recipe,
            get_recipe_steps=q_get_recipe_steps,
            get_step_inputs=q_get_step_inputs,
            check_inventory=q_check_inventory,
        ),
    )

    # The advance_batch command is dispatched by the policy (and once by us, to
    # kick off the chain). The host routes it to run_batch.
    def dispatch_advance_batch(command: AdvanceBatch) -> None:
        run_batch(run_batch_ctx, command)

    # --- Build the catalog: ingredients, tools, recipes, and typed steps ---
    print("Catalog:")
    for ing, name, unit in [
        ("flour", "Bread flour", "g"),
        ("water", "Water", "ml"),
        ("salt", "Fine sea salt", "g"),
        ("olive_oil", "Olive oil", "ml"),
        ("garlic", "Garlic", "clove"),
    ]:
        record_ingredient(
            record_ingredient_ctx,
            RegisterIngredient(ingredient_type=ing, name=name, unit=unit),
        )
    for tool_id, name in [
        ("jar", "Glass fermentation jar"),
        ("mixer", "Stand mixer"),
        ("oven", "Deck oven"),
        ("knife", "Chef's knife"),
        ("bowl", "Mixing bowl"),
    ]:
        record_tool(record_tool_ctx, RegisterTool(tool_id=tool_id, name=name))
    print("  5 ingredients, 5 tools registered")

    def define(recipe_id, name, requires_type, output_type, output_unit, steps, inputs):
        record_recipe(
            record_recipe_ctx,
            DefineRecipe(
                recipe_id=recipe_id,
                name=name,
                requires_type=requires_type,
                output_type=output_type,
                output_unit=output_unit,
            ),
        )
        for order, kind, tool in steps:
            record_step(
                record_step_ctx,
                AddRecipeStep(
                    recipe_id=recipe_id, step_order=order, activity_kind=kind, tool_id=tool
                ),
            )
        for order, ingredient, qty, unit in inputs:
            record_step_input(
                record_step_input_ctx,
                AddStepInput(
                    recipe_id=recipe_id,
                    step_order=order,
                    ingredient_type=ingredient,
                    qty=qty,
                    unit=unit,
                ),
            )

    define(
        "cultivate_starter",
        "Sourdough starter",
        None,
        "active_starter",
        "jar",
        steps=[(1, "mix", "jar"), (2, "ferment", "jar")],
        inputs=[(1, "flour", 100, "g"), (1, "water", 100, "ml")],
    )
    define(
        "bake_sourdough",
        "Sourdough loaf",
        "active_starter",
        "sourdough_loaf",
        "loaf",
        steps=[(1, "mix", "mixer"), (2, "ferment", "jar"), (3, "bake", "oven")],
        inputs=[(1, "flour", 500, "g"), (1, "water", 350, "ml"), (1, "salt", 10, "g")],
    )
    define(
        "make_croutons",
        "Garlic croutons",
        "sourdough_loaf",
        "garlic_croutons",
        "bowl",
        steps=[(1, "cut", "knife"), (2, "toss", "bowl"), (3, "bake", "oven")],
        inputs=[(2, "olive_oil", 30, "ml"), (2, "garlic", 2, "clove")],
    )
    print("  3 recipes defined (starter ▶ loaf ▶ croutons)")

    # --- Open all three batches up front ---
    # The loaf and croutons batches require entities that do not exist yet, so they
    # open *blocked*. The starter batch requires nothing, so it opens ready.
    print("\nOpening batches:")
    open_batch(open_batch_ctx, StartBatch(batch_id="croutons-1", recipe_id="make_croutons"))
    open_batch(open_batch_ctx, StartBatch(batch_id="loaf-1", recipe_id="bake_sourdough"))
    open_batch(open_batch_ctx, StartBatch(batch_id="starter-1", recipe_id="cultivate_starter"))

    # --- One trigger: advance the starter. The policy cascades the rest. ---
    print("\nAdvancing starter-1 (watch the cascade):")
    dispatch_advance_batch(AdvanceBatch(batch_id="starter-1"))

    # --- Read the results back out ---
    print("\nFinal batch states:")
    for batch_id in ("starter-1", "loaf-1", "croutons-1"):
        b = q_get_batch(GetBatchInput(batch_id=batch_id))
        print(f"  {batch_id}: {b.status}")

    print("\nProvenance of the croutons (trace_provenance):")
    trace = trace_provenance(
        TraceProvenanceInput(entity_id="croutons-1:garlic_croutons"),
        trace_provenance_context(adapter=adapter),
    )
    for line in trace.lines:
        print(f"  {line}")


if __name__ == "__main__":
    main()
