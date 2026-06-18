# All recipe headers, as parallel lists (one entry per recipe).
from gen_int.python.query.list_recipes import list_recipes_context
from gen_def.pydantic.query.list_recipes import ListRecipesInput, ListRecipesOutput
from gen_def.sqla.models.catalog import Recipe


def list_recipes(input: ListRecipesInput, context: list_recipes_context) -> ListRecipesOutput:
    rows = context.adapter.session.query(Recipe).order_by(Recipe.recipe_id).all()
    return ListRecipesOutput(
        recipe_ids=[r.recipe_id for r in rows],
        names=[r.name for r in rows],
        requires_types=[r.requires_type or "" for r in rows],
        output_types=[r.output_type for r in rows],
        output_units=[r.output_unit for r in rows],
    )
