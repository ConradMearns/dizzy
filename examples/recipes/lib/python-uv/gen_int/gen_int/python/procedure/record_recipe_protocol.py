# AUTO-GENERATED — do not edit
from typing import Protocol

from gen_def.pydantic.commands import DefineRecipe
from gen_int.python.procedure.record_recipe_context import (
    record_recipe_context,
)


class record_recipe_protocol(Protocol):
    """Record a recipe header. requires_type names the upstream entity this recipe consumes (empty for a root recipe like the starter); output_type names the entity it yields."""

    def __call__(
        self,
        context: record_recipe_context,
        command: DefineRecipe,
    ) -> None:
        ...
