# New Project Guide: Building a Todo App with Dizzy

This guide documents the step-by-step process of creating a new Dizzy application from scratch, using the `app/todo` collaborative todo list as an example.

## Overview

The todo app demonstrates Dizzy's event-driven architecture with a real-time web interface. It's simpler than `app/dedupe` but showcases the full pattern:
- Commands flow in via HTTP POST
- Procedures execute and emit events
- Events stream back to browsers via Server-Sent Events (SSE)

## Step 1: Project Structure Setup

### 1.1 Create Directory Structure

```bash
mkdir -p app/todo/{def,gen,procedures,queries,mutations,policies,tests,web/static}
```

### 1.2 Create `__init__.py` Files

```bash
touch app/todo/{__init__.py,def/__init__.py,gen/__init__.py,procedures/__init__.py,queries/__init__.py,mutations/__init__.py,policies/__init__.py}
```

### 1.3 Create `pyproject.toml`

Location: `app/todo/pyproject.toml`

```toml
[project]
name = "todo"
version = "0.1.0"
description = "Simple collaborative todo list application using Dizzy framework"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "dizzy",
    "linkml>=1.9.4",
    "fastapi>=0.115.0",
    "uvicorn>=0.32.0",
]

[dependency-groups]
dev = [
    "pytest>=8.4.2",
]

[tool.pytest.ini_options]
pythonpath = "."
markers = [
    "manual: marks tests as manual-only (deselect with '-m \"not manual\"')"
]
addopts = "-m 'not manual'"
```

## Step 2: Define YAML Schemas

### 2.1 Models (`def/models.yaml`)

Define the core data structures:

```yaml
id: https://example.org/todo
name: todo-schema
title: Todo Data Model

classes:
  Todo:
    description: Represents a todo item
    attributes:
      id:
        identifier: true
        required: true
        range: string
      text:
        required: true
        range: string
      completed:
        required: true
        range: boolean
      created_at:
        required: true
        range: datetime
      completed_at:
        required: false
        range: datetime
```

### 2.2 Commands (`def/commands.yaml`)

Define user intents:

```yaml
classes:
  AddTodo:
    description: Command to add a new todo item
    is_a: Command
    attributes:
      text:
        required: true
        range: string

  CompleteTodo:
    description: Command to mark a todo item as completed
    is_a: Command
    attributes:
      todo_id:
        required: true
        range: string

  DeleteTodo:
    description: Command to delete a todo item
    is_a: Command
    attributes:
      todo_id:
        required: true
        range: string
```

### 2.3 Events (`def/events.yaml`)

Define immutable facts:

```yaml
classes:
  TodoAdded:
    description: Event recording that a todo item was added
    is_a: DomainEvent
    attributes:
      todo:
        required: true
        range: Todo

  TodoCompleted:
    description: Event recording that a todo item was completed
    is_a: DomainEvent
    attributes:
      todo_id:
        required: true
        range: string
      completed_at:
        required: true
        range: datetime

  TodoDeleted:
    description: Event recording that a todo item was deleted
    is_a: DomainEvent
    attributes:
      todo_id:
        required: true
        range: string
```

### 2.4 Queries (`def/queries.yaml`)

Define read operations:

```yaml
classes:
  ListTodosInput:
    description: Input for listing all todos
    is_a: QueryInput
    attributes:
      include_completed:
        required: false
        range: boolean

  ListTodosOutput:
    description: Output containing list of todos
    is_a: QueryOutput
    attributes:
      todos:
        required: true
        range: Todo
        multivalued: true

  GetTodoInput:
    description: Input for getting a specific todo by ID
    is_a: QueryInput
    attributes:
      todo_id:
        required: true
        range: string

  GetTodoOutput:
    description: Output containing a single todo
    is_a: QueryOutput
    attributes:
      todo:
        required: false
        range: Todo
```

### 2.5 Procedures (`def/procedures.d.yaml`)

Map commands to their dependencies:

