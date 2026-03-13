# DIZZY Code Generation Pipeline

This document provides a detailed technical reference for how DIZZY's code generation system works, from feature definitions through to deployable implementations.

## Overview

DIZZY uses a two-command generation flow:

1. **`dizzy gen init`** - Generates LinkML schemas and Pydantic models from feature definitions
2. **`dizzy gen src`** - Generates procedure/policy protocols and scaffolds implementations

Both commands read from `{feature}.feat.yaml` as the single source of truth.

## Command Reference

### dizzy gen init

**Purpose**: Bootstrap project structure and generate type-safe models.

**Usage**:
```bash
dizzy gen init [--app-dir DIR] [--feat-dir NAME] [--feat-path FILE] [--fresh]
```

**Options**:
- `--app-dir DIR` - Application directory (default: `app/dedupe`)
- `--feat-dir NAME` - Feature directory name (default: `scan_and_upload`)
- `--feat-path FILE` - Feature YAML file (default: `scan_and_upload.feat.yaml`)
- `--fresh` - Overwrite existing schemas (default: preserve existing)

**Execution Steps**:

1. **Step 1**: (Skipped) - Reserved for future feature model generation
2. **Step 2**: Generate LinkML schemas from feature YAML
   - Creates `def/commands/{command_name}.yaml` for each command
   - Creates `def/events/{event_name}.yaml` for each event
   - Schemas include metadata, imports, and placeholder attributes
3. **Step 3**: Setup `gen/` directory structure
   - Creates directory hierarchy for generated code
   - Initializes `__init__.py` files
4. **Step 4**: Generate Pydantic models from LinkML schemas
   - Runs `linkml-gen-pydantic` on all schemas in `def/`
   - Outputs to `gen/pyd/commands/` and `gen/pyd/events/`
5. **Step 4b**: Populate `__init__.py` files with imports
   - Auto-generates imports for all generated models

**Location**: `/dizzy/src/dizzy/commands/gen_init.py`

### dizzy gen src

**Purpose**: Generate procedure/policy protocols and scaffold implementations.

**Usage**:
```bash
dizzy gen src [--app-dir DIR] [--feat-dir NAME] [--feat-path FILE]
```

**Execution Steps**:

1. **Step 6**: Generate procedure and policy contexts/protocols
   - Creates `gen/pyd/procedure/{procedure_name}_context.py`
   - Creates `gen/pyd/procedure/{procedure_name}_protocol.py`
   - Creates `gen/pyd/policy/{policy_name}_context.py`
   - Creates `gen/pyd/policy/{policy_name}_protocol.py`
2. **Step 6b**: Populate protocol `__init__.py` files
3. **Step 7**: Generate implementation scaffolds using Claude Code CLI
   - Creates `src/procedure/cc_py/{procedure_name}.py`
   - Creates `src/policy/cc_py/{policy_name}.py`
   - Builds `impl.yaml` manifest

**Location**: `/dizzy/src/dizzy/commands/gen_src.py`

## Feature YAML Structure

The `{feature}.feat.yaml` file is the single source of truth for the entire system.

### Complete Example

