# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.events import EntityConsumed
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class inventory_consumer_context:
    adapter: SqlaAdapter


class inventory_consumer_projection(Protocol):
    """Mark an inventory lot unavailable once it is consumed"""

    def __call__(self, event: EntityConsumed, context: inventory_consumer_context) -> None:
        """Apply the projection — mutate model state in response to the event."""
        ...
