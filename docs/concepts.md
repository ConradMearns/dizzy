# DIZZY Core Concepts

DIZZY implements Command Query Responsibility Separation (CQRS) with Event Sourcing in a language-agnostic, infrastructure-decoupled manner.

## Data Components

### Commands ($c$)

**Commands** are imperative intents that describe what should happen.

- **Imperative**: Express intention ("StartScan", "CalculateHash")
- **Ephemeral**: Not stored long-term, processed and discarded
- **Input to Procedures**: Each command triggers exactly one procedure
- **Structure**: Defined in LinkML schemas at `def/commands/{command_name}.yaml`

Example: `StartScan(scan_path="/data", recursive=True)`

### Events ($e$)

**Events** are immutable facts about what has happened in the system.

- **Immutable**: Once created, never modified
- **Durable**: Stored permanently in the event store
- **Past Tense**: Named for completed actions ("ScanItemFound", "HashCalculated")
- **Source of Truth**: Events are the only required persistent data
- **Structure**: Defined in LinkML schemas at `def/events/{event_name}.yaml`

Example: `ScanItemFound(item_path="/data/file.txt", size_bytes=1024, timestamp="2026-01-31T12:00:00Z")`

Key principle: **Events are all you need** for complete system state reconstruction via Event Sourcing.

### Models ($m$)

**Models** are database representations that optimize queries.

- **Optimization**: "The database is an optimization" - models make queries faster
- **Derived State**: Can always be rebuilt from events via projections
- **Multiple Representations**: Same events can populate multiple model types (SQL, NoSQL, graph, etc.)
- **Structure**: Defined in `feat.yaml` under `projections:`

Example:
```yaml
projections:
  ScanResult:
    description: "Aggregated scan statistics"
    attributes:
      total_items: "Total number of items found"
      total_bytes: "Total size in bytes"
      scan_duration: "Time taken to complete scan"
```

### Queries ($Q$)

**Queries** are request-response interfaces to read from models.

- **Bidirectional**: Request ($q_i$) → Process ($q_p$) → Response ($q_o$)
- **Read-Only**: Queries never modify state
- **Model-Backed**: Query implementations read from models (databases)
- **Typed Interface**: Parameters and return types defined in `feat.yaml`
- **Structure**: Defined in `feat.yaml` under `queries:`

Example:
```yaml
queries:
  get_scan_results:
    description: "Retrieve aggregated scan results"
    uses: [ScanResult]
    parameters:
      - scan_id: "Unique identifier for the scan"
    returns: "ScanResult object with statistics"
```

Queries enable fast lookups without replaying entire event history.

## Process Components

All processes in DIZZY follow a key principle: **No return statements**. Instead, processes use dependency injection to acquire callback functions (emitters) defined at deployment time.

### Context

The execution context provides processes with:
- **Emitters**: Callbacks to emit events or commands (defined at deployment)
- **Queries**: Interfaces to query the current world model

```python
@dataclass
class Context:
    emit: BazCrunchedEmitter  # Callable[[BazCrunched], None]
    query: BazQueriers        # Query interfaces

def process(input: Input, context: Context):
    result = compute_something(input, context.query.search("term"))
    context.emit(BazCrunched(result))  # Fire-and-forget
```

**Fire-and-forget philosophy**: Don't wait to inform other components. Emit events immediately and let the system react.

### Procedures ($d$)

**Procedures** perform meaningful work and emit events.

- **Command Handler**: Each procedure handles exactly one command type
- **Read/Write**: Can query models and produce side effects
- **Event Emission**: Emits zero or more events describing work completed
- **Effectful**: May interact with external systems (file I/O, API calls, calculations)
- **Structure**:
  - Protocol: `gen/pyd/procedure/{command_name}_protocol.py`
  - Context: `gen/pyd/procedure/{command_name}_context.py`
  - Implementation: `src/procedure/{impl_type}/{procedure_name}.py`

```python
def partition_scan(context: start_scan_context, command: StartScan) -> None:
    """Scan directory and emit events for each item found."""
    for item in os.walk(command.scan_path):
        context.emit.scan_item_found(ScanItemFound(path=item, ...))
    context.emit.scan_complete(ScanComplete(total_items=count))
```

