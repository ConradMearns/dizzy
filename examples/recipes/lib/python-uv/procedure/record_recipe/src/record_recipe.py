# Record a recipe header. requires_type names the upstream entity this recipe
# consumes (empty for a root recipe); output_type names the entity it yields.
from gen_int.python.procedure.record_recipe_context import record_recipe_context
from gen_def.pydantic.commands import DefineRecipe
from gen_def.pydantic.events import RecipeDefined


def record_recipe(
    context: record_recipe_context,
    command: DefineRecipe,
) -> None:
    if not command.recipe_id.strip():
        raise ValueError("recipe_id must not be empty")
    requires = (command.requires_type or "").strip() or None
    context.emit.recipe_defined(
        RecipeDefined(
            recipe_id=command.recipe_id.strip(),
            name=command.name.strip(),
            requires_type=requires,
            output_type=command.output_type.strip(),
            output_unit=command.output_unit.strip(),
        )
    )
