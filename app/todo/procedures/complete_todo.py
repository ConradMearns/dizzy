"""
Procedure for marking a todo item as completed.
"""

from datetime import datetime, timezone
from procedures.interfaces import CompleteTodoProcedureProtocol
from gen.procedures import CompleteTodoContext
from gen.commands import CompleteTodo
from gen.queries import GetTodoInput
from gen.events import TodoCompleted


class CompleteTodoProcedure:
    """Handles the CompleteTodo command."""

    def __call__(self, context: CompleteTodoContext, command: CompleteTodo) -> None:
        # Query for the todo to verify it exists
        query_result = context.query.get_todo(GetTodoInput(todo_id=command.todo_id))

        if query_result.todo is None:
            print(f"Error: Todo {command.todo_id} not found")
            return

        if query_result.todo.completed:
            print(f"Todo {command.todo_id} is already completed")
            return

        # Emit the TodoCompleted event
        completed_at = datetime.now(timezone.utc)
        context.emit.todo_completed(
            TodoCompleted(todo_id=command.todo_id, completed_at=completed_at)
        )

        print(f"Completed todo: {query_result.todo.text} (ID: {command.todo_id})")


# Type check
_: CompleteTodoProcedureProtocol = CompleteTodoProcedure()
