# DIZZY Build Order

DIZZY follows a strict build pipeline from definitions through deployment. Understanding this order is critical for development.

## Overview: The Four Stages

```
1. Definitions (def/)     → LinkML schemas
2. Generated (gen/)       → Type-safe interfaces from definitions
3. Source (src/)          → Manual implementations
4. Deployment (result/)   → Packaged artifacts
```

## Stage 1: Definitions (`def/`)

**Input**: Feature YAML file (`{feature_name}.feat.yaml`)
**Output**: LinkML schema files in `def/commands/` and `def/events/`
**Command**: `dizzy gen init`

### 1.1 Create Feature Definition

Start with a feature YAML file describing your domain:

```yaml
# app/{domain}/{feature}.feat.yaml
description: "Feature description"

commands:
  start_scan: "Begin scanning a directory"
  calculate_hash: "Calculate content hash for a file"

events:
  scan_item_found: "A scannable item was discovered"
  scan_complete: "Scan finished successfully"
  hash_calculated: "Hash computation completed"

procedures:
  partition_scan:
    description: "Walk directory tree and emit items"
    command: start_scan
    emits: [scan_item_found, scan_complete]
    context: []

policies:
  hash_priority_files:
    description: "Queue hash commands for important files"
    event: scan_item_found
    emits: [calculate_hash]
    context: []

projections:
  ScanResult:
    description: "Aggregated scan statistics"
    attributes:
      total_items: "Number of items found"
      total_bytes: "Total size in bytes"

queries:
  get_scan_results:
    description: "Retrieve scan statistics"
    uses: [ScanResult]
    parameters:
      - scan_id: "Scan identifier"
    returns: "ScanResult object"
```

### 1.2 Generate LinkML Schemas

Run `dizzy gen init` to generate LinkML schema templates:

```bash
dizzy gen init --app-dir app/{domain} --feat-dir {feature} --feat-path {feature}.feat.yaml
```

This creates:
- `def/commands/{command_name}.yaml` for each command
- `def/events/{event_name}.yaml` for each event

Each schema file is a template with:
- Unique ID and namespace
- Import of base Command or Event type
- Placeholder attributes

### 1.3 Refine LinkML Schemas

**MANUAL STEP**: Edit generated schemas to add domain-specific fields.

Example: `def/commands/start_scan.yaml`

```yaml
id: https://example.org/dedupe/start_scan
name: dedupe-start_scan-command
imports:
  - linkml:types
  - ../../dizzy/def/commands
classes:
  StartScan:
    is_a: Command
    attributes:
      command_id:
        required: true
        identifier: true
      scan_path:           # ADD THIS
        range: string
        required: true
      recursive:           # ADD THIS
        range: boolean
        required: false
```

**Why LinkML?**: Schemas enable:
- Type validation
- Multiple language bindings (Python, TypeScript, Rust, etc.)
- Documentation generation
- Schema evolution tracking

## Stage 2: Generated Code (`gen/`)

**Input**: LinkML schemas from `def/`
**Output**: Type-safe Python interfaces
**Commands**: `dizzy gen init` (step 4), `dizzy gen src` (step 6)

### 2.1 Generate Pydantic Models

After defining LinkML schemas, `dizzy gen init` continues:

```bash
# Automatically runs after schema generation
linkml-gen-pydantic def/commands/*.yaml → gen/pyd/commands/
linkml-gen-pydantic def/events/*.yaml → gen/pyd/events/
```

Creates:
- `gen/pyd/commands/{command_name}.py` - Pydantic dataclasses for commands
- `gen/pyd/events/{event_name}.py` - Pydantic dataclasses for events

Example output:

```python
# gen/pyd/commands/start_scan.py
@dataclass
class StartScan(Command):
    command_id: str
    scan_path: str
    recursive: bool = False
```

### 2.2 Generate Procedure & Policy Protocols

Run `dizzy gen src` to generate context and protocol files:

```bash
dizzy gen src --app-dir app/{domain} --feat-dir {feature}
```

Creates for each procedure:
- `gen/pyd/procedure/{procedure_name}_context.py` - Context with emitters and queries
- `gen/pyd/procedure/{procedure_name}_protocol.py` - Protocol interface

Creates for each policy:
- `gen/pyd/policy/{policy_name}_context.py` - Context with emitters
- `gen/pyd/policy/{policy_name}_protocol.py` - Protocol interface

Example context:

```python
# gen/pyd/procedure/partition_scan_context.py
@dataclass
class start_scan_emitters:
    scan_item_found: Callable[[ScanItemFound], None]
    scan_complete: Callable[[ScanComplete], None]

@dataclass
class start_scan_queries:
    pass  # Queries added here if defined in feat.yaml

@dataclass
class start_scan_context:
    emit: start_scan_emitters
    query: start_scan_queries
```

Example protocol:

```python
# gen/pyd/procedure/partition_scan_protocol.py
class start_scan_procedure_protocol(Protocol):
    def __call__(self, context: start_scan_context, command: StartScan) -> None:
        """Execute the start_scan procedure."""
        ...
```

