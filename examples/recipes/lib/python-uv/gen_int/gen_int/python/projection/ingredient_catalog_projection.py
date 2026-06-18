# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.events import IngredientRegistered
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class ingredient_catalog_context:
    adapter: SqlaAdapter


class ingredient_catalog_projection(Protocol):
    """Persist each registered ingredient into the catalog"""

    def __call__(self, event: IngredientRegistered, context: ingredient_catalog_context) -> None:
        """Apply the projection — mutate model state in response to the event."""
        ...
