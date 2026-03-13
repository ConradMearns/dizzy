#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#import "figures.typ": flow

// Specification Configuration
#set page(
  paper: "us-letter",
  margin: (x: 1in, y: 1in),
)

#set text(
  size: 12pt,
)

#set par(
  justify: true,
  leading: 0.65em,
)

// Title
#align(center)[
  #text(24pt, weight: "bold")[D I Z Z Y]
  
  #text(12pt, weight: "bold")[
    Specification for Event Driven Architectures with Decoupled Infrastructure
  ]

  #v(0.5em)

  #text(12pt)[Conrad Mearns]
  // #text(11pt)[#datetime.today().display()]
]

#figure(flow)

= Abstract

This document specifies DIZZY, a software architecture framework for building event-driven systems with decoupled infrastructure. DIZZY implements Command Query Responsibility Separation (CQRS) with Event Sourcing using language-agnostic schemas and a code generation pipeline. The architecture enables reversible decisions, supports multiple programming languages, and provides infrastructure independence through strict separation of concerns.

For the philosophy, motivation, and design rationale behind DIZZY, see the companion whitepaper.

// Enable section numbering
#set heading(numbering: "1a1a1a1a")
// #set heading(numbering: "1.1")

#pagebreak()

// Table of Contents
#outline(
  title: [Table of Contents],
  indent: auto,
)

#pagebreak()


= DIZZY

#figure(
  flow
) <fig-flow>

The general flow for execution flow in dizzy is represented similarly to traditional DDD EDA.
Commands ($c$) describe an imperative intent. 
Events ($e$) record immutable facts about our system, and external effects.
Procedures ($d$) 
Policies ($y$) 

Event's are all you need to record and query for information with an Event Sourcing paradigm,
but queries grow slower as the Event Store grows; read's are unoptimized.
In general, we want to enable faster time to action by careful design of queries that answer specific questions about the world.
We can accomplish this by using events to inform a World Model ($m$).

We can generally support any number Models, utilizing any number of databases and database platforms. As long as we can guarantee that databases can be managed solely through Events,
then we can always rebuild deterministic state.

Since the number of events in our system $|e|$ is uncoupled from the number of unique model elements $|m|$ - we need a map from events to model elements. Projections ($j$) serve as the software component to resolve this mapping.

In order for procedures and policies to effectively query from the domain model, We specify a schema for all Queries ($Q$). Queries are represented by a double-arrow dashed line to show That they are bidirectional flow: Request and Response.  Each query element may be instead represented by 3 subcomponents. Query inputs ($q_i$), Query outputs ($q_o$), And the query process ($q_p$).

In the general flow diagram, this is denoted with the dashed line as shorthand.


== Component Specifications

=== Commands

Commands MUST be
- *Imperative*: Express intent (e.g., "StartScan", "CalculateHash")
- *Ephemeral*: Not persisted long-term
- *Unique*: Identified by a unique `command_id`

Commands SHOULD:
- Use present tense naming
- Include all parameters needed for execution
- Be idempotent when possible

1. Command is created (by user, policy, or external system)
2. Command is validated against schema
3. Command is routed to exactly one Procedure
4. Command is processed
5. Command is discarded (not stored long-term)

=== Events

Events MUST be:
- *Immutable*: Never modified after creation
- *Durable*: Stored permanently in Event Store
- *Factual*: Describe what happened (past tense)
- *Unique*: Identified by unique `event_id`

Events SHOULD:
- Use past tense naming (e.g., "ScanCompleted", "HashCalculated")
- Include timestamp
- Include sufficient context for projections
- Be granular (one fact per event)

1. Event is emitted by Procedure
2. Event is validated against schema
3. Event is appended to Event Store
4. Event triggers zero or more Policies
5. Event triggers zero or more Projections
6. Event is retained indefinitely


=== Procedures

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

Procedures SHOULD:
- Emit error events rather than raising exceptions for domain errors
- Only raise exceptions for infrastructure failures
- Include error context in error events

=== Policies

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

Policies SHOULD:
- Encode business rules, not technical operations
- Be testable with mock queries
- Avoid complex state management
- Make decisions based on current Model state


