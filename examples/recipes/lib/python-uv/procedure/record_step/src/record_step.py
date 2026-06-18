# Record one ordered step of a recipe as structured data.
from gen_int.python.procedure.record_step_context import record_step_context
from gen_def.pydantic.commands import AddRecipeStep
from gen_def.pydantic.events import RecipeStepAdded


def record_step(
    context: record_step_context,
    command: AddRecipeStep,
) -> None:
    tool = (command.tool_id or "").strip() or None
    context.emit.recipe_step_added(
        RecipeStepAdded(
            recipe_id=command.recipe_id.strip(),
            step_order=command.step_order,
            activity_kind=command.activity_kind.strip(),
            tool_id=tool,
        )
    )
