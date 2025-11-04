"""
Procedure for adding a new todo item.
"""

import uuid
from datetime import datetime, timezone
from procedures.interfaces import AddTodoProcedureProtocol
from gen.procedures import AddTodoContext
from gen.commands import AddTodo
from gen.queries import ListTodosInput
from gen.events import TodoAdded
from gen.models import Todo


class AddTodoProcedure:
    """Handles the AddTodo command."""

    def __call__(self, context: AddTodoContext, command: AddTodo) -> None:
        # Generate a new unique ID for the todo
        todo_id = str(uuid.uuid4())

        # Create the new todo
        todo = Todo(
            id=todo_id,
            text=command.text,
            completed=False,
            created_at=datetime.now(timezone.utc),
            completed_at=None,
        )

        # Emit the TodoAdded event
        context.emit.todo_added(TodoAdded(
            todo_id=todo.id,
            text=todo.text,
            created_at=todo.created_at
        ))

        print(f"Added todo: {todo.text} (ID: {todo.id})")


# Type check
_: AddTodoProcedureProtocol = AddTodoProcedure()
