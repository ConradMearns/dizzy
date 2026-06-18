# The typed inputs of a recipe's steps, as parallel lists (one entry per input).
from gen_int.python.query.get_step_inputs import get_step_inputs_context
from gen_def.pydantic.query.get_step_inputs import GetStepInputsInput, GetStepInputsOutput
from gen_def.sqla.models.catalog import StepInput


def get_step_inputs(
    input: GetStepInputsInput, context: get_step_inputs_context
) -> GetStepInputsOutput:
    rows = (
        context.adapter.session.query(StepInput)
        .filter(StepInput.recipe_id == input.recipe_id)
        .order_by(StepInput.step_order)
        .all()
    )
    return GetStepInputsOutput(
        step_orders=[r.step_order for r in rows],
        ingredient_types=[r.ingredient_type for r in rows],
        qtys=[r.qty for r in rows],
        units=[r.unit for r in rows],
    )
