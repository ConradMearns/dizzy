# AUTO-GENERATED — do not edit
from typing import Protocol

from gen_def.pydantic.commands import AddStepInput
from gen_int.python.procedure.record_step_input_context import (
    record_step_input_context,
)


class record_step_input_protocol(Protocol):
    """Record one typed input consumed by a recipe step."""

    def __call__(
        self,
        context: record_step_input_context,
        command: AddStepInput,
    ) -> None:
        ...
