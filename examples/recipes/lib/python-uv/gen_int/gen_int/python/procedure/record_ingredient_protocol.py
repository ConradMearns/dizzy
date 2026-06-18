# AUTO-GENERATED — do not edit
from typing import Protocol

from gen_def.pydantic.commands import RegisterIngredient
from gen_int.python.procedure.record_ingredient_context import (
    record_ingredient_context,
)


class record_ingredient_protocol(Protocol):
    """Validate and record a new pantry ingredient type."""

    def __call__(
        self,
        context: record_ingredient_context,
        command: RegisterIngredient,
    ) -> None:
        ...
