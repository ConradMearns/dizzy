# Validate and record a new pantry ingredient type.
from gen_int.python.procedure.record_ingredient_context import record_ingredient_context
from gen_def.pydantic.commands import RegisterIngredient
from gen_def.pydantic.events import IngredientRegistered


def record_ingredient(
    context: record_ingredient_context,
    command: RegisterIngredient,
) -> None:
    if not command.ingredient_type.strip():
        raise ValueError("ingredient_type must not be empty")
    context.emit.ingredient_registered(
        IngredientRegistered(
            ingredient_type=command.ingredient_type.strip(),
            name=command.name.strip(),
            unit=command.unit.strip(),
        )
    )
