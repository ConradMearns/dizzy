# Open a batch for a recipe. If the recipe has no requires_type, or an entity of
# that type is already available, the batch is ready; otherwise it is blocked.
from gen_int.python.procedure.open_batch_context import open_batch_context
from gen_def.pydantic.commands import StartBatch
from gen_def.pydantic.events import BatchOpened
from gen_def.pydantic.query.get_recipe import GetRecipeInput
from gen_def.pydantic.query.check_inventory import CheckInventoryInput


def open_batch(
    context: open_batch_context,
    command: StartBatch,
) -> None:
    recipe = context.query.get_recipe(GetRecipeInput(recipe_id=command.recipe_id))
    if recipe.recipe_id is None:
        raise ValueError(f"unknown recipe: {command.recipe_id}")

    requires = (recipe.requires_type or "").strip() or None
    if requires is None:
        status = "ready"
    else:
        inventory = context.query.check_inventory(CheckInventoryInput(entity_type=requires))
        status = "ready" if inventory.available else "blocked"

    context.emit.batch_opened(
        BatchOpened(
            batch_id=command.batch_id,
            recipe_id=command.recipe_id,
            requires_type=requires,
            status=status,
        )
    )
