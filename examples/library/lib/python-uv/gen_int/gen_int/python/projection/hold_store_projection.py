# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.events import HoldPlaced
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class hold_store_context:
    adapter: SqlaAdapter


class hold_store_projection(Protocol):
    """Persist each placed hold into the holds model"""

    def __call__(self, event: HoldPlaced, context: hold_store_context) -> None:
        """Apply the projection — mutate model state in response to the event."""
        ...