```yaml
procedures:
  add_todo:
    command: AddTodo
    emitters:
      emit_todo_added: TodoAdded
    queries:
      list_todos: ListTodos

  complete_todo:
    command: CompleteTodo
    emitters:
      emit_todo_completed: TodoCompleted
    queries:
      get_todo: GetTodo

  delete_todo:
    command: DeleteTodo
    emitters:
      emit_todo_deleted: TodoDeleted
    queries:
      get_todo: GetTodo
```

### 2.6 Policies (`def/policies.d.yaml`)

For simple apps, may be empty:

```yaml
policies: {}
```

### 2.7 Mutations (`def/mutations.yaml`)

For simple apps, may be a placeholder:

```yaml
classes:
  # Placeholder for future mutations if needed
```

## Step 3: Generate Code

Run the Dizzy code generator using the `justfile`:

```bash
cd app/todo
just gen
```

This runs:
1. `gen-pydantic` on each YAML schema to create Pydantic models
2. `generate_query_interfaces` to create query protocol interfaces
3. `generate_procedure_contexts` to create procedure contexts and protocol interfaces

Output files in `gen/`:
- `models.py` - Pydantic models for Todo
- `commands.py` - AddTodo, CompleteTodo, DeleteTodo
- `events.py` - TodoAdded, TodoCompleted, TodoDeleted
- `queries.py` - ListTodos, GetTodo (with Input classes)
- `procedures.py` - Procedure contexts (AddTodoContext, etc.)

Output files in implementation folders:
- `queries/interfaces.py` - Query protocol interfaces
- `procedures/interfaces.py` - Procedure protocol interfaces

## Step 4: Implement Queries

Create `queries/todo_queries.py`:

```python
class TodoStore:
    """Shared in-memory storage for todos."""
    def __init__(self):
        self.todos: Dict[str, Todo] = {}

    def add(self, todo: Todo) -> None: ...
    def get(self, todo_id: str) -> Todo | None: ...
    def list_all(self, include_completed: bool = True) -> list[Todo]: ...
    def update(self, todo: Todo) -> None: ...
    def delete(self, todo_id: str) -> None: ...

class ListTodosQuery:
    def __init__(self, store: TodoStore): ...
    def execute(self, query_input: ListTodosInput) -> ListTodos: ...

class GetTodoQuery:
    def __init__(self, store: TodoStore): ...
    def execute(self, query_input: GetTodoInput) -> GetTodo: ...
```

## Step 5: Implement Procedures

Create procedure files in `procedures/`:

**add_todo.py**:
```python
class AddTodoProcedure:
    def __call__(self, context: AddTodoContext, command: AddTodo) -> None:
        todo = Todo(id=str(uuid.uuid4()), text=command.text, ...)
        context.emit.todo_added(TodoAdded(todo=todo))

# Type check
_: AddTodoProcedureProtocol = AddTodoProcedure()
```

**complete_todo.py**:
```python
class CompleteTodoProcedure:
    def __call__(self, context: CompleteTodoContext, command: CompleteTodo) -> None:
        query_result = context.query.get_todo(GetTodoInput(todo_id=command.todo_id))
        if query_result.todo and not query_result.todo.completed:
            context.emit.todo_completed(TodoCompleted(...))
```

**delete_todo.py**:
```python
class DeleteTodoProcedure:
    def __call__(self, context: DeleteTodoContext, command: DeleteTodo) -> None:
        query_result = context.query.get_todo(GetTodoInput(todo_id=command.todo_id))
        if query_result.todo:
            context.emit.todo_deleted(TodoDeleted(todo_id=command.todo_id))
```

## Step 6: Build Web Server with SSE

Create `web/server.py` with FastAPI:

### Key Components

**TodoService Class** (implements st_service.py pattern):
```python
class TodoService:
    def __init__(self):
        self.store = TodoStore()
        self.command_queue = []
        self.event_queue = []
        self.sse_subscribers = []  # asyncio.Queue per client

        # Command map: command type -> procedures
        self.command_map = {
            AddTodo: [self.add_todo_proc],
            CompleteTodo: [self.complete_todo_proc],
            DeleteTodo: [self.delete_todo_proc],
        }

    async def process_queues(self):
        """Process commands, then events (may emit more commands)"""
        while self.command_queue:
            while self.command_queue:
                command = self.command_queue.pop(0)
                procedure(context, command)  # May emit events

            while self.event_queue:
                event = self.event_queue.pop(0)
                self.apply_event_to_store(event)
                await self.broadcast_event(event)
```

