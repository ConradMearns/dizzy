"""
FastAPI server for todo app with Server-Sent Events (SSE) support.

Implements the Dizzy service pattern with:
- Command queue for incoming commands
- Event queue for emitted events
- SSE streaming to push events to browsers
"""

import asyncio
import json
from typing import Dict, Any
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Generated types
from todo.gen.commands import AddTodo, CompleteTodo, DeleteTodo
from todo.gen.events import TodoAdded, TodoCompleted, TodoDeleted
from todo.gen.procedures import (
    AddTodoContext,
    AddTodoEmitters,
    AddTodoQueries,
    CompleteTodoContext,
    CompleteTodoEmitters,
    CompleteTodoQueries,
    DeleteTodoContext,
    DeleteTodoEmitters,
    DeleteTodoQueries,
)

# Implementations
from todo.procedures.add_todo import AddTodoProcedure
from todo.procedures.complete_todo import CompleteTodoProcedure
from todo.procedures.delete_todo import DeleteTodoProcedure
from todo.queries.todo_queries import TodoStore, ListTodosQuery, GetTodoQuery

app = FastAPI(title="Dizzy Todo App")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TodoService:
    """
    Main service class implementing the Dizzy pattern.

    Follows the st_service.py example with:
    - command_queue: incoming commands to process
    - event_queue: events emitted by procedures
    - command_map: maps command types to procedures
    - procedure_map: maps procedures to their contexts
    - sse_subscribers: queues for SSE event streaming
    """

    def __init__(self):
        # Shared storage
        self.store = TodoStore()

        # Queues
        self.command_queue = []
        self.event_queue = []

        # SSE subscribers (asyncio queues for each client)
        self.sse_subscribers: list[asyncio.Queue] = []

        # Procedure instances
        self.add_todo_proc = AddTodoProcedure()
        self.complete_todo_proc = CompleteTodoProcedure()
        self.delete_todo_proc = DeleteTodoProcedure()

        # Command map: command type -> list of procedures
        self.command_map = {
            AddTodo: [self.add_todo_proc],
            CompleteTodo: [self.complete_todo_proc],
            DeleteTodo: [self.delete_todo_proc],
        }

        # Procedure map: procedure -> context
        # Note: contexts are created fresh for each command execution
        # with emitters that capture events to the event queue

    def emit_event(self, event) -> None:
        """Add event to queue."""
        self.event_queue.append(event)

    def emit_command(self, command) -> None:
        """Add command to queue."""
        self.command_queue.append(command)

    def create_add_todo_context(self) -> AddTodoContext:
        """Create context for AddTodo procedure."""
        return AddTodoContext(
            emit=AddTodoEmitters(todo_added=self.emit_event),
            query=AddTodoQueries(
                list_todos=ListTodosQuery(self.store).execute
            ),
        )

    def create_complete_todo_context(self) -> CompleteTodoContext:
        """Create context for CompleteTodo procedure."""
        return CompleteTodoContext(
            emit=CompleteTodoEmitters(todo_completed=self.emit_event),
            query=CompleteTodoQueries(
                get_todo=GetTodoQuery(self.store).execute
            ),
        )

    def create_delete_todo_context(self) -> DeleteTodoContext:
        """Create context for DeleteTodo procedure."""
        return DeleteTodoContext(
            emit=DeleteTodoEmitters(todo_deleted=self.emit_event),
            query=DeleteTodoQueries(
                get_todo=GetTodoQuery(self.store).execute
            ),
        )

    def get_context_for_procedure(self, procedure):
        """Get context for a given procedure instance."""
        if procedure is self.add_todo_proc:
            return self.create_add_todo_context()
        elif procedure is self.complete_todo_proc:
            return self.create_complete_todo_context()
        elif procedure is self.delete_todo_proc:
            return self.create_delete_todo_context()
        else:
            raise ValueError(f"Unknown procedure: {procedure}")

    async def process_queues(self) -> None:
        """
        Process command and event queues following the Dizzy pattern.

        From st_service.py:
        while command_queue:
            # Process all commands
            while command_queue:
                command = command_queue.pop(0)  # FIFO
                procedure(context, command)  # May emit events

            # Process all events (may emit more commands)
            while event_queue:
                event = event_queue.pop(0)  # FIFO
                policy(context, event)  # May emit commands
        """
        while self.command_queue:
            # Process all commands
            while self.command_queue:
                command = self.command_queue.pop(0)  # FIFO
                command_type = type(command)

                if command_type in self.command_map:
                    for procedure in self.command_map[command_type]:
                        context = self.get_context_for_procedure(procedure)
                        procedure(context=context, command=command)

            # Process all events
            while self.event_queue:
                event = self.event_queue.pop(0)  # FIFO

                # Update store based on events (event sourcing)
                self.apply_event_to_store(event)

                # Broadcast event to SSE subscribers
                await self.broadcast_event(event)

                # TODO: Process policies here if we have any
                # for policy in self.event_map.get(type(event), []):
                #     context = self.policy_map[policy]
                #     policy(context=context, event=event)

    def apply_event_to_store(self, event) -> None:
        """Apply event to update the in-memory store (event sourcing)."""
        if isinstance(event, TodoAdded):
            # Reconstruct Todo object from event data
            from todo.gen.models import Todo
            todo = Todo(
                id=event.todo_id,
                text=event.text,
                completed=False,
                created_at=event.created_at,
                completed_at=None
            )
            self.store.add(todo)
        elif isinstance(event, TodoCompleted):
            todo = self.store.get(event.todo_id)
            if todo:
                todo.completed = True
                todo.completed_at = event.completed_at
                self.store.update(todo)
        elif isinstance(event, TodoDeleted):
            self.store.delete(event.todo_id)

    async def broadcast_event(self, event) -> None:
        """Broadcast event to all SSE subscribers."""
        event_data = self.serialize_event(event)
        for queue in self.sse_subscribers:
            await queue.put(event_data)

    def serialize_event(self, event) -> dict:
        """Serialize event to JSON-compatible dict."""
        # Convert pydantic model to dict
        event_dict = event.model_dump(mode="json")
        event_dict["type"] = type(event).__name__
        return event_dict


