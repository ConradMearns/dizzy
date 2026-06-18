# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.events import BatchOpened
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class batch_store_context:
    adapter: SqlaAdapter


class batch_store_projection(Protocol):
    """Insert each opened batch with its status and requires_type"""

    def __call__(self, event: BatchOpened, context: batch_store_context) -> None:
        """Apply the projection — mutate model state in response to the event."""
        ...
