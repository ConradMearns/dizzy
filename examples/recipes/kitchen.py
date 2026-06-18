"""Host wiring for the recipes feature, shared by every host that runs it.

Dizzy generates the typed pieces (commands, events, procedures, projections,
queries, the policy); a *host* owns the database and connects them: it routes
each emitted event to its projections and to the policy, and binds each query
over the read adapter. ``demo.py`` (a CLI host) and ``server.py`` (an HTTP host)
both call :func:`build_kitchen` rather than repeat that wiring.

A :class:`Kitchen` is just a bundle of ready-to-call command runners and query
callables, all bound to one ``SqlaAdapter`` (i.e. one database session). Build a
fresh one per unit of work (per CLI run, per HTTP request).

The optional ``observer`` is called with ``(event_name, event)`` for every event
the feature emits — hosts use it to log, print, or collect the cascade.
"""

from dataclasses import dataclass
from typing import Any, Callable, Optional

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
from gen_def.pydantic.query.get_recipe import GetRecipeInput, GetRecipeOutput
from gen_def.pydantic.query.get_recipe_steps import GetRecipeStepsInput, GetRecipeStepsOutput
from gen_def.pydantic.query.get_step_inputs import GetStepInputsInput, GetStepInputsOutput
from gen_def.pydantic.query.get_batch import GetBatchInput, GetBatchOutput
from gen_def.pydantic.query.check_inventory import CheckInventoryInput, CheckInventoryOutput
from gen_def.pydantic.query.find_blocked_batches import (
    FindBlockedBatchesInput,
    FindBlockedBatchesOutput,
)
from gen_def.pydantic.query.trace_provenance import TraceProvenanceInput, TraceProvenanceOutput

from gen_int.python.adapters.sqla import SqlaAdapter

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
from gen_int.python.policy.advance_ready_batches_context import (
    advance_ready_batches_context,
    advance_ready_batches_emitters,
    advance_ready_batches_queries,
)
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
from gen_int.python.query.get_recipe import get_recipe_context
from gen_int.python.query.get_recipe_steps import get_recipe_steps_context
from gen_int.python.query.get_step_inputs import get_step_inputs_context
from gen_int.python.query.get_batch import get_batch_context
from gen_int.python.query.check_inventory import check_inventory_context
from gen_int.python.query.find_blocked_batches import find_blocked_batches_context
from gen_int.python.query.trace_provenance import trace_provenance_context

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


EventObserver = Callable[[str, Any], None]


@dataclass
class Kitchen:
    """Command runners and query callables bound to one database session."""

    # Commands (each runs a procedure; effects flow through events to projections).
    register_ingredient: Callable[[RegisterIngredient], None]
    register_tool: Callable[[RegisterTool], None]
    define_recipe: Callable[[DefineRecipe], None]
    add_recipe_step: Callable[[AddRecipeStep], None]
    add_step_input: Callable[[AddStepInput], None]
    start_batch: Callable[[StartBatch], None]
    advance_batch: Callable[[AdvanceBatch], None]

    # Queries (read the projected models back out).
    get_recipe: Callable[[GetRecipeInput], GetRecipeOutput]
    get_recipe_steps: Callable[[GetRecipeStepsInput], GetRecipeStepsOutput]
    get_step_inputs: Callable[[GetStepInputsInput], GetStepInputsOutput]
    get_batch: Callable[[GetBatchInput], GetBatchOutput]
    check_inventory: Callable[[CheckInventoryInput], CheckInventoryOutput]
    find_blocked_batches: Callable[[FindBlockedBatchesInput], FindBlockedBatchesOutput]
    trace_provenance: Callable[[TraceProvenanceInput], TraceProvenanceOutput]


