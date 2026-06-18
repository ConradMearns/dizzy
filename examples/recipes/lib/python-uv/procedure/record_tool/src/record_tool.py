# Validate and record a new tool (a PROV agent).
from gen_int.python.procedure.record_tool_context import record_tool_context
from gen_def.pydantic.commands import RegisterTool
from gen_def.pydantic.events import ToolRegistered


def record_tool(
    context: record_tool_context,
    command: RegisterTool,
) -> None:
    if not command.tool_id.strip():
        raise ValueError("tool_id must not be empty")
    context.emit.tool_registered(
        ToolRegistered(
            tool_id=command.tool_id.strip(),
            name=command.name.strip(),
        )
    )
