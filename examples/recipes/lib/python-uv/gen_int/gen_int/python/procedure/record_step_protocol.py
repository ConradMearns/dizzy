# AUTO-GENERATED — do not edit
from typing import Protocol

from gen_def.pydantic.commands import AddRecipeStep
from gen_int.python.procedure.record_step_context import (
    record_step_context,
)


class record_step_protocol(Protocol):
    """Record one ordered step of a recipe as structured data."""

    def __call__(
        self,
        context: record_step_context,
        command: AddRecipeStep,
    ) -> None:
        ...
