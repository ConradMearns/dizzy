# AUTO-GENERATED — do not edit
from typing import Protocol

from gen_def.pydantic.commands import ReturnBook
from gen_int.python.procedure.process_return_context import (
    process_return_context,
)


class process_return_protocol(Protocol):
    """Record that a book has come back"""

    def __call__(
        self,
        context: process_return_context,
        command: ReturnBook,
    ) -> None:
        ...
