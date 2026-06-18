# The ordered steps of a recipe, as parallel lists (one entry per step).
from gen_int.python.query.get_recipe_steps import get_recipe_steps_context
from gen_def.pydantic.query.get_recipe_steps import GetRecipeStepsInput, GetRecipeStepsOutput
from gen_def.sqla.models.catalog import RecipeStep


def get_recipe_steps(
    input: GetRecipeStepsInput, context: get_recipe_steps_context
) -> GetRecipeStepsOutput:
    rows = (
        context.adapter.session.query(RecipeStep)
        .filter(RecipeStep.recipe_id == input.recipe_id)
        .order_by(RecipeStep.step_order)
        .all()
    )
    return GetRecipeStepsOutput(
        step_orders=[r.step_order for r in rows],
        activity_kinds=[r.activity_kind for r in rows],
        tool_ids=[r.tool_id or "" for r in rows],
    )