**HTTP Endpoints**:
```python
@app.post("/command")
async def handle_command(request: CommandRequest):
    command = parse_command(request.type, request.data)
    service.emit_command(command)
    await service.process_queues()
    return {"status": "ok"}

@app.get("/events")
async def stream_events():
    queue = asyncio.Queue()
    service.sse_subscribers.append(queue)

    async def event_generator():
        try:
            while True:
                event = await queue.get()
                yield f"data: {json.dumps(event)}\n\n"
        finally:
            service.sse_subscribers.remove(queue)

    return StreamingResponse(event_generator(),
                            media_type="text/event-stream")
```

## Step 7: Create HTML/JS Frontend

Create `web/static/index.html`:

**SSE Connection**:
```javascript
const evtSource = new EventSource("/events");

evtSource.onmessage = (e) => {
    const event = JSON.parse(e.data);
    handleEvent(event);
};

function handleEvent(event) {
    if (event.type === "TodoAdded") {
        todos.set(event.todo.id, event.todo);
        renderTodos();
    } else if (event.type === "TodoCompleted") {
        const todo = todos.get(event.todo_id);
        todo.completed = true;
        renderTodos();
    } else if (event.type === "TodoDeleted") {
        todos.delete(event.todo_id);
        renderTodos();
    }
}
```

**Send Commands**:
```javascript
async function sendCommand(type, data) {
    await fetch("/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type, data })
    });
}

async function addTodo() {
    await sendCommand("AddTodo", { text: "..." });
}
```

## Step 8: Run the Server

```bash
cd app/todo
uv run python web/server.py
```

Open http://localhost:8000 in multiple browser tabs to see real-time synchronization!

## Directory Structure Reference

```
app/todo/
├── def/                      # YAML schema definitions (YOU EDIT THESE)
│   ├── commands.yaml         # User commands
│   ├── events.yaml           # Domain events
│   ├── queries.yaml          # Read operations
│   ├── models.yaml           # Data models
│   ├── procedures.d.yaml     # Procedure-to-command mappings
│   ├── mutations.yaml        # State mutations
│   └── policies.d.yaml       # Event-to-policy mappings
├── gen/                      # Generated code (DO NOT EDIT)
│   ├── commands.py
│   ├── events.py
│   ├── queries.py
│   ├── models.py
│   ├── procedures.py
│   └── mutations.py
├── procedures/               # Your procedure implementations
│   ├── add_todo.py
│   ├── complete_todo.py
│   └── delete_todo.py
├── queries/                  # Your query implementations
│   ├── list_todos.py
│   └── get_todo.py
├── web/                      # Web server
│   ├── server.py
│   └── static/
│       └── index.html
├── tests/
├── pyproject.toml
└── README.md
```

## Architecture Pattern

### Command Flow
```
Browser → HTTP POST /command → Procedure → Event → Event Queue
```

### Event Flow
```
Event Queue → SSE Stream → Browser → UI Update
```

### Service Loop (from st_service.py)
```python
while command_queue:
    # Process all commands
    while command_queue:
        command = command_queue.pop(0)
        procedure = command_map[type(command)]
        procedure(context, command)  # May emit events

    # Process all events (may emit more commands)
    while event_queue:
        event = event_queue.pop(0)
        policy = event_map[type(event)]
        policy(context, event)  # May emit commands
```

## Key Dizzy Patterns

1. **Commands are ephemeral** - They represent intent, not state
2. **Events are immutable** - They represent facts that happened
3. **Procedures are pure functions** - All dependencies injected via context
4. **Queries are read-only** - They return projections of current state
5. **Policies react to events** - They may trigger new commands

## Project Status

### Completed Steps