# Global service instance
service = TodoService()


# Request models
class CommandRequest(BaseModel):
    """Generic command request wrapper."""
    type: str
    data: Dict[str, Any]


# Routes

@app.post("/command")
async def handle_command(request: CommandRequest):
    """
    Handle incoming commands from the browser.

    Command format:
    {
        "type": "AddTodo" | "CompleteTodo" | "DeleteTodo",
        "data": { ...command-specific fields }
    }
    """
    cmd_type = request.type
    cmd_data = request.data

    # Parse command based on type
    if cmd_type == "AddTodo":
        command = AddTodo(**cmd_data)
    elif cmd_type == "CompleteTodo":
        command = CompleteTodo(**cmd_data)
    elif cmd_type == "DeleteTodo":
        command = DeleteTodo(**cmd_data)
    else:
        return {"error": f"Unknown command type: {cmd_type}"}

    # Add command to queue and process
    service.emit_command(command)
    await service.process_queues()

    return {"status": "ok"}


@app.get("/events")
async def stream_events():
    """
    Server-Sent Events (SSE) endpoint for streaming events to browsers.

    Clients subscribe via:
    const evtSource = new EventSource("/events");
    evtSource.onmessage = (e) => {
        const event = JSON.parse(e.data);
        // Handle event...
    };
    """
    queue = asyncio.Queue()
    service.sse_subscribers.append(queue)

    async def event_generator():
        try:
            # Send initial connection message
            yield ": connected\n\n"

            while True:
                # Wait for next event with timeout for heartbeat
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15.0)
                    # Send as SSE format: "data: {json}\n\n"
                    yield f"data: {json.dumps(event)}\n\n"
                except asyncio.TimeoutError:
                    # Send heartbeat comment to keep connection alive
                    yield ": heartbeat\n\n"
        except (asyncio.CancelledError, GeneratorExit):
            pass
        except Exception as e:
            print(f"Error in SSE stream: {e}")
        finally:
            # Safely remove subscriber
            if queue in service.sse_subscribers:
                service.sse_subscribers.remove(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.get("/")
async def serve_index():
    """Serve the main HTML page."""
    return FileResponse("todo/web/static/index.html")


if __name__ == "__main__":
    import uvicorn
    import socket

    # Get the server's IP address
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    print("Starting Dizzy Todo Server...")
    print(f"Local access: http://localhost:8000")
    print(f"Network access: http://{local_ip}:8000")
    print("Press Ctrl+C to stop")
    uvicorn.run(app, host="0.0.0.0", port=8000)
