# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.query.list_recipes import ListRecipesInput, ListRecipesOutput
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class list_recipes_context:
    adapter: SqlaAdapter


class list_recipes_query(Protocol):
    """All recipe headers, for a dashboard"""

    def __call__(
        self, input: ListRecipesInput, context: list_recipes_context
    ) -> ListRecipesOutput:
        ...
