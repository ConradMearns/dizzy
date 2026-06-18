# Record one typed input consumed by a recipe step.
from gen_int.python.procedure.record_step_input_context import record_step_input_context
from gen_def.pydantic.commands import AddStepInput
from gen_def.pydantic.events import StepInputAdded


def record_step_input(
    context: record_step_input_context,
    command: AddStepInput,
) -> None:
    context.emit.step_input_added(
        StepInputAdded(
            recipe_id=command.recipe_id.strip(),
            step_order=command.step_order,
            ingredient_type=command.ingredient_type.strip(),
            qty=command.qty,
            unit=command.unit.strip(),
        )
    )
