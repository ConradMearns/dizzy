# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.query.get_recipe_steps import GetRecipeStepsInput, GetRecipeStepsOutput
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class get_recipe_steps_context:
    adapter: SqlaAdapter


class get_recipe_steps_query(Protocol):
    """The ordered steps of a recipe, as parallel lists"""

    def __call__(
        self, input: GetRecipeStepsInput, context: get_recipe_steps_context
    ) -> GetRecipeStepsOutput:
        ...
