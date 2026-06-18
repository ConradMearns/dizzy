# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.events import EntityProduced
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class inventory_store_context:
    adapter: SqlaAdapter


class inventory_store_projection(Protocol):
    """Record each produced entity lot as available inventory"""

    def __call__(self, event: EntityProduced, context: inventory_store_context) -> None:
        """Apply the projection — mutate model state in response to the event."""
        ...