def build_kitchen(adapter: SqlaAdapter, observer: Optional[EventObserver] = None) -> Kitchen:
    """Wire the feature over one read/write adapter and return a :class:`Kitchen`."""

    def note(name: str, event: Any) -> None:
        if observer is not None:
            observer(name, event)

    # --- Queries, each bound to the read adapter ---
    def q_get_recipe(inp: GetRecipeInput) -> GetRecipeOutput:
        return get_recipe(inp, get_recipe_context(adapter=adapter))

    def q_get_recipe_steps(inp: GetRecipeStepsInput) -> GetRecipeStepsOutput:
        return get_recipe_steps(inp, get_recipe_steps_context(adapter=adapter))

    def q_get_step_inputs(inp: GetStepInputsInput) -> GetStepInputsOutput:
        return get_step_inputs(inp, get_step_inputs_context(adapter=adapter))

    def q_get_batch(inp: GetBatchInput) -> GetBatchOutput:
        return get_batch(inp, get_batch_context(adapter=adapter))

    def q_check_inventory(inp: CheckInventoryInput) -> CheckInventoryOutput:
        return check_inventory(inp, check_inventory_context(adapter=adapter))

    def q_find_blocked_batches(inp: FindBlockedBatchesInput) -> FindBlockedBatchesOutput:
        return find_blocked_batches(inp, find_blocked_batches_context(adapter=adapter))

    def q_trace_provenance(inp: TraceProvenanceInput) -> TraceProvenanceOutput:
        return trace_provenance(inp, trace_provenance_context(adapter=adapter))

    # --- Event routing (projections + the policy) ---
    def on_ingredient_registered(e: IngredientRegistered) -> None:
        ingredient_catalog(e, ingredient_catalog_context(adapter=adapter))
        note("ingredient_registered", e)

    def on_tool_registered(e: ToolRegistered) -> None:
        tool_catalog(e, tool_catalog_context(adapter=adapter))
        note("tool_registered", e)

    def on_recipe_defined(e: RecipeDefined) -> None:
        recipe_catalog(e, recipe_catalog_context(adapter=adapter))
        note("recipe_defined", e)

    def on_recipe_step_added(e: RecipeStepAdded) -> None:
        step_catalog(e, step_catalog_context(adapter=adapter))
        note("recipe_step_added", e)

    def on_step_input_added(e: StepInputAdded) -> None:
        step_input_catalog(e, step_input_catalog_context(adapter=adapter))
        note("step_input_added", e)

    def on_batch_opened(e: BatchOpened) -> None:
        batch_store(e, batch_store_context(adapter=adapter))
        note("batch_opened", e)

    def on_batch_completed(e: BatchCompleted) -> None:
        batch_finalizer(e, batch_finalizer_context(adapter=adapter))
        note("batch_completed", e)

    def on_step_performed(e: StepPerformed) -> None:
        note("step_performed", e)

    def on_entity_consumed(e: EntityConsumed) -> None:
        inventory_consumer(e, inventory_consumer_context(adapter=adapter))
        note("entity_consumed", e)

    def on_entity_derived(e: EntityDerived) -> None:
        derivation_graph(e, derivation_graph_context(adapter=adapter))
        note("entity_derived", e)

    def on_entity_produced(e: EntityProduced) -> None:
        # Data loop first: fold the fact into inventory + the provenance graph,
        # so the read state is current before the policy queries it.
        inventory_store(e, inventory_store_context(adapter=adapter))
        generation_graph(e, generation_graph_context(adapter=adapter))
        note("entity_produced", e)
        # Reactivity loop: the policy decides what to advance next.
        advance_ready_batches(
            e,
            advance_ready_batches_context(
                emit=advance_ready_batches_emitters(advance_batch=dispatch_advance_batch),
                query=advance_ready_batches_queries(
                    find_blocked_batches=q_find_blocked_batches
                ),
            ),
        )

    # --- Procedure contexts ---
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
        query=open_batch_queries(get_recipe=q_get_recipe, check_inventory=q_check_inventory),
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

    # advance_batch is dispatched both by callers and by the policy; the host
    # routes it into run_batch, whose entity_produced re-triggers the policy.
    def dispatch_advance_batch(command: AdvanceBatch) -> None:
        run_batch(run_batch_ctx, command)

    return Kitchen(
        register_ingredient=lambda c: record_ingredient(record_ingredient_ctx, c),
        register_tool=lambda c: record_tool(record_tool_ctx, c),
        define_recipe=lambda c: record_recipe(record_recipe_ctx, c),
        add_recipe_step=lambda c: record_step(record_step_ctx, c),
        add_step_input=lambda c: record_step_input(record_step_input_ctx, c),
        start_batch=lambda c: open_batch(open_batch_ctx, c),
        advance_batch=dispatch_advance_batch,
        get_recipe=q_get_recipe,
        get_recipe_steps=q_get_recipe_steps,
        get_step_inputs=q_get_step_inputs,
        get_batch=q_get_batch,
        check_inventory=q_check_inventory,
        find_blocked_batches=q_find_blocked_batches,
        trace_provenance=q_trace_provenance,
    )