```yaml
description: "Scan directories and calculate content hashes"

commands:
  start_scan: "Begin scanning a directory"
  calculate_cas_hash: "Calculate content-addressed hash for a file"

events:
  scan_item_found: "A scannable item was discovered"
  scan_complete: "Directory scan finished"
  scan_item_failed: "Failed to scan an item"
  cas_hash_calculated: "Content hash computed successfully"
  cas_hash_telemetry: "Hash calculation performance metrics"

procedures:
  partition_scan:
    description: "Walk directory tree and emit item events"
    command: start_scan
    emits: [scan_item_found, scan_complete, scan_item_failed]
    context:
      - get_previous_scan_results

  calculate_cas_hash:
    description: "Compute content-addressed hash"
    command: calculate_cas_hash
    emits: [cas_hash_calculated, cas_hash_telemetry]
    context: []

policies:
  hash_only_priority_files:
    description: "Queue hash commands only for priority file types"
    event: scan_item_found
    emits: [calculate_cas_hash]
    context:
      - get_file_priority_config

projections:
  ScanResult:
    description: "Aggregated scan statistics by scan_id"
    attributes:
      scan_id: "Unique scan identifier"
      total_items: "Number of items found"
      total_bytes: "Total size in bytes"
      start_time: "Scan start timestamp"
      end_time: "Scan completion timestamp"

  FileRecord:
    description: "Individual file metadata"
    attributes:
      file_path: "Absolute path to file"
      size_bytes: "File size"
      last_modified: "Last modification timestamp"
      content_hash: "CAS hash if calculated"

queries:
  get_scan_results:
    description: "Retrieve aggregated scan statistics"
    uses: [ScanResult]
    parameters:
      - scan_id: "Scan identifier"
    returns: "ScanResult object or None"

  get_previous_scan_results:
    description: "Get results from previous scans"
    uses: [ScanResult]
    parameters:
      - limit: "Maximum number of results"
    returns: "List of ScanResult objects"

  get_file_priority_config:
    description: "Retrieve file priority configuration"
    uses: [FileRecord]
    parameters: []
    returns: "Configuration object with priority file extensions"
```

### Section Breakdown

#### Commands Section
```yaml
commands:
  command_name: "Description of the command's intent"
```

- Keys become command class names (e.g., `StartScan`, `CalculateHash`)
- Values are human-readable descriptions
- Each command triggers exactly one procedure

#### Events Section
```yaml
events:
  event_name: "Description of what happened"
```

- Keys become event class names (e.g., `ScanItemFound`, `ScanComplete`)
- Values describe the fact that was recorded
- Past tense naming convention

#### Procedures Section
```yaml
procedures:
  procedure_name:
    description: "What work this procedure performs"
    command: command_name           # Which command triggers this
    emits: [event1, event2]         # Which events can be emitted
    context:                         # Which queries are available
      - query_name1
      - query_name2
```

- `procedure_name` becomes the implementation function name
- `command` links to a command from the commands section
- `emits` lists events this procedure can emit (must exist in events section)
- `context` lists queries available to the procedure

#### Policies Section
```yaml
policies:
  policy_name:
    description: "Business logic this policy implements"
    event: event_name               # Which event triggers this policy
    emits: [command1, command2]     # Which commands can be emitted
    context:                         # Which queries are available
      - query_name
```

- `policy_name` becomes the implementation function name
- `event` links to a single triggering event
- `emits` lists commands this policy can emit
- `context` lists queries available to the policy

#### Projections Section
```yaml
projections:
  EntityName:
    description: "What this model represents"
    attributes:
      field_name: "Field description"
```

- `EntityName` becomes the model/table name
- `attributes` define fields in the model
- Used by queries to read data

#### Queries Section
```yaml
queries:
  query_name:
    description: "What information this query retrieves"
    uses: [Projection1, Projection2]  # Which models are queried
    parameters:
      - param_name: "Parameter description"
    returns: "Description of return value"
```

- `query_name` becomes the query interface name
- `uses` lists projections this query reads from
- `parameters` define query inputs
- `returns` describes output structure

## Generated File Structure

### Complete Directory Hierarchy