=== Projections

Projections MUST:
- Be idempotent (replay safe)
- Be deterministic (same Event produces same Model update)
- Handle Event ordering issues gracefully

Projections MAY:
- Update multiple Models per Event
- Ignore Events that don't affect their Model
- Maintain internal state for aggregation

Projections MUST support full Model rebuild:
1. Clear existing Model
2. Replay all Events from Event Store
3. Apply each Event to Model
4. Resulting Model MUST match production Model


=== Models

Models:
- Represent derived state (not source of truth)
- Optimize specific query patterns
- Can be rebuilt from Events at any time
- MAY use any database technology

Models MUST:
- Eventually consistent with Event Store
- Support concurrent updates if multiple instances exist
- Handle duplicate Events idempotently

=== Queries

Queries MUST:
- Read from Models (not Event Store)
- Be side-effect free
- Define typed inputs and outputs

Queries MAY:
- Join multiple Models
- Implement caching
- Use any database query language

Queries consist of three components:

1. *Query Input* ($q_i$): Parameters defining what to retrieve
2. *Query Process* ($q_p$): Logic for retrieving data from Models
3. *Query Output* ($q_o$): Structured result data


// ==== context
// =======
// Processes are the opinionated wrappers of library code that preforms work,
// executes algorithms, crunches numbers, sorts data, and everything in between.

// Processes are mostly intended to be fire-and-forget.
// Some single input arrives, work is done, and the function exits.
// DIZZY breaks from other conventions by omitting `return` statements completely. Instead, processes use dependency injection to acquire callback functions which are defined at deployment time. 



// ==== Context

// The general design philosophy of a process is that we don't want to wait to inform other components of the work we've completed.

// Instead of relying on return codes, everything looks like a callback. How this callback is implemented is up to the deployment code. // TODO link to deployment section

// In most cases, the callback is a simple `put` onto a queue.

// #box[
// ```python
// @dataclass
// class Context:
//     emit: BazCrunchedEmitter # Callable[[BazCrunched], None]
//     query: BazQueriers # assuming has a .search(str) query
// def process(input: Input, context: Context):
//   baz = foo(input.bar, context.query.search("fubar term history"))
//   context.emit(BazCrunched(baz))
// ```
// ]


== Data Flow Specifications

=== Event Loop Flow

1. Command arrives (from user, policy, or external system)
2. System validates Command against schema
3. System routes Command to registered Procedure
4. Procedure executes with provided Context
5. Procedure emits Events via context.emit
6. Events are validated and appended to Event Store
7. Events trigger registered Policies
8. Policies execute and emit new Commands
9. Loop continues from step 1


=== Model Loop Flow

1. Event is appended to Event Store
2. Event triggers registered Projections
3. Projections update Models
4. Models become available for Queries
5. Procedures/Policies use Queries via Context
6. Query results influence future Commands/Events

// == modelling recommendations

// durable execution; sagas; identity;

// == development recommendations

// unit testing; chaos testing; 

// def; gen; src; bin;

// == deployment recommendations

// event sourcing; queues; 

// == user interfaces

// similarities to model view controller; $c->d->Q$

// == examples

// todo with ui; rtos; k8s web app; etl;





== Code Generation Pipeline

=== Overview

DIZZY uses a multi-stage code generation pipeline to maintain type safety while preserving implementation flexibility.

// A DIZZY feature MUST follow this structure:



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

=== Pipeline Stages

==== Stage 1: Feature Definition

*Input*: Domain knowledge
*Output*: `{feature}.feat.yaml`
*Tool*: Manual editing

Feature Definition MUST declare:
- All Commands with descriptions
- All Events with descriptions
- All Procedures with command mappings, emits lists, and contexts
- All Policies with event mappings, emits lists, and contexts
- All Projections (Models) with attributes
- All Queries with parameters and return types

=== Stage 2: Schema Generation

*Input*: `{feature}.feat.yaml`
*Output*: LinkML schemas in `def/commands/` and `def/events/`
*Tool*: `dizzy gen init`

