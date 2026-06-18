# A recipe header — its requires_type, output_type, and output_unit.
from gen_int.python.query.get_recipe import get_recipe_context
from gen_def.pydantic.query.get_recipe import GetRecipeInput, GetRecipeOutput
from gen_def.sqla.models.catalog import Recipe


def get_recipe(input: GetRecipeInput, context: get_recipe_context) -> GetRecipeOutput:
    recipe = context.adapter.session.get(Recipe, input.recipe_id)
    if recipe is None:
        return GetRecipeOutput()
    return GetRecipeOutput(
        recipe_id=recipe.recipe_id,
        name=recipe.name,
        requires_type=recipe.requires_type,
        output_type=recipe.output_type,
        output_unit=recipe.output_unit,
    )
