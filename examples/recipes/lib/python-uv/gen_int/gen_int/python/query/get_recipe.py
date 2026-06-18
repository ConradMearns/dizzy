# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.query.get_recipe import GetRecipeInput, GetRecipeOutput
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class get_recipe_context:
    adapter: SqlaAdapter


class get_recipe_query(Protocol):
    """A recipe header — its requires_type, output_type, and output_unit"""

    def __call__(
        self, input: GetRecipeInput, context: get_recipe_context
    ) -> GetRecipeOutput:
        ...