Generated schemas:
- MUST include unique IDs and namespaces
- MUST import base Command or Event types
- MUST include placeholder attributes
- SHOULD be edited to add domain-specific attributes

==== Stage 3: Model Generation

*Input*: LinkML schemas from `def/`
*Output*: Pydantic models in `gen/pyd/commands/` and `gen/pyd/events/`
*Tool*: `dizzy gen init` (uses `linkml-gen-pydantic`)

Generated models:
- MUST include type hints
- MUST include validation logic
- MUST NOT be manually edited
- MUST be regenerated when schemas change

==== Stage 4: Protocol Generation

*Input*: `{feature}.feat.yaml` and generated models
*Output*: Context and Protocol files in `gen/pyd/procedure/` and `gen/pyd/policy/`
*Tool*: `dizzy gen src`

Generated protocols:
- MUST define type-safe interfaces
- MUST include Context with emitters and queries
- MUST NOT be manually edited
- MUST be regenerated when Feature Definition changes

==== Stage 5: Implementation

*Input*: Generated protocols
*Output*: Implementation files in `src/procedure/` and `src/policy/`
*Tool*: Manual development or `dizzy gen src` scaffolding

Implementations:
- MUST match Protocol signatures
- MUST be manually edited
- MUST NOT be overwritten by regeneration
- SHOULD include unit tests

==== Stage 6: Deployment

*Input*: Implementations and `impl.yaml` manifest
*Output*: Deployment-specific artifacts in `result/`
*Tool*: Deployment-specific tooling

Deployment artifacts:
- MUST wire emitters to infrastructure (queues, lambdas, etc.)
- MUST wire queries to database implementations
- MAY use different strategies per environment

=== Regeneration Rules

==== Safe Regeneration

The following operations are safe:
- Regenerating `gen/` after schema changes
- Regenerating protocols after Feature Definition changes
- Adding new Commands/Events/Procedures/Policies

==== Manual Intervention Required

The following require manual updates:
- Schema changes affecting existing implementations
- Adding new attributes to Commands/Events
- Changing Procedure/Policy signatures

==== Files Never Touched by Generator

The generator MUST NEVER modify:
- Files in `src/` (implementations)
- Tests
- Deployment configurations
- Documentation

== Testing
=== Model Tests
- cardinality
=== Other Data Tests?
=== Projections
=== Queries
=== Procedures
=== Chaos Testing









// = Figures


// #diagram(
//   node-corner-radius: 4pt,

//   // Event space elements
//   node((0,0), $e_1$),
//   node((0,1), $e_2$),
//   node((0,2), $e_3$),
//   node((0,3), $e_4$),
//   node((0,4), $e_5$),
//   node((0,5), $e_6$),

//   // Model space elements
//   node((3,0), $m_1$),
//   node((3,1), $m_2$),
//   node((3,2), $m_3$),

//   {
//     let tint(c) = (stroke: c, fill: rgb(..c.components().slice(0,3), 5%), inset: 8pt)
//     node(enclose: ((0,0), (0,5)), ..tint(blue), name: <e>)
//     node(enclose: ((3,0), (3,2)), ..tint(green), name: <m>)
//   },

//   edge(<e>, <m>, "->", $j$, stroke: 2pt),
// )

// #diagram(
//   node-corner-radius: 4pt,

//   // Event space elements (on top)
//   node((0,0), $e_1$),
//   node((1,0), $e_2$),
//   node((2,0), $e_3$),
//   node((3,0), $e_4$),
//   node((4,0), $e_5$),
//   node((5,0), $e_6$),

//   // Model space elements (on bottom)
//   node((0,3), $m_1$),
//   node((1,3), $m_2$),
//   node((2,3), $m_3$),

//   {
//     let tint(c) = (stroke: c, fill: rgb(..c.components().slice(0,3), 5%), inset: 8pt)
//     node(enclose: ((0,0), (5,0)), ..tint(blue), name: <e>)
//     node(enclose: ((0,3), (2,3)), ..tint(green), name: <m>)
//   },

