# AUTO-GENERATED — do not edit
from typing import Protocol

from gen_def.pydantic.commands import PlaceHold
from gen_int.python.procedure.record_hold_context import (
    record_hold_context,
)


class record_hold_protocol(Protocol):
    """Validate and record a patron's hold on a book"""

    def __call__(
        self,
        context: record_hold_context,
        command: PlaceHold,
    ) -> None:
        ...
