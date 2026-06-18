# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.events import EntityProduced
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class generation_graph_context:
    adapter: SqlaAdapter


class generation_graph_projection(Protocol):
    """Record each entity's generation (which batch/type produced it)"""

    def __call__(self, event: EntityProduced, context: generation_graph_context) -> None:
        """Apply the projection — mutate model state in response to the event."""
        ...
