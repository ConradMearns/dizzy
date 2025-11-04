"""
Procedure for deleting a todo item.
"""

from procedures.interfaces import DeleteTodoProcedureProtocol
from gen.procedures import DeleteTodoContext
from gen.commands import DeleteTodo
from gen.queries import GetTodoInput
from gen.events import TodoDeleted


class DeleteTodoProcedure:
    """Handles the DeleteTodo command."""

    def __call__(self, context: DeleteTodoContext, command: DeleteTodo) -> None:
        # Query for the todo to verify it exists
        query_result = context.query.get_todo(GetTodoInput(todo_id=command.todo_id))

        if query_result.todo is None:
            print(f"Error: Todo {command.todo_id} not found")
            return

        # Emit the TodoDeleted event
        context.emit.todo_deleted(TodoDeleted(todo_id=command.todo_id))

        print(f"Deleted todo: {query_result.todo.text} (ID: {command.todo_id})")


# Type check
_: DeleteTodoProcedureProtocol = DeleteTodoProcedure()
