# DIZZY Architecture Specification

**Status**: Draft
**Version**: 0.1.0
**Date**: 2026-01-31
**Author**: Conrad Mearns
**Category**: Informational

---

## Abstract

This document specifies DIZZY, a software architecture framework for building event-driven systems with decoupled infrastructure. DIZZY implements Command Query Responsibility Separation (CQRS) with Event Sourcing using language-agnostic schemas and a code generation pipeline. The architecture enables reversible decisions, supports multiple programming languages, and provides infrastructure independence through strict separation of concerns.

## Table of Contents

1. [Introduction](#1-introduction)
2. [Terminology](#2-terminology)
3. [Architecture Overview](#3-architecture-overview)
4. [Component Specifications](#4-component-specifications)
5. [Data Flow Specifications](#5-data-flow-specifications)
6. [Code Generation Pipeline](#6-code-generation-pipeline)
7. [Implementation Requirements](#7-implementation-requirements)
8. [Deployment Specifications](#8-deployment-specifications)
9. [Feature Requirements](#9-feature-requirements)
10. [Security Considerations](#10-security-considerations)
11. [References](#11-references)

---

## 1. Introduction

### 1.1 Motivation

Modern software development faces several persistent challenges:

1. **Technology Lock-in**: Architectural decisions made early in a project often become irreversible constraints that persist for decades
2. **Infrastructure Coupling**: Business logic becomes tightly coupled to specific cloud providers, databases, or messaging systems
3. **Language Barriers**: Components written in different programming languages cannot easily interoperate
4. **Schema Evolution**: Changing data structures requires coordinated updates across multiple systems
5. **Debugging Difficulty**: Understanding system behavior requires reconstructing state from scattered logs and databases

### 1.2 Design Principles

DIZZY addresses these challenges through three core principles:

1. **Support (Almost) Any Programming Language**: Components communicate via serialized data rather than shared memory or libraries
2. **Deferring Decisions**: Critical choices (database selection, serialization format, deployment architecture) can be postponed or reversed
3. **Architecting for Reversibility**: Wrong decisions can be corrected without system-wide rewrites

### 1.3 Scope

This specification defines:

- Core architectural components and their responsibilities
- Data flow patterns and communication protocols
- Code generation pipeline and tooling requirements
- Implementation guidelines for procedures, policies, and projections
- Deployment strategies for various infrastructure targets

This specification does NOT define:

- Specific serialization formats (implementation choice)
- Database technologies (implementation choice)
- Network protocols for component communication (implementation choice)
- Programming languages for implementations (implementation choice)

### 1.4 Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119.

---

## 2. Terminology

### 2.1 Core Terms

**Command** ($c$)
An imperative instruction describing an intent to perform work. Commands are ephemeral and trigger exactly one Procedure.

**Event** ($e$)
An immutable record of a fact that has occurred in the system. Events are durable and stored permanently in the Event Store.

**Procedure** ($d$)
A process that handles a Command, performs work (with potential side effects), and emits zero or more Events.

**Policy** ($y$)
A process that reacts to an Event, applies business logic, and emits zero or more Commands.

**Projection** ($j$)
A process that transforms Events into Model updates, maintaining derived state optimized for queries.

**Model** ($m$)
A database representation that provides optimized read access to system state. Models are derived from Events and can be rebuilt.

**Query** ($Q$)
A request-response interface for reading data from Models. Queries consist of input parameters ($q_i$), processing logic ($q_p$), and output results ($q_o$).

### 2.2 Architectural Terms

**Event Store**
A durable, append-only log containing all Events that have occurred in the system. The Event Store is the single source of truth.

**Event Loop**
The cycle: Command → Procedure → Event → Policy → Command

**Model Loop**
The cycle: Event → Projection → Model → Query

**Context**
An execution environment provided to Procedures and Policies containing emitters (callbacks for producing Commands/Events) and queries (interfaces for reading Models).

**Feature Definition**
A YAML file (`{feature}.feat.yaml`) serving as the single source of truth for a DIZZY feature, declaring all Commands, Events, Procedures, Policies, Projections, and Queries.

### 2.3 Implementation Terms

**LinkML Schema**
A language-agnostic data structure definition using the Linked Data Modeling Language. Schemas define Commands, Events, and Models.

**Pydantic Model**
A Python dataclass with type hints and validation logic, generated from LinkML schemas.

**Protocol**
A type-safe interface definition specifying the signature required for Procedure or Policy implementations.

**Implementation Manifest**
A YAML file (`impl.yaml`) mapping Procedures and Policies to their concrete implementations.

---

## 3. Architecture Overview

### 3.1 Architectural Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Event Loop                           │
│                                                             │
│  Command (c) → Procedure (d) → Event (e) → Policy (y)      │
│       ↑                                          │          │
│       └──────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        Model Loop                           │
│                                                             │
│  Event (e) → Projection (j) → Model (m) → Query (Q)        │
│                                              │              │
│                                              ↓              │
│                                     Procedure/Policy        │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Separation of Concerns

DIZZY enforces strict separation between:

**Write Side** (CQRS Command Side):
- Commands express intent
- Procedures perform work
- Events record facts
- All writes flow through Event Store

**Read Side** (CQRS Query Side):
- Events trigger projections
- Projections update models
- Queries read from models
- Multiple models can represent the same data differently

### 3.3 Event Sourcing

The system stores the complete sequence of Events rather than current state. This enables:

1. Complete audit trail
2. Time travel (reconstruct any historical state)
3. Debug by replay
4. Multiple model representations
5. Late schema binding (add new projections to existing events)

### 3.4 Language Agnostic Design

Components communicate exclusively through serialized data structures:

- No shared memory
- No library dependencies between components
- Each component can be implemented in any language
- Type safety maintained through schema definitions

---

## 4. Component Specifications

### 4.1 Commands

#### 4.1.1 Properties

Commands MUST be:
- **Imperative**: Express intent (e.g., "StartScan", "CalculateHash")
- **Ephemeral**: Not persisted long-term
- **Unique**: Identified by a unique `command_id`

Commands SHOULD:
- Use present tense naming
- Include all parameters needed for execution
- Be idempotent when possible

#### 4.1.2 Schema Definition

Commands MUST be defined as LinkML schemas in `def/commands/{command_name}.yaml`:

```yaml
classes:
  CommandName:
    is_a: Command
    attributes:
      command_id:
        required: true
        identifier: true
        range: string
      # Additional domain-specific attributes
```

#### 4.1.3 Lifecycle

1. Command is created (by user, policy, or external system)
2. Command is validated against schema
3. Command is routed to exactly one Procedure
4. Command is processed
5. Command is discarded (not stored long-term)

### 4.2 Events

#### 4.2.1 Properties

Events MUST be:
- **Immutable**: Never modified after creation
- **Durable**: Stored permanently in Event Store
- **Factual**: Describe what happened (past tense)
- **Unique**: Identified by unique `event_id`

Events SHOULD:
- Use past tense naming (e.g., "ScanCompleted", "HashCalculated")
- Include timestamp
- Include sufficient context for projections
- Be granular (one fact per event)

#### 4.2.2 Schema Definition

Events MUST be defined as LinkML schemas in `def/events/{event_name}.yaml`:

```yaml
classes:
  EventName:
    is_a: Event
    attributes:
      event_id:
        required: true
        identifier: true
        range: string
      timestamp:
        required: true
        range: datetime
      # Additional domain-specific attributes
```

#### 4.2.3 Lifecycle

1. Event is emitted by Procedure
2. Event is validated against schema
3. Event is appended to Event Store
4. Event triggers zero or more Policies
5. Event triggers zero or more Projections
6. Event is retained indefinitely

### 4.3 Procedures

#### 4.3.1 Properties

Procedures MUST:
- Accept exactly one Command type as input
- Receive a Context with emitters and queries
- Return nothing (use emitters for output)
- Be deterministic given same inputs and query results

Procedures MAY:
- Perform side effects (I/O, external API calls)
- Read from Models via queries
- Emit multiple Events
- Emit different Events based on execution results

#### 4.3.2 Signature

```python
def procedure_name(context: ProcedureContext, command: CommandType) -> None:
    # Implementation
    context.emit.event_name(EventData(...))
```

#### 4.3.3 Context Structure

```python
@dataclass
class ProcedureContext:
    emit: ProcedureEmitters    # Callbacks for emitting events
    query: ProcedureQueries    # Interfaces for querying models
```

#### 4.3.4 Error Handling

Procedures SHOULD:
- Emit error events rather than raising exceptions for domain errors
- Only raise exceptions for infrastructure failures
- Include error context in error events

### 4.4 Policies

#### 4.4.1 Properties

Policies MUST:
- React to exactly one Event type
- Receive a Context with emitters and queries
- Return nothing (use emitters for output)
- Be side-effect free (read-only operations)

Policies MAY:
- Emit zero or more Commands
- Read from Models via queries
- Implement complex business logic
- Emit different Commands based on query results

#### 4.4.2 Signature

```python
def policy_name(context: PolicyContext, event: EventType) -> None:
    # Implementation
    if condition:
        context.emit.command_name(CommandData(...))
```

#### 4.4.3 Context Structure

```python
@dataclass
class PolicyContext:
    emit: PolicyEmitters      # Callbacks for emitting commands
    query: PolicyQueries      # Interfaces for querying models
```

#### 4.4.4 Design Guidelines

Policies SHOULD:
- Encode business rules, not technical operations
- Be testable with mock queries
- Avoid complex state management
- Make decisions based on current Model state

### 4.5 Projections

#### 4.5.1 Properties

Projections MUST:
- Be idempotent (replay safe)
- Be deterministic (same Event produces same Model update)
- Handle Event ordering issues gracefully

Projections MAY:
- Update multiple Models per Event
- Ignore Events that don't affect their Model
- Maintain internal state for aggregation

#### 4.5.2 Implementation

```python
def projection_name(event: EventType, model: ModelType) -> ModelType:
    # Update model based on event
    return updated_model
```

#### 4.5.3 Rebuild Requirements

Projections MUST support full Model rebuild:
1. Clear existing Model
2. Replay all Events from Event Store
3. Apply each Event to Model
4. Resulting Model MUST match production Model

### 4.6 Models

#### 4.6.1 Properties

Models:
- Represent derived state (not source of truth)
- Optimize specific query patterns
- Can be rebuilt from Events at any time
- MAY use any database technology

#### 4.6.2 Schema Definition

Models are defined in Feature Definition under `projections`:

```yaml
projections:
  ModelName:
    description: "Model purpose"
    attributes:
      field_name: "Field description"
```

#### 4.6.3 Consistency

Models MUST:
- Eventually consistent with Event Store
- Support concurrent updates if multiple instances exist
- Handle duplicate Events idempotently

### 4.7 Queries

#### 4.7.1 Properties

Queries MUST:
- Read from Models (not Event Store)
- Be side-effect free
- Define typed inputs and outputs

Queries MAY:
- Join multiple Models
- Implement caching
- Use any database query language

#### 4.7.2 Structure

Queries consist of three components:

1. **Query Input** ($q_i$): Parameters defining what to retrieve
2. **Query Process** ($q_p$): Logic for retrieving data from Models
3. **Query Output** ($q_o$): Structured result data

#### 4.7.3 Definition

Queries are defined in Feature Definition under `queries`:

```yaml
queries:
  query_name:
    description: "What this query retrieves"
    uses: [Model1, Model2]
    parameters:
      - param_name: "Parameter description"
    returns: "Return type description"
```

---

## 5. Data Flow Specifications

### 5.1 Event Loop Flow

```
1. Command arrives (from user, policy, or external system)
2. System validates Command against schema
3. System routes Command to registered Procedure
4. Procedure executes with provided Context
5. Procedure emits Events via context.emit
6. Events are validated and appended to Event Store
7. Events trigger registered Policies
8. Policies execute and emit new Commands
9. Loop continues from step 1
```

### 5.2 Model Loop Flow

```
1. Event is appended to Event Store
2. Event triggers registered Projections
3. Projections update Models
4. Models become available for Queries
5. Procedures/Policies use Queries via Context
6. Query results influence future Commands/Events
```

### 5.3 Message Ordering

#### 5.3.1 Within Event Store

Events MUST be:
- Totally ordered within a single Event Store
- Timestamped with monotonic clock
- Sequentially numbered

#### 5.3.2 Between Components

The system SHOULD:
- Process Events in order when possible
- Handle out-of-order Events gracefully in Projections
- Use correlation IDs to track related Events

### 5.4 Failure Handling

#### 5.4.1 Procedure Failure

If a Procedure fails:
1. Command is NOT marked as processed
2. Procedure MAY emit error Event before failing
3. System MAY retry Command (deployment-specific)
4. No partial Events are committed

#### 5.4.2 Policy Failure

If a Policy fails:
1. Event remains in Event Store
2. Policy MAY be retried (deployment-specific)
3. Other Policies still process the Event
4. No partial Commands are emitted

#### 5.4.3 Projection Failure

If a Projection fails:
1. Event remains in Event Store
2. Model MAY be inconsistent
3. Projection SHOULD be rerun from last checkpoint
4. Other Projections continue processing

---

## 6. Code Generation Pipeline

### 6.1 Overview

DIZZY uses a multi-stage code generation pipeline to maintain type safety while preserving implementation flexibility.

### 6.2 Pipeline Stages

#### 6.2.1 Stage 1: Feature Definition

**Input**: Domain knowledge
**Output**: `{feature}.feat.yaml`
**Tool**: Manual editing

Feature Definition MUST declare:
- All Commands with descriptions
- All Events with descriptions
- All Procedures with command mappings, emits lists, and contexts
- All Policies with event mappings, emits lists, and contexts
- All Projections (Models) with attributes
- All Queries with parameters and return types

#### 6.2.2 Stage 2: Schema Generation

**Input**: `{feature}.feat.yaml`
**Output**: LinkML schemas in `def/commands/` and `def/events/`
**Tool**: `dizzy gen init`

Generated schemas:
- MUST include unique IDs and namespaces
- MUST import base Command or Event types
- MUST include placeholder attributes
- SHOULD be edited to add domain-specific attributes

#### 6.2.3 Stage 3: Model Generation

**Input**: LinkML schemas from `def/`
**Output**: Pydantic models in `gen/pyd/commands/` and `gen/pyd/events/`
**Tool**: `dizzy gen init` (uses `linkml-gen-pydantic`)

Generated models:
- MUST include type hints
- MUST include validation logic
- MUST NOT be manually edited
- MUST be regenerated when schemas change

#### 6.2.4 Stage 4: Protocol Generation

**Input**: `{feature}.feat.yaml` and generated models
**Output**: Context and Protocol files in `gen/pyd/procedure/` and `gen/pyd/policy/`
**Tool**: `dizzy gen src`

Generated protocols:
- MUST define type-safe interfaces
- MUST include Context with emitters and queries
- MUST NOT be manually edited
- MUST be regenerated when Feature Definition changes

#### 6.2.5 Stage 5: Implementation

**Input**: Generated protocols
**Output**: Implementation files in `src/procedure/` and `src/policy/`
**Tool**: Manual development or `dizzy gen src` scaffolding

Implementations:
- MUST match Protocol signatures
- MUST be manually edited
- MUST NOT be overwritten by regeneration
- SHOULD include unit tests

#### 6.2.6 Stage 6: Deployment

**Input**: Implementations and `impl.yaml` manifest
**Output**: Deployment-specific artifacts in `result/`
**Tool**: Deployment-specific tooling

Deployment artifacts:
- MUST wire emitters to infrastructure (queues, lambdas, etc.)
- MUST wire queries to database implementations
- MAY use different strategies per environment

### 6.3 Regeneration Rules

#### 6.3.1 Safe Regeneration

The following operations are safe:
- Regenerating `gen/` after schema changes
- Regenerating protocols after Feature Definition changes
- Adding new Commands/Events/Procedures/Policies

#### 6.3.2 Manual Intervention Required

The following require manual updates:
- Schema changes affecting existing implementations
- Adding new attributes to Commands/Events
- Changing Procedure/Policy signatures

#### 6.3.3 Files Never Touched by Generator

The generator MUST NEVER modify:
- Files in `src/` (implementations)
- Tests
- Deployment configurations
- Documentation

---

## 7. Implementation Requirements

### 7.1 Directory Structure

A DIZZY feature MUST follow this structure:

```
{feature}/
├── def/                  # LinkML schemas (edit after generation)
│   ├── commands/
│   └── events/
├── gen/                  # Generated code (DO NOT EDIT)
│   └── pyd/
│       ├── commands/
│       ├── events/
│       ├── procedure/
│       └── policy/
├── src/                  # Implementations (EDIT HERE)
│   ├── procedure/
│   └── policy/
├── result/               # Deployment artifacts
├── {feature}.feat.yaml   # Feature Definition
└── impl.yaml             # Implementation manifest
```

### 7.2 Naming Conventions

#### 7.2.1 Commands

- PascalCase
- Present tense verbs
- Example: `StartScan`, `CalculateHash`, `SendEmail`

#### 7.2.2 Events

- PascalCase
- Past tense
- Example: `ScanStarted`, `HashCalculated`, `EmailSent`

#### 7.2.3 Procedures

- snake_case
- Verb phrase
- Example: `partition_scan`, `calculate_cas_hash`, `send_welcome_email`

#### 7.2.4 Policies

- snake_case
- Business rule description
- Example: `hash_priority_files`, `retry_failed_scans`, `notify_on_completion`

#### 7.2.5 Models

- PascalCase
- Noun phrase
- Example: `ScanResult`, `FileRecord`, `UserProfile`

#### 7.2.6 Queries

- snake_case
- Starts with `get_` or `find_` or `list_`
- Example: `get_scan_results`, `find_files_by_hash`, `list_active_users`

### 7.3 Version Control

Projects MUST version control:
- Feature Definitions (`*.feat.yaml`)
- LinkML schemas (`def/`)
- Implementations (`src/`)
- Tests
- Implementation manifests (`impl.yaml`)

Projects SHOULD NOT version control:
- Generated code (`gen/`)
- Build artifacts
- Deployment-specific credentials

### 7.4 Testing Requirements

#### 7.4.1 Unit Tests

Implementations MUST include unit tests that:
- Mock Context emitters and queries
- Verify Events are emitted correctly
- Test error handling
- Cover edge cases

#### 7.4.2 Integration Tests

Features SHOULD include integration tests that:
- Test Event Loop flows
- Verify Projections update Models correctly
- Test Queries return expected data
- Validate end-to-end workflows

#### 7.4.3 Contract Tests

Features SHOULD verify:
- Implementations match Protocol signatures
- Only declared Events are emitted
- All required Events are eventually emitted

---

## 8. Deployment Specifications

### 8.1 Deployment Independence

Implementations MUST NOT:
- Import deployment-specific libraries
- Reference environment-specific configuration
- Assume specific messaging infrastructure
- Hardcode database connection strings

### 8.2 Wiring Requirements

Deployment code MUST:
- Instantiate Context with concrete emitters
- Provide Query implementations
- Handle serialization/deserialization
- Manage infrastructure connections

### 8.3 Deployment Patterns

#### 8.3.1 Serverless (AWS Lambda)

```python
def lambda_handler(event, context):
    # Parse Command from event
    command = parse_command(event)

    # Wire Context to SQS
    procedure_context = create_context(
        emitters=sqs_emitters(),
        queries=dynamodb_queries()
    )

    # Execute Procedure
    procedure(procedure_context, command)
```

#### 8.3.2 Message Queue Service

```python
def worker_loop():
    while True:
        message = queue.receive()
        command = deserialize(message)

        procedure_context = create_context(
            emitters=queue_emitters(),
            queries=postgres_queries()
        )

        procedure(procedure_context, command)
        queue.ack(message)
```

#### 8.3.3 Monolithic Service

```python
def handle_request(request):
    command = request_to_command(request)

    procedure_context = create_context(
        emitters=in_memory_emitters(),
        queries=sqlite_queries()
    )

    procedure(procedure_context, command)
    return response_from_events()
```

### 8.4 Scalability

Deployments MAY:
- Run multiple instances of Procedures/Policies
- Partition Event Store
- Shard Models across databases
- Use read replicas for Queries

Deployments MUST ensure:
- At-least-once Event delivery
- Idempotent Projection updates
- Event ordering within partitions

---

## 9. Feature Requirements

This section defines specific feature requirements for DIZZY system capabilities.

### 9.1 Core System Requirements

#### 9.1.1 Feature Definition Validation

**Requirement**: The system MUST validate Feature Definitions before code generation.

**Acceptance Criteria**:
- All referenced Commands exist in `commands:` section
- All referenced Events exist in `events:` section
- All Procedure `emits` lists reference valid Events
- All Policy `emits` lists reference valid Commands
- All Query `uses` lists reference valid Projections

#### 9.1.2 Schema Evolution

**Requirement**: The system SHOULD support backward-compatible schema evolution.

**Acceptance Criteria**:
- Adding optional attributes to existing schemas does not break implementations
- Event Store can contain Events with different schema versions
- Projections handle missing attributes gracefully

#### 9.1.3 Code Generation Idempotency

**Requirement**: Running code generation multiple times MUST produce identical output.

**Acceptance Criteria**:
- `dizzy gen init` produces same schemas given same Feature Definition
- `dizzy gen src` produces same protocols given same schemas
- Timestamps and random IDs are not included in generated code

### 9.2 Dependency Update Notification

**Status**: Proposed
**Priority**: TBD
**Complexity**: TBD

_This section is reserved for detailed requirements regarding automated dependency update notification and management within DIZZY projects._

**Placeholder Subsections**:

#### 9.2.1 Dependency Tracking

_Requirements for tracking dependencies across DIZZY components_

#### 9.2.2 Update Detection

_Requirements for detecting when dependencies have updates available_

#### 9.2.3 Notification Mechanism

_Requirements for notifying developers of available updates_

#### 9.2.4 Compatibility Verification

_Requirements for verifying update compatibility with current implementations_

#### 9.2.5 Update Workflow

_Requirements for the process of applying dependency updates_

---

## 10. Security Considerations

### 10.1 Event Store Security

The Event Store:
- MUST be append-only (no deletions or modifications)
- MUST authenticate all write operations
- SHOULD encrypt Events at rest
- SHOULD encrypt Events in transit

### 10.2 Command Validation

Commands MUST:
- Be validated against schema before processing
- Include authentication/authorization context
- Reject Commands from untrusted sources
- Sanitize inputs to prevent injection attacks

### 10.3 Query Authorization

Queries MUST:
- Enforce access control based on caller identity
- Prevent unauthorized data access
- Log query access for audit
- Rate limit to prevent DoS

### 10.4 Procedure Side Effects

Procedures that interact with external systems MUST:
- Validate all external inputs
- Use secure communication channels
- Handle credentials securely
- Implement retry with exponential backoff

### 10.5 Sensitive Data

Events containing sensitive data SHOULD:
- Be encrypted in Event Store
- Use field-level encryption where appropriate
- Implement data retention policies
- Support GDPR/privacy compliance (e.g., event redaction)

### 10.6 Deployment Security

Deployment configurations MUST:
- Store credentials in secure vaults (not version control)
- Use least-privilege access for components
- Implement network isolation where appropriate
- Regularly update dependencies for security patches

---

## 11. References

### 11.1 Normative References

[RFC2119] Bradner, S., "Key words for use in RFCs to Indicate Requirement Levels", BCP 14, RFC 2119, March 1997.

[LinkML] "Linked Data Modeling Language", https://linkml.io/

[CQRS] Fowler, M., "CQRS", https://martinfowler.com/bliki/CQRS.html

[EventSourcing] Fowler, M., "Event Sourcing", https://martinfowler.com/eaaDev/EventSourcing.html

### 11.2 Informative References

[DDD] Evans, E., "Domain-Driven Design: Tackling Complexity in the Heart of Software", Addison-Wesley, 2003.

[CosmicPython] Percival, H. and Gregory, B., "Architecture Patterns with Python", O'Reilly, 2020, https://www.cosmicpython.com/

[Conway] Conway, M., "How Do Committees Invent?", 1968, http://www.melconway.com/Home/Committees_Paper.html

[Dijkstra] Dijkstra, E., "The Humble Programmer", ACM Turing Lecture, 1972.

[Feathers] Feathers, M., "Working Effectively with Legacy Code", Prentice Hall, 2004.

[Kleppmann] Kleppmann, M., "Designing Data-Intensive Applications", O'Reilly, 2017.

### 11.3 Project References

[CLAUDE.md] "DIZZY Documentation Index", /CLAUDE.md

[Concepts] "DIZZY Core Concepts", /docs/concepts.md

[BuildOrder] "DIZZY Build Order", /docs/build-order.md

[Testing] "DIZZY Testing Guide", /docs/testing.md

[Pipeline] "DIZZY Code Generation Pipeline", /docs/analysis.md

[Whitepaper] "DIZZY Whitepaper", /whitepaper.typ

---

## Appendix A: Feature Definition Example

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

procedures:
  partition_scan:
    description: "Walk directory tree and emit item events"
    command: start_scan
    emits: [scan_item_found, scan_complete, scan_item_failed]
    context: [get_previous_scan_results]

  calculate_cas_hash:
    description: "Compute content-addressed hash"
    command: calculate_cas_hash
    emits: [cas_hash_calculated]
    context: []

policies:
  hash_only_priority_files:
    description: "Queue hash commands only for priority file types"
    event: scan_item_found
    emits: [calculate_cas_hash]
    context: [get_file_priority_config]

projections:
  ScanResult:
    description: "Aggregated scan statistics"
    attributes:
      scan_id: "Unique scan identifier"
      total_items: "Number of items found"
      total_bytes: "Total size in bytes"

queries:
  get_scan_results:
    description: "Retrieve aggregated scan statistics"
    uses: [ScanResult]
    parameters:
      - scan_id: "Scan identifier"
    returns: "ScanResult object or None"
```

---

## Appendix B: Change Log

**Version 0.1.0 (2026-01-31)**:
- Initial draft specification
- Core architecture definition
- Component specifications
- Code generation pipeline
- Placeholder for Dependency Update Notification feature

---

**End of Specification**