**Key Point**: Generated code is **never manually edited**. It's regenerated when schemas or feat.yaml change.

## Stage 3: Source Code (`src/`)

**Input**: Generated protocols from `gen/`
**Output**: Manual implementations
**Command**: `dizzy gen src` (step 7) or manual development

### 3.1 Implement Procedures

Create implementations matching generated protocols:

```python
# src/procedure/cc_py/partition_scan.py
from gen.pyd.commands.start_scan import StartScan
from gen.pyd.procedure.partition_scan_context import start_scan_context
from gen.pyd.events.scan_item_found import ScanItemFound
from gen.pyd.events.scan_complete import ScanComplete
import os

def partition_scan(context: start_scan_context, command: StartScan) -> None:
    """Walk directory and emit events for each item found."""
    items_found = 0

    for root, dirs, files in os.walk(command.scan_path):
        for file in files:
            file_path = os.path.join(root, file)
            stat = os.stat(file_path)

            context.emit.scan_item_found(ScanItemFound(
                event_id=str(uuid.uuid4()),
                file_path=file_path,
                size_bytes=stat.st_size,
                timestamp=datetime.now().isoformat()
            ))
            items_found += 1

    context.emit.scan_complete(ScanComplete(
        event_id=str(uuid.uuid4()),
        total_items=items_found
    ))
```

### 3.2 Implement Policies

```python
# src/policy/cc_py/hash_priority_files.py
from gen.pyd.events.scan_item_found import ScanItemFound
from gen.pyd.policy.hash_priority_files_context import hash_priority_context
from gen.pyd.commands.calculate_hash import CalculateHash
import uuid

PRIORITY_EXTENSIONS = {'.pdf', '.docx', '.xlsx', '.zip'}

def hash_priority_files(context: hash_priority_context, event: ScanItemFound) -> None:
    """Emit hash command for priority file types only."""
    file_ext = os.path.splitext(event.file_path)[1].lower()

    if file_ext in PRIORITY_EXTENSIONS:
        context.emit.calculate_hash(CalculateHash(
            command_id=str(uuid.uuid4()),
            file_path=event.file_path
        ))
```

### 3.3 Implementation Directory Structure

```
src/
├── procedure/
│   ├── cc_py/              # Claude Code Python implementations
│   │   ├── partition_scan.py
│   │   └── calculate_cas_hash.py
│   ├── rust/               # (Future) Rust implementations
│   └── go/                 # (Future) Go implementations
└── policy/
    ├── cc_py/
    │   └── hash_priority_files.py
    └── sql/                # (Future) SQL-based policies
```

Different implementation types (`cc_py`, `rust`, etc.) allow:
- Language choice per component
- Performance optimization of critical paths
- Gradual migration between languages

## Stage 4: Testing (`src/`)

**Before deployment**: Validate implementations

### 4.1 Unit Tests

Test procedures and policies in isolation:

```python
# src/procedure/cc_py/test_partition_scan.py
from unittest.mock import Mock
from src.procedure.cc_py.partition_scan import partition_scan
from gen.pyd.commands.start_scan import StartScan
from gen.pyd.procedure.partition_scan_context import (
    start_scan_context, start_scan_emitters, start_scan_queries
)

def test_partition_scan_emits_events():
    # Arrange
    mock_emit_found = Mock()
    mock_emit_complete = Mock()

    context = start_scan_context(
        emit=start_scan_emitters(
            scan_item_found=mock_emit_found,
            scan_complete=mock_emit_complete
        ),
        query=start_scan_queries()
    )

    command = StartScan(
        command_id="test-123",
        scan_path="/tmp/test",
        recursive=True
    )

    # Act
    partition_scan(context, command)

    # Assert
    assert mock_emit_found.call_count > 0
    assert mock_emit_complete.call_count == 1
```

### 4.2 Integration Tests

Test event flow through procedures and policies:

```python
def test_scan_to_hash_workflow():
    event_store = []
    command_queue = []

    # Set up procedure context
    procedure_context = start_scan_context(
        emit=start_scan_emitters(
            scan_item_found=lambda e: event_store.append(e),
            scan_complete=lambda e: event_store.append(e)
        ),
        query=start_scan_queries()
    )

    # Run procedure
    partition_scan(procedure_context, StartScan(...))

    # Set up policy context
    policy_context = hash_priority_context(
        emit=hash_priority_emitters(
            calculate_hash=lambda c: command_queue.append(c)
        )
    )

    # Run policy on emitted events
    for event in event_store:
        if isinstance(event, ScanItemFound):
            hash_priority_files(policy_context, event)

    # Assert workflow
    assert len(event_store) > 0
    assert len(command_queue) > 0  # Priority files queued
```

### 4.3 Property-Based Tests

Use hypothesis for property testing:

```python
from hypothesis import given, strategies as st

@given(st.text(), st.booleans())
def test_start_scan_always_emits_complete(scan_path, recursive):
    # Properties that must hold for all inputs
    ...
```

