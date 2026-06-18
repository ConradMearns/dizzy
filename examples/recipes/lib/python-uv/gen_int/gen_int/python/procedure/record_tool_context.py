# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Callable

from gen_def.pydantic.events import ToolRegistered


@dataclass
class record_tool_emitters:
    tool_registered: Callable[[ToolRegistered], None]


@dataclass
class record_tool_context:
    emit: record_tool_emitters