```
app/{domain}/{feature}/
├── def/                                    # LinkML schema definitions
│   ├── commands/
│   │   ├── start_scan.yaml
│   │   └── calculate_cas_hash.yaml
│   └── events/
│       ├── scan_item_found.yaml
│       ├── scan_complete.yaml
│       ├── scan_item_failed.yaml
│       ├── cas_hash_calculated.yaml
│       └── cas_hash_telemetry.yaml
│
├── gen/                                    # Generated code (DO NOT EDIT)
│   ├── __init__.py
│   └── pyd/                                # Pydantic models
│       ├── commands/
│       │   ├── __init__.py
│       │   ├── start_scan.py
│       │   └── calculate_cas_hash.py
│       ├── events/
│       │   ├── __init__.py
│       │   ├── scan_item_found.py
│       │   ├── scan_complete.py
│       │   ├── scan_item_failed.py
│       │   ├── cas_hash_calculated.py
│       │   └── cas_hash_telemetry.py
│       ├── procedure/
│       │   ├── __init__.py
│       │   ├── partition_scan_context.py
│       │   ├── partition_scan_protocol.py
│       │   ├── calculate_cas_hash_context.py
│       │   └── calculate_cas_hash_protocol.py
│       └── policy/
│           ├── __init__.py
│           ├── hash_only_priority_files_context.py
│           └── hash_only_priority_files_protocol.py
│
├── src/                                    # Manual implementations (EDIT HERE)
│   ├── procedure/
│   │   └── cc_py/                          # Claude Code Python
│   │       ├── partition_scan.py
│   │       └── calculate_cas_hash.py
│   └── policy/
│       └── cc_py/
│           └── hash_only_priority_files.py
│
├── result/                                 # Deployment artifacts
│   └── st_service/                         # Streamlit deployment
│       ├── app.py
│       └── requirements.txt
│
├── {feature}.feat.yaml                     # Source of truth
└── impl.yaml                               # Implementation manifest
```

## Generated File Details

### LinkML Schema Files

**Location**: `def/commands/{command_name}.yaml` and `def/events/{event_name}.yaml`

**Purpose**: Define data structures in a language-agnostic way

**Example**: `def/commands/start_scan.yaml`
```yaml
id: https://example.org/dedupe/start_scan
name: dedupe-start_scan-command
title: Start Scan Command
description: "Begin scanning a directory"

prefixes:
  linkml: https://w3id.org/linkml/
  dedupe: https://example.org/dedupe/

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
        range: string
      scan_path:
        range: string
        required: true
        description: "Directory path to scan"
      recursive:
        range: boolean
        required: false
        description: "Scan subdirectories recursively"
```

**Generated by**: `linkml_generator.py`

**Manual editing required**: Yes - add domain-specific attributes after initial generation

### Pydantic Model Files

**Location**: `gen/pyd/commands/{command_name}.py` and `gen/pyd/events/{event_name}.py`

**Purpose**: Type-safe Python dataclasses with validation

**Example**: `gen/pyd/commands/start_scan.py`
```python
from __future__ import annotations
from dataclasses import dataclass
from linkml_runtime.linkml_model import Decimal
from typing import Optional
from gen.pyd.base.commands import Command

@dataclass
class StartScan(Command):
    """Begin scanning a directory."""
    command_id: str
    scan_path: str
    recursive: Optional[bool] = False

    def __post_init__(self):
        super().__post_init__()
        # LinkML validation logic
```

**Generated by**: LinkML's `gen-python` tool (called by `subprocess_utils.py`)

**Manual editing**: No - regenerate when schemas change

### Procedure Context Files

**Location**: `gen/pyd/procedure/{procedure_name}_context.py`

**Purpose**: Define emitters and queries available to procedure

**Example**: `gen/pyd/procedure/partition_scan_context.py`
```python
from dataclasses import dataclass
from typing import Callable
from gen.pyd.events.scan_item_found import ScanItemFound
from gen.pyd.events.scan_complete import ScanComplete
from gen.pyd.events.scan_item_failed import ScanItemFailed

@dataclass
class start_scan_emitters:
    """Emitters for start_scan procedure (partition_scan)."""
    scan_item_found: Callable[[ScanItemFound], None]
    scan_complete: Callable[[ScanComplete], None]
    scan_item_failed: Callable[[ScanItemFailed], None]

@dataclass
class start_scan_queries:
    """Queries for start_scan procedure (partition_scan)."""
    get_previous_scan_results: Callable[[int], list]  # Example query

@dataclass
class start_scan_context:
    """Context for start_scan procedure (partition_scan)."""
    emit: start_scan_emitters
    query: start_scan_queries
```

