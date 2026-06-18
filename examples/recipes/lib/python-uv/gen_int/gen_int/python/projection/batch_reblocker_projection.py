# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.events import BatchRunFailed
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class batch_reblocker_context:
    adapter: SqlaAdapter


class batch_reblocker_projection(Protocol):
    """Return a batch to blocked when a run attempt failed for lack of an input, so a later lot can pull it again."""

    def __call__(self, event: BatchRunFailed, context: batch_reblocker_context) -> None:
        """Apply the projection — mutate model state in response to the event."""
        ...
