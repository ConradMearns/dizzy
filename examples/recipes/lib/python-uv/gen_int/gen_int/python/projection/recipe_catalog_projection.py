# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.events import RecipeDefined
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class recipe_catalog_context:
    adapter: SqlaAdapter


class recipe_catalog_projection(Protocol):
    """Persist each defined recipe header into the catalog"""

    def __call__(self, event: RecipeDefined, context: recipe_catalog_context) -> None:
        """Apply the projection — mutate model state in response to the event."""
        ...