**Generated by**: `protocols_generator.py`

**Manual editing**: No - regenerate when feat.yaml changes

### Procedure Protocol Files

**Location**: `gen/pyd/procedure/{procedure_name}_protocol.py`

**Purpose**: Define type-safe interface for implementations

**Example**: `gen/pyd/procedure/partition_scan_protocol.py`
```python
from typing import Protocol
from gen.pyd.commands.start_scan import StartScan
from gen.pyd.procedure.partition_scan_context import start_scan_context

class start_scan_procedure_protocol(Protocol):
    """Protocol for start_scan procedure implementations (partition_scan)."""

    def __call__(self, context: start_scan_context, command: StartScan) -> None:
        """
        Execute the start_scan procedure.

        Walk directory tree and emit item events for each file/directory found.

        Args:
            context: Execution context with emitters and queries
            command: StartScan command with scan parameters

        Returns:
            None - results are communicated via context.emit calls
        """
        ...
```

**Generated by**: `protocols_generator.py`

**Manual editing**: No

### Policy Context and Protocol Files

Similar structure to procedures, but for policies:

**Example**: `gen/pyd/policy/hash_only_priority_files_context.py`
```python
@dataclass
class hash_only_priority_files_emitters:
    """Emitters for hash_only_priority_files policy."""
    calculate_cas_hash: Callable[[CalculateCasHash], None]

@dataclass
class hash_only_priority_files_queries:
    """Queries for hash_only_priority_files policy."""
    get_file_priority_config: Callable[[], dict]

@dataclass
class hash_only_priority_files_context:
    """Context for hash_only_priority_files policy."""
    emit: hash_only_priority_files_emitters
    query: hash_only_priority_files_queries
```

### Implementation Files

**Location**: `src/procedure/cc_py/{procedure_name}.py` and `src/policy/cc_py/{policy_name}.py`

**Purpose**: Actual business logic implementations

**Example**: `src/procedure/cc_py/partition_scan.py`
```python
import os
import uuid
from datetime import datetime
from gen.pyd.commands.start_scan import StartScan
from gen.pyd.procedure.partition_scan_context import start_scan_context
from gen.pyd.events.scan_item_found import ScanItemFound
from gen.pyd.events.scan_complete import ScanComplete
from gen.pyd.events.scan_item_failed import ScanItemFailed

def partition_scan(context: start_scan_context, command: StartScan) -> None:
    """Walk directory tree and emit events for each item found."""
    items_found = 0
    items_failed = 0

    try:
        for root, dirs, files in os.walk(command.scan_path):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    stat = os.stat(file_path)

                    context.emit.scan_item_found(ScanItemFound(
                        event_id=str(uuid.uuid4()),
                        file_path=file_path,
                        size_bytes=stat.st_size,
                        timestamp=datetime.now().isoformat()
                    ))
                    items_found += 1

                except Exception as e:
                    context.emit.scan_item_failed(ScanItemFailed(
                        event_id=str(uuid.uuid4()),
                        file_path=file_path,
                        error=str(e)
                    ))
                    items_failed += 1

    finally:
        context.emit.scan_complete(ScanComplete(
            event_id=str(uuid.uuid4()),
            total_items=items_found,
            total_failed=items_failed
        ))
```

**Generated by**: `implementation_generator.py` (via Claude Code CLI) or manual development

**Manual editing**: Yes - this is where you write actual logic

### Implementation Manifest

**Location**: `impl.yaml`

**Purpose**: Map procedures/policies to their implementations