### Policies ($y$)

**Policies** encode workflow logic and business rules.

- **Event Handler**: Each policy reacts to one event type
- **Read-Only**: Can only query models, cannot perform side effects
- **Command Emission**: Emits zero or more commands based on business logic
- **Reactive**: Implements "when this happens, then do that" logic
- **Structure**:
  - Protocol: `gen/pyd/policy/{event_name}_protocol.py`
  - Context: `gen/pyd/policy/{policy_name}_context.py`
  - Implementation: `src/policy/{impl_type}/{policy_name}.py`

```python
def hash_priority_files(context: hash_policy_context, event: ScanItemFound) -> None:
    """Emit hash command only for priority file types."""
    if event.file_path.endswith(('.pdf', '.docx')):
        context.emit.calculate_hash(CalculateHash(file_path=event.file_path))
```

**Key distinction**: Procedures do work, Policies decide what work should be done next.

### Projections ($j$)

**Projections** map events to model updates.

- **Event → Model Mapping**: Transform events into database operations
- **Idempotent**: Can safely process same event multiple times
- **Model Builder**: Updates read models based on event content
- **Many-to-Many**: Multiple events can update one model; one event can update multiple models
- **Rebuild Capability**: Since projections are deterministic, models can be rebuilt by replaying events

```
Event Stream: [e₁, e₂, e₃, e₄, e₅, e₆]
                ↓  ↓  ↓  ↓  ↓  ↓
           Projections (j)
                ↓  ↓  ↓
Models:     [m₁, m₂, m₃]
```

Example: `ScanItemFound` event might update:
- `ScanResult` model (increment total_items counter)
- `FileInventory` model (add new file record)
- `Analytics` model (track file type distribution)

## Information Flow

### Event Loop (Command → Event)

```
Command (c) → Procedure (d) → Event (e) → Policy (y) → Command (c') → ...
```

1. Command arrives requesting work
2. Procedure performs work and emits events
3. Events trigger policies
4. Policies emit new commands
5. Cycle continues

### Model Loop (Event → Query)

```
Event (e) → Projection (j) → Model (m) → Query (Q) → Response
```

1. Event describes what happened
2. Projection updates model(s)
3. Model provides optimized queryable state
4. Query retrieves information for procedures/policies

## CQRS Separation

**Write Side** (Commands → Procedures → Events):
- Commands express intent
- Procedures perform work
- Events record facts
- All writes go through event store

**Read Side** (Events → Projections → Models → Queries):
- Events update projections
- Projections maintain models
- Queries read from models
- Optimized for specific read patterns

**Benefit**: Write and read concerns are completely decoupled. Can optimize, scale, and even use different databases for different queries.

## Event Sourcing

Traditional systems store current state. DIZZY stores the sequence of events that led to that state.

**Advantages**:
- **Complete Audit Trail**: Every change is recorded with full context
- **Time Travel**: Reconstruct state at any point in history
- **Debugging**: Replay events to reproduce issues
- **Model Evolution**: Add new projections to existing event streams
- **Multiple Models**: Same events can populate different database types

**Principle**: "The database is an optimization." Models are just cached views of event history, optimized for specific query patterns. If a model is corrupted or schema changes, rebuild it by replaying events through projections.

## Why This Architecture?

### Support (Almost) Any Programming Language

- Components communicate via serialized data (commands, events)
- No shared memory or library dependencies
- Procedures can be written in different languages
- Each component is independently deployable

### Deferring Decisions

- Don't choose database upfront - use events
- Add projections for new models later
- Switch serialization formats without changing logic
- Change infrastructure without touching business logic

### Architecting for Reversibility

- Made wrong database choice? Add new projection, deprecate old model
- Need to split monolith? Components already decoupled
- Performance issue? Replace individual procedure in different language
- Schema evolution? Events are immutable, models can evolve

**Philosophy**: "Everything in computing changes, it's just a matter of _when_."

DIZZY embraces change rather than fighting it.