## Stage 5: Deployment (`result/`)

**Input**: Tested implementations from `src/`
**Output**: Deployable artifacts
**Process**: Package implementations with deployment-specific wiring

### 5.1 Deployment Manifest

Create `impl.yaml` mapping components to implementations:

```yaml
# impl.yaml
domain: dedupe
feature: scan_and_upload

procedures:
  partition_scan:
    command: start_scan
    implementation: src/procedure/cc_py/partition_scan.py
    function: partition_scan

policies:
  hash_priority_files:
    event: scan_item_found
    implementation: src/policy/cc_py/hash_priority_files.py
    function: hash_priority_files
```

### 5.2 Deployment Types

Different deployment targets wire components differently:

#### Lambda / Serverless
```python
# result/lambda/handler.py
from gen.pyd.commands.start_scan import StartScan
from src.procedure.cc_py.partition_scan import partition_scan

# Wire emitters to SQS
def lambda_handler(event, context):
    sqs = boto3.client('sqs')

    procedure_context = start_scan_context(
        emit=start_scan_emitters(
            scan_item_found=lambda e: sqs.send_message(
                QueueUrl=os.environ['EVENT_QUEUE'],
                MessageBody=e.json()
            ),
            scan_complete=lambda e: sqs.send_message(...)
        ),
        query=start_scan_queries()
    )

    command = StartScan(**json.loads(event['body']))
    partition_scan(procedure_context, command)
```

#### Streamlit UI
```python
# result/st_service/app.py
import streamlit as st

# Wire emitters to local event store
def run_scan():
    events = []

    context = start_scan_context(
        emit=start_scan_emitters(
            scan_item_found=lambda e: events.append(e),
            scan_complete=lambda e: events.append(e)
        ),
        query=start_scan_queries()
    )

    command = StartScan(scan_path=st.text_input("Path"))
    partition_scan(context, command)

    st.write(f"Found {len(events)} items")
```

#### Message Queue Service
```python
# result/mq_service/worker.py
# Wire emitters to RabbitMQ, Redis, Kafka, etc.
```

### 5.3 Deployment Directory Structure

```
result/
├── lambda/           # AWS Lambda deployment
│   ├── handler.py
│   └── requirements.txt
├── st_service/       # Streamlit UI
│   ├── app.py
│   └── requirements.txt
└── docker/           # Containerized service
    ├── Dockerfile
    └── entrypoint.py
```

## Component Build Order

Within each stage, build in this order:

### Order 1: Foundation (Models & Events)

Build these first (no dependencies):

1. **Models** (projections in feat.yaml)
   - Define database schema
   - No dependencies

2. **Events** (events in feat.yaml)
   - Define what happened
   - No dependencies

### Order 2: Read Path (Projections & Queries)

Build these second (depend on Models & Events):

3. **Projections**
   - Depend on: Events, Models
   - Map events to model updates

4. **Queries**
   - Depend on: Models
   - Read from models

### Order 3: Write Path (Commands)

Build these third:

5. **Commands** (commands in feat.yaml)
   - Define what should happen
   - No dependencies (but referenced by procedures)

### Order 4: Processing (Procedures & Policies)

Build these last (depend on everything):

6. **Procedures**
   - Depend on: Commands (input), Events (output), Queries (context)
   - Do work and emit events

7. **Policies**
   - Depend on: Events (input), Commands (output), Queries (context)
   - React to events and emit commands

## Regeneration Rules

### When to Regenerate

**Regenerate `gen/`** when:
- LinkML schemas in `def/` change
- `feat.yaml` changes (commands, events, procedures, policies)

**Do NOT regenerate `gen/`** when:
- Only implementation in `src/` changes
- Only deployment configuration changes

### Safe Regeneration

```bash
# Regenerate everything (safe - won't touch src/)
dizzy gen init --fresh  # Regenerates def/ and gen/
dizzy gen src          # Regenerates gen/ protocols
```

Generated files in `gen/` are disposable. Source files in `src/` are precious.

## Summary: Build Pipeline Checklist

- [ ] 1. Write `{feature}.feat.yaml` defining domain
- [ ] 2. Run `dizzy gen init` to generate LinkML schemas
- [ ] 3. Edit LinkML schemas in `def/` to add domain fields
- [ ] 4. Run `dizzy gen init` again to generate Pydantic models
- [ ] 5. Run `dizzy gen src` to generate protocols
- [ ] 6. Implement procedures in `src/procedure/{type}/`
- [ ] 7. Implement policies in `src/policy/{type}/`
- [ ] 8. Write unit tests for implementations
- [ ] 9. Write integration tests for workflows
- [ ] 10. Create `impl.yaml` deployment manifest
- [ ] 11. Wire implementations in `result/{deployment_type}/`
- [ ] 12. Package and deploy

**Key Principle**: Flow from abstract (definitions) to concrete (implementations) to configured (deployments).
