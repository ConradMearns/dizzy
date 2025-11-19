"""
In-memory implementations for todo queries.

HIDDEN DEPENDENCIES:
- Requires access to shared todo storage (in-memory dict)
"""

from typing import Dict
from todo.gen.queries import (
    ListTodosInput,
    ListTodos,
    GetTodoInput,
    GetTodo,
)
from todo.gen.models import Todo


class TodoStore:
    """Shared in-memory storage for todos."""

    def __init__(self):
        self.todos: Dict[str, Todo] = {}

    def add(self, todo: Todo) -> None:
        """Add a todo to the store."""
        self.todos[todo.id] = todo

    def get(self, todo_id: str) -> Todo | None:
        """Get a todo by ID."""
        return self.todos.get(todo_id)

    def list_all(self, include_completed: bool = True) -> list[Todo]:
        """List all todos, optionally filtering by completion status."""
        if include_completed:
            return list(self.todos.values())
        return [todo for todo in self.todos.values() if not todo.completed]

    def update(self, todo: Todo) -> None:
        """Update a todo in the store."""
        self.todos[todo.id] = todo

    def delete(self, todo_id: str) -> None:
        """Delete a todo from the store."""
        if todo_id in self.todos:
            del self.todos[todo_id]


class ListTodosQuery:
    """Query implementation for listing todos."""

    def __init__(self, store: TodoStore):
        self.store = store

    def execute(self, query_input: ListTodosInput) -> ListTodos:
        """Execute the ListTodos query."""
        include_completed = query_input.include_completed if query_input.include_completed is not None else True
        todos = self.store.list_all(include_completed=include_completed)
        return ListTodos(todos=[todo.id for todo in todos])


class GetTodoQuery:
    """Query implementation for getting a specific todo."""

    def __init__(self, store: TodoStore):
        self.store = store

    def execute(self, query_input: GetTodoInput) -> GetTodo:
        """Execute the GetTodo query."""
        todo = self.store.get(query_input.todo_id)
        return GetTodo(todo=todo.id if todo else None)