**Example**:
```yaml
domain: dedupe
feature: scan_and_upload
version: 1.0.0

procedures:
  partition_scan:
    command: start_scan
    implementation: src/procedure/cc_py/partition_scan.py
    function: partition_scan
    language: python
    runtime: python3.11

  calculate_cas_hash:
    command: calculate_cas_hash
    implementation: src/procedure/cc_py/calculate_cas_hash.py
    function: calculate_cas_hash
    language: python
    runtime: python3.11

policies:
  hash_only_priority_files:
    event: scan_item_found
    implementation: src/policy/cc_py/hash_only_priority_files.py
    function: hash_only_priority_files
    language: python
    runtime: python3.11
```

**Generated by**: `dizzy gen src`

**Used by**: Deployment tooling to wire components together

## Generation Pipeline Flow

### Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. DEFINE: Write {feature}.feat.yaml                            │
│    - Commands, Events, Procedures, Policies, Projections        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. INIT: dizzy gen init                                         │
│    Step 2: Generate LinkML schemas in def/                      │
│    Step 3: Setup gen/ directory structure                       │
│    Step 4: Generate Pydantic models in gen/pyd/                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. REFINE: Edit LinkML schemas in def/                          │
│    - Add domain-specific attributes                             │
│    - Define field constraints and validations                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. REGEN: dizzy gen init (again)                                │
│    - Regenerate Pydantic models with updated schemas            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. SCAFFOLD: dizzy gen src                                      │
│    Step 6: Generate procedure/policy contexts and protocols     │
│    Step 7: Generate implementation scaffolds in src/            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. IMPLEMENT: Write business logic in src/                      │
│    - Implement procedures                                       │
│    - Implement policies                                         │
│    - Write unit tests                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. DEPLOY: Package and wire components in result/               │
│    - Create deployment-specific wiring                          │
│    - Configure emitters for target infrastructure               │
└─────────────────────────────────────────────────────────────────┘
```

## Key System Files

### CLI Entry Point
**Path**: `/dizzy/src/dizzy/cli.py`
**Purpose**: Main entry point for `dizzy` command
**Key functions**: Argument parsing, command routing

### Generation Commands
**Path**: `/dizzy/src/dizzy/commands/gen_init.py`
**Purpose**: Implements `dizzy gen init`
**Steps**: Schema generation, model generation, directory setup

**Path**: `/dizzy/src/dizzy/commands/gen_src.py`
**Purpose**: Implements `dizzy gen src`
**Steps**: Protocol generation, implementation scaffolding

### Generators
**Path**: `/dizzy/src/dizzy/generators/linkml_generator.py`
**Purpose**: Generate LinkML schema templates from feat.yaml
**Key functions**: `generate_command_schema()`, `generate_event_schema()`

**Path**: `/dizzy/src/dizzy/generators/protocols_generator.py`
**Purpose**: Generate procedure/policy contexts and protocols
**Key functions**: Generate context dataclasses with emitters and queries

**Path**: `/dizzy/src/dizzy/generators/implementation_generator.py`
**Purpose**: Scaffold implementations using Claude Code CLI
**Integration**: Calls Claude Code to generate initial implementation code

### Utilities
**Path**: `/dizzy/src/dizzy/config.py`
**Purpose**: Configuration management
**Loads**: Settings from config files and environment

**Path**: `/dizzy/src/dizzy/helpers/file_utils.py`
**Purpose**: File and directory operations
**Key functions**: Directory creation, `__init__.py` generation

**Path**: `/dizzy/src/dizzy/helpers/subprocess_utils.py`
**Purpose**: Run external tools (LinkML gen-python)
**Key functions**: Safe subprocess execution with error handling

## Common Workflows

### Starting a New Feature

```bash
# 1. Create feature YAML
vim app/mydomain/myfeature.feat.yaml

# 2. Generate initial structure
dizzy gen init --app-dir app/mydomain --feat-dir myfeature

