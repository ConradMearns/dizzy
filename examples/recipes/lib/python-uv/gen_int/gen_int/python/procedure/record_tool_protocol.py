# AUTO-GENERATED — do not edit
from typing import Protocol

from gen_def.pydantic.commands import RegisterTool
from gen_int.python.procedure.record_tool_context import (
    record_tool_context,
)


class record_tool_protocol(Protocol):
    """Validate and record a new tool."""

    def __call__(
        self,
        context: record_tool_context,
        command: RegisterTool,
    ) -> None:
        ...