- [x] **Step 1-2**: Created project structure and YAML schemas
- [x] **Step 3**: Generated code from schemas using `just gen`
- [x] **Step 4**: Implemented queries with in-memory TodoStore
- [x] **Step 5**: Implemented three procedures (add, complete, delete)
- [x] **Step 6**: Built FastAPI web server with SSE support
- [x] **Step 7**: Created responsive HTML/JS frontend
- [x] **Step 8**: Ready to run!

### Testing the App

1. **Start the server**:
   ```bash
   cd app/todo
   uv run python web/server.py
   ```

2. **Open in browser**:
   - Navigate to http://localhost:8000
   - Try opening multiple tabs to see real-time synchronization!

3. **What to test**:
   - Add todos in one tab, see them appear in others
   - Mark todos complete, watch the UI update everywhere
   - Delete todos, see them disappear in real-time
   - Check the browser console for event logs

### How It Works

**Command Flow**:
```
User clicks "Add" → JavaScript sendCommand()
                  ↓
                HTTP POST /command
                  ↓
            service.emit_command(AddTodo)
                  ↓
            service.process_queues()
                  ↓
         AddTodoProcedure executes
                  ↓
    context.emit.todo_added(TodoAdded)
                  ↓
            Event added to event_queue
```

**Event Flow**:
```
Event in event_queue
        ↓
  apply_event_to_store() → Updates in-memory TodoStore
        ↓
  broadcast_event() → Push to all SSE subscribers
        ↓
Browser EventSource.onmessage → handleEvent()
        ↓
  Update local todos Map → renderTodos()
        ↓
  DOM updated with new state
```

### Architecture Highlights

1. **Pure Dizzy Pattern**: Follows `st_service.py` exactly
   - Commands processed FIFO from command_queue
   - Events processed FIFO from event_queue
   - Policies can react to events (though we have none in this simple example)

2. **Event Sourcing**: TodoStore is updated by applying events
   - TodoAdded → store.add(todo)
   - TodoCompleted → store.update(todo with completed=true)
   - TodoDeleted → store.delete(todo_id)

3. **Dependency Injection**: All procedure dependencies via context
   - Emitters are injected (capture events to queue)
   - Queries are injected (access to TodoStore)

4. **Type Safety**: Protocol interfaces ensure correctness
   - `_: AddTodoProcedureProtocol = AddTodoProcedure()` validates at module load
   - IDEs catch type mismatches during development

### Extending the App

Want to add features? Follow the pattern:

**Add a new command** (e.g., "RenameT odo"):
1. Add to `def/commands.yaml`
2. Add event to `def/events.yaml`
3. Add to `def/procedures.d.yaml`
4. Run `just gen`
5. Implement procedure in `procedures/rename_todo.py`
6. Add to service command_map in `web/server.py`
7. Add handler in frontend JavaScript

**Add a policy** (e.g., "Auto-archive completed todos"):
1. Add to `def/policies.d.yaml`
2. Run `just gen`
3. Implement in `policies/auto_archive.py`
4. Register in service event_map

### Comparison to Other Approaches

**Traditional REST API**:
```
Browser → GET /todos → Server → Response
Browser → POST /todos → Server → Response
Browser → Poll GET /todos every N seconds (inefficient!)
```

**Dizzy + SSE**:
```
Browser → POST /command → Server processes → Event emitted
Server → SSE push → All browsers instantly updated
```

Benefits:
- No polling needed
- True real-time updates
- Server is source of truth
- Multiple clients stay in sync
- Event log provides audit trail

---

## Troubleshooting

**ImportError: No module named 'dizzy'**
- Run from within `app/todo` directory
- Ensure `uv` is using the right Python environment
- Try: `uv sync` to install dependencies

**Server won't start**
- Check port 8000 isn't already in use
- Verify all Python files have correct imports
- Check for syntax errors in procedures

**Events not appearing in browser**
- Open browser DevTools → Network → Check EventSource connection
- Look for errors in console
- Verify server is broadcasting events (check server logs)

**Type errors when running procedures**
- Run `just gen` again to regenerate interfaces
- Check that procedure signatures match protocol
- Verify the type assertion line at end of each procedure file

---

*Implementation completed successfully! This guide now serves as a complete reference for building Dizzy applications.*