# 3. Edit LinkML schemas to add fields
vim app/mydomain/myfeature/def/commands/*.yaml
vim app/mydomain/myfeature/def/events/*.yaml

# 4. Regenerate Pydantic models
dizzy gen init --app-dir app/mydomain --feat-dir myfeature

# 5. Generate protocols and scaffolds
dizzy gen src --app-dir app/mydomain --feat-dir myfeature

# 6. Implement business logic
vim app/mydomain/myfeature/src/procedure/cc_py/*.py
vim app/mydomain/myfeature/src/policy/cc_py/*.py
```

### Adding a New Command/Event

```bash
# 1. Add to feat.yaml
vim app/mydomain/myfeature.feat.yaml

# 2. Regenerate (preserves existing schemas)
dizzy gen init --app-dir app/mydomain --feat-dir myfeature

# 3. Edit new schema if needed
vim app/mydomain/myfeature/def/commands/new_command.yaml

# 4. Regenerate models
dizzy gen init --app-dir app/mydomain --feat-dir myfeature
```

### Adding a New Procedure/Policy

```bash
# 1. Add to feat.yaml procedures: or policies: section
vim app/mydomain/myfeature.feat.yaml

# 2. Regenerate protocols
dizzy gen src --app-dir app/mydomain --feat-dir myfeature

# 3. Implement logic
vim app/mydomain/myfeature/src/procedure/cc_py/new_procedure.py
```

### Updating an Existing Schema

```bash
# 1. Edit LinkML schema
vim app/mydomain/myfeature/def/commands/my_command.yaml

# 2. Regenerate Pydantic models
dizzy gen init --app-dir app/mydomain --feat-dir myfeature

# 3. Update implementations to use new fields
vim app/mydomain/myfeature/src/procedure/cc_py/*.py
```

## Best Practices

### DO:
- ✓ Edit `feat.yaml` as single source of truth
- ✓ Edit LinkML schemas in `def/` to add domain-specific fields
- ✓ Edit implementations in `src/`
- ✓ Run `dizzy gen init` after schema changes
- ✓ Run `dizzy gen src` after feat.yaml changes
- ✓ Version control `def/`, `src/`, `feat.yaml`, `impl.yaml`

### DON'T:
- ✗ Edit generated code in `gen/` - it will be overwritten
- ✗ Manually create `__init__.py` files - generator handles this
- ✗ Skip editing LinkML schemas - defaults are minimal placeholders
- ✗ Commit `gen/` to version control - it's regeneratable
- ✗ Use `--fresh` flag carelessly - it overwrites existing schemas

## Troubleshooting

### Issue: "LinkML schema validation failed"
**Solution**: Check that all referenced events/commands in feat.yaml actually exist in the events/commands sections

### Issue: "Pydantic model import errors"
**Solution**: Run `dizzy gen init` to regenerate `__init__.py` files with proper imports

### Issue: "Protocol signature mismatch"
**Solution**: Regenerate protocols with `dizzy gen src` after updating feat.yaml

### Issue: "Implementation not found in impl.yaml"
**Solution**: Run `dizzy gen src` to rebuild implementation manifest

### Issue: "Cannot find generated model"
**Solution**: Ensure you ran `dizzy gen init` after creating/modifying LinkML schemas

## Architecture Benefits

### Type Safety
- LinkML schemas provide language-agnostic type definitions
- Pydantic models give Python type hints and validation
- Protocols ensure implementations match expected interfaces

### Single Source of Truth
- `feat.yaml` defines entire system
- All generated code derives from this one file
- Changes propagate automatically through regeneration

### Separation of Concerns
- `def/` - Data structure definitions (schemas)
- `gen/` - Generated type-safe interfaces (disposable)
- `src/` - Business logic implementations (precious)
- `result/` - Deployment configurations (environment-specific)

### Regeneration Safety
- Generated code in `gen/` is disposable
- Implementation code in `src/` is never touched by generators
- Schemas in `def/` preserved unless `--fresh` flag used

### Language Flexibility
- LinkML can generate bindings for many languages
- Currently generates Python, but could generate TypeScript, Rust, Go, etc.
- Implementations can mix languages (Python procedures, Rust policies)

This pipeline enables rapid development while maintaining type safety and architectural consistency across the entire event-driven system.
