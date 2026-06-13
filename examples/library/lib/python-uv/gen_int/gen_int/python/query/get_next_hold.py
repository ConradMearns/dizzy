# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.query.get_next_hold import GetNextHoldInput, GetNextHoldOutput
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class get_next_hold_context:
    adapter: SqlaAdapter


class get_next_hold_query(Protocol):
    """The oldest active hold for a given book, or none if the queue is empty"""

    def __call__(
        self, input: GetNextHoldInput, context: get_next_hold_context
    ) -> GetNextHoldOutput:
        ...