//   // Complex mapping between events and models
//   edge((0,0), (0,3), "->", stroke: .5pt),
//   edge((0,0), (1,3), "->", stroke: .5pt),
//   edge((1,0), (1,3), "->", stroke: .5pt),
//   edge((2,0), (0,3), "->", stroke: .5pt),
//   edge((2,0), (2,3), "->", stroke: .5pt),
//   edge((3,0), (2,3), "->", stroke: .5pt),
//   edge((4,0), (0,3), "->", stroke: .5pt),
//   edge((4,0), (1,3), "->", stroke: .5pt),
//   edge((4,0), (2,3), "->", stroke: .5pt),
//   edge((5,0), (1,3), "->", stroke: .5pt),
// )

// #diagram(
//   node-corner-radius: 4pt,
//   spacing: (2em, 1.5em),

//   // Event space elements with examples
//   node((0,0), [$e_1$: ItemAddedToCart]),
//   node((0,1), [$e_2$: ItemRemovedFromCart]),
//   node((0,2), [$e_3$: OrderPlaced]),
//   node((0,3), [$e_4$: PaymentReceived]),
//   node((0,4), [$e_5$: ItemShipped]),

//   // Model space elements (database tables)
//   node((3,0), [$m_1$: CartItems]),
//   node((3,1), [$m_2$: Orders]),
//   node((3,2), [$m_3$: Inventory]),
//   node((3,3), [$m_4$: Analytics]),

//   {
//     let tint(c) = (stroke: c, fill: rgb(..c.components().slice(0,3), 5%), inset: 8pt)
//     node(enclose: ((0,0), (0,4)), ..tint(blue), name: <e>)
//     node(enclose: ((3,0), (3,3)), ..tint(green), name: <m>)
//   },

//   // Complex mapping between events and models
//   edge((0,0), (3,0), "->", stroke: .5pt),
//   edge((0,0), (3,2), "->", stroke: .5pt),
//   edge((0,0), (3,3), "->", stroke: .5pt),
//   edge((0,1), (3,0), "->", stroke: .5pt),
//   edge((0,1), (3,2), "->", stroke: .5pt),
//   edge((0,1), (3,3), "->", stroke: .5pt),
//   edge((0,2), (3,0), "->", stroke: .5pt),
//   edge((0,2), (3,1), "->", stroke: .5pt),
//   edge((0,2), (3,3), "->", stroke: .5pt),
//   edge((0,3), (3,1), "->", stroke: .5pt),
//   edge((0,3), (3,3), "->", stroke: .5pt),
//   edge((0,4), (3,1), "->", stroke: .5pt),
//   edge((0,4), (3,2), "->", stroke: .5pt),
//   edge((0,4), (3,3), "->", stroke: .5pt),
// )

// template:



// #diagram(
//   node-corner-radius: 4pt,
//   node((0,0), $S a$),
//   node((1,0), $T b$),
//   node((0,1), $S a'$),
//   node((1,1), $T b'$),
//   edge((0,0), (1,0), "->", $f$),
//   edge((0,1), (1,1), "->", $f'$),
//   edge((0,0), (0,1), "->", $alpha$),
//   edge((1,0), (1,1), "->", $beta$),

//   node((2,0), $(a, b, f)$),
//   edge("->", text(0.8em, $(alpha, beta)$)),
//   node((2,1), $(a', b', f')$),

//   node((0,2), $S a$),
//   edge("->", $f$),
//   node((1,2), $T b$),

//   node((2,2), $(a, b, f)$),

//   {
//       let tint(c) = (stroke: c, fill: rgb(..c.components().slice(0,3), 5%), inset: 8pt)
//       node(enclose: ((0,0), (1,1)), ..tint(teal), name: <big>)
//       node(enclose: ((2,0), (2,1)), ..tint(teal), name: <tall>)
//       node(enclose: ((0,2), (1,2)), ..tint(green), name: <wide>)
//       node(enclose: ((2,2),), ..tint(green), name: <small>)
//   },

//   edge(<big>, <tall>, "<==>", stroke: teal + .75pt),
//   edge(<wide>, <small>, "<==>", stroke: green + .75pt),
//   edge(<big>, <wide>, "<=>", stroke: .75pt),
//   edge(<tall>, <small>, "<=>", stroke: .75pt),
// )