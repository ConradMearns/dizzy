# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.events import EntityDerived
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class derivation_graph_context:
    adapter: SqlaAdapter


class derivation_graph_projection(Protocol):
    """Record each output→source derivation edge"""

    def __call__(self, event: EntityDerived, context: derivation_graph_context) -> None:
        """Apply the projection — mutate model state in response to the event."""
        ...
