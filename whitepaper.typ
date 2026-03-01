#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#import "figures.typ": flow

// Whitepaper Configuration
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
    A Software Philosophy for Event Driven Architectures with Decoupled Infrastructure
  ]

  #v(0.5em)

  #text(12pt)[Conrad Mearns]
  // #text(11pt)[#datetime.today().display()]
]

#figure(flow)

#quote(block: true, attribution: [Edsger W. Dijkstra, 2000])[
  "The required techniques of effective reasoning are pretty formal, but as long as programming is done by people that don't master them, the software crisis will remain with us and will be considered an incurable disease."
  // https://www.cs.utexas.edu/~EWD/transcriptions/EWD13xx/EWD1305.html
]

= Abstract

// TODO: Write a whitepaper abstract that focuses on the philosophy and motivation,
// not the technical specification. What problem does DIZZY solve for the reader?
// Why should they care? What will they take away?

#set heading(numbering: "1a1a1a1a")

#pagebreak()

#outline(
  title: [Table of Contents],
  indent: auto,
)

#pagebreak()

= The Burden of Software Architecture is

== The Irreversibility of Poor Decisions

Everything in computing changes - it's just a matter of _when_ the change occurs. Our demands change, our platforms, capabilities, problems, fashions, and scale all change too.

We often see, especially in the most cursed software projects, that poor decisions will rear their heads to haunt us again later on.

Decisions that seemed either well intentioned, necessary, critical, or even genuinely brilliant can all turn into a curse when the conditions are right. And truly - I don't know what is worse: the number of projects people have retained as sunk costs, due to pride or politics - or the number of people who seemingly have no awareness of the curses they write. 

(Though, hindsight punishes the early architects all too often. 
There are too many such cases, when a developer succumbs to the pressures of the labor. When they break, integrity breaks too. We see mitigations, shortcuts, hacks and sloppy writing apparent as the evidence of such mental slips and burnouts.)

A decent Software Architecture is a ward against such curses. It is the draft of constraints that prevent the workarounds, the dirty hacks, and the "clever" tricks that inevitably cause confusion and harm later. A decent architecture promotes modularity for the sake of repairability.

Poor Architectures are those that attract curses rather than features. They are those whose structure itself is vile physarum of traces that span dozens of files, and couples itself to hardcoded strings, special conditionals, and ancient rituals of practices and patterns of by-gone developers.

We call this "Coupling"

// consider moving into 1.1

// TODO: What happens when your database choice, your deployment model, your
// programming language, and your business logic are all entangled?
// Give concrete examples of real-world pain:
// - "We can't migrate off Postgres because our business logic is in stored procedures"
// - "We can't rewrite the hot path in Rust because our types are Python-only"
// - "We can't split this monolith because the modules share a database"
// Each of these represents an irreversible decision that constrains all future decisions.


// Key points to develop:
// Everything in computing changes, it's just a matter of _when_.
// Many systems are implemented to solve for specific problems in software development,
// only to be usurped and made obsolete by advances in hardware development,
// or algorithms that change the objective completely.

// 

https://longnow.org/ideas/pace-layers/


== The False Dichotomies of Deployment Solutions

Every decision has the potential to become a permanent constraint.
Microservices on monoliths, AWS or Azure, Svelte or Vue or React...
The problem is not deciding which option is _correct_ - the choice itself is what become load-bearing.

There are many stories of those who find a themselves in some peril with bad architecture, and how they saved themselves with a large and heroic refactor.
These stories illustrate the fear and focus of Software Architecture. We can take direct comparisons against the prices others have paid for the wrong decision - and how long such mistakes took to fix.

Such is also the case for vendor lock-in - whether it be a Service maintained by another organization, or an entire cloud provider. 

// TODO: Argue that the real issue with modern architectures is not whether
// Monoliths or Microservices are better — it's that we force that decision
// upon ourselves and become shackled to its consequences for decades.
// The choice of deployment topology becomes load-bearing for the entire codebase,
// making it nearly impossible to change later.


// == The Same Data, Described a Dozen Times
// TODO: The same domain primitives (a user, an order, a transaction) get
// redefined in Pydantic, SQL Alchemy, Protobuf, Rust structs, JSON schemas --
// each slightly different, each drifting out of sync. This isn't just tedious;
// it's a breeding ground for subtle bugs. And the underlying data types are
// often wrong too -- doubles for currency, 64-bit integers for 8-bit port numbers.
// The tooling doesn't prevent this; it multiplies it.
// (See transcript 34:18 - 35:36)

== Applications as Islands

The isolation of data within applications hurts both consumers and businesses.

As a consumer, the data we generate from our photos, health integrations, recipes, liked posts, videos, journal entries etc are effectively useless to us. 
Power users of information cannot access their own data from the Walled Gardens of the internet without using complex and bespoke API's, and cannot integrate their applications together on their own.

Similarly, even within a single business teams struggle to share data effectively.
The interfaces for which data is shared requires bespoke translations and jury-rigged events.

// https://maggieappleton.com/garden-history
// https://veilid.com/Launch-Slides-Veilid.pdf

== The Map Grossly Mislabels the Territory

The Map is Not the Territory. The map usually hardly comes close to the territory.

When leadership and business stakeholders make decisions about their software, it's critical that they understand the system. We still rely on slide decks, books of documentation, and tribal knowledge over code in many instance.

Why? Because the code teaches us nothing about how the code works, why the code works, and what decisions led to the code being created.


// == Most Architecture is Bespoke, Vernacular, or simple Mimicry

// Software Architecture is largely vernacular because we simply don't have the tools to define and discuss the larger and larger systems we consider builder. Vernacular, because even though many Developers lack formal training, many can still write better software than industry "professionals" given certain tasks. They learn through communities and helpful eyes how to build systems that last - systems that scale - and systems that solve problems.

// Without the journeyman approach to pair programming, many can only rely on mimicry - which is typically enough. Copy and Paste is often joked to be the only necessary keyboard shortcuts needed to write most software. If you're goal is to pick [LAMP | MEAN | WISA] Stack, then you likely can get by with a lot of copy and paste.

// Mimicry fails when we cannot copy someone else's solution to our problem.

// Vernacular Architecture fails when the practices and rituals of building no longer align with shift in culture, scale, and practices required in our solutions.

// Every so often, I am reminded that Roller Coatser Tycoon was designed and compiled with MS Macro Assembler V6.11c.

// Few today would attempt a similar feat, simply because the language of Assembly does not align with the language of high performance game design, or roller coasters.

// Today, many would choose an efficient language intended to solve data problems, access and allocation problems, or visualization problems. Like C, or Rust.

// Some - like NaughtyDog - would choose a LISP-Like language to build their DSL's within their target language itself.

// A solution like this is vernacular still - but bespoke and artful too. The problem is not so much an obstacle, but a conversation.


== Scaling Software without Adequate Support

There will always be a natural limit to the number of experienced software developers who can take on the craft of design and implementation, as well as the discussion and delegation of work, and also ensure timeliness in the execution of a project.

The Standish CHAOS study finds that only 31% of software projects are successful,
52% are over budget or miss missed deadlines,
and that 19% of projects fail completely.

https://www.standishgroup.com/sample_research_files/CHAOSReport2015-Final.pdf

Melvin Conway, states that systems designed by organizations are constrained to mirror the communication structures of those organizations.

As software begins, it's design only must necessitate the communication structure of the individual. As software grows, and it's design becomes becomes an argument of the individuals and the many. Boundaries are built around convince and practicality, rather than sustainability, maintainability.

As software scales to serve more, and it's features become uncountable, and the ability for developers, stakeholders, and leadership cannot retain the necessary mental models to make accurate predictions of change.

DIZZY's intent on enforcing rigid constraints is a philosophical and practical choice to shape and guide the communication flow of users, developers, stakeholders, data and logical flow.

= Guiding Principles

// TODO: Introduce the philosophical foundation. These aren't just technical
// patterns — they're design values that inform every decision in DIZZY.
//   

== Deferring Decisions

The best decision is often the one you don't have to make yet.

DIZZY is a a philosophy of  software architecture that emphasizes the deference of choice.

Which databases, which message brokers, which languages and whatever other foundations that required are deferred until they are needed.

DIZZY prefers to answer and understand the business problems to solve from first principals first - and let the tradeoff space be explored at a different layer of the architecture.

// DIZZY is designed so that infrastructure choices (which database, which
// message broker, monolith vs. microservice, which language for which component)
// can be deferred until you have enough information to choose well —
// and reversed when that information changes.

== Architecting for Reversibility

Reversibility is about maintaining the freedom to respond to new information. 

- What if we could swap databases in and out of our system as easily as a feature flag?
- What if our database vendor contract has to be abandoned?
- What if we chose the wrong query model for our data?
- What if the deployment paradigm is generating too high of an operational cost?

DIZZY's goal is to empower business to adapt and utilize the best conditions for computation without vendor lock-in.


== Support (Almost) Any Programming Language

Truly modular software should work across disciplines, languages, networks, and hardware. DIZZY achieves language independence through language-agnostic schemas and code generation.
By generating interfaces and protocols for the DIZZY Processes, the bare minimum of guarantees can be made to show what components are capable of what tasks.

// The domain model is defined once; implementations can be generated for
// any target language. A Python policy can emit a command handled by a Rust procedure.


== Separate Data from Process

DIZZY is intentionally a mostly functional paradigm. Data (commands, events, models, and query IO) and processes (procedures, policies, projections, and queriers) are explicitly  separated. This is fundamentally different form the traditional Object Oriented Paradigm that traditional DDD is based upon.

This separation is what enables various components of the full DIZZY system to be deployed independently.


== Infrastructure _from_ Code

// TODO: Expand on the idea of #strike[Infrastructure as Code] -> Infrastructure _from_ Code.
// Rather than separately defining infrastructure and hoping it matches your code,

DIZZY derives infrastructure requirements separate from the domain model.

Just as Programming Languages translate human intent to machine code - so too should DIZZY translate business intent to infrastructure. Automatically, with optimizations for infrastructure that can be refined out of phase with business needs - just as GCC can improve compilation and optimizations without requiring changes to C.

DIZZY calls this an Interstitial Infrastructure. The goal is to treat Interstitial Infrastructure as a compilation problem.

Infrastructure decisions are the final step in a DIZZY deployment, and enable DIZZY to be built as either a monolith, microservices, or something in between. 

Commands, Events, and Models are data. They can be communicated over any number or combinations of message passing channels, such as ZeroMQ, Kafka, HTTP, WebSocket, gRPC, etc.

The deployment of Processes support any potential target as long as it can satisfy channel connectivity requirements.

== Event Driven Eventual Consistency

Events are not records that are ever migrated - they are records of past actions and outcomes. As such, the past cannot be altered - events must be immutable.

Schema evolution may still be a consideration for Queriers and databases, but not for events.
Instead, any records of history that are intended to be augmented must be done so by the inclusion of additional events. Events cannot be deleted, but an event can notify that they're information is deprecated.

The goal from this constraint is to enable Eventual Consistency for long horizons.
As well as data reprocessing and auditing.


== Consistent Communication

The rigidity of the DIZZY schema is a constraint to enable naive parallelism for both machines, and the laborers who must adapt and add behavior into their system.

Every component has clearly defined inputs and outputs, every dependency chain is already known - and can be agreed on and tested before deployment.

Processes can be horizontally scaled with the same minimal effort as serverless.

And work can scale according to the number of DIZZY flow segments that require change - a countable figure for a codebase, rather than someone arbitrarily derived from an "Agile" backlog.


= The DIZZY Architecture at a Glance

#figure(flow)

This is intended to be a very high level, and ill-thorough description of the DIZZY architecture. See the Specification for more detail.

DIZZY can be thought of as an intersection of two spirals or loops.

Firstly, a reactivity loop. Where Commands trigger Procedures, which emit Events that trigger Policies, that emit Commands.

Secondly, a data retrieval and optimization loop. Where Events are projected to Models (databases), which can be queried by Queriers on Query Inputs to return Query Outputs to Procedures and Policies.

The reactivity loop enables processing, algorithms, and business logic to react and change to new information.

The data loop enables change information (Events) to be recorded in highly specialized formats specifically for the purposes of efficient retrieval by Procedures and Policies.

== Commands as Intent

Commands represent what users _want_ to happen.
They are ephemeral expressions of intent — not records of fact.
This distinction matters because intent can be rejected, retried, or rerouted, while facts cannot.

commands can be repeated, or contain PII, and other data that is meant to be ephemeral

== Events as Truth

Events are the single source of truth. Everything else — every model, every view, every report — is derived from events. The same event stream can power multiple databases with completely different schemas, each optimized for different queries.

Events are immutable logs.

Because events capture _what happened_ independently of any particular
database schema, the same event stream can power multiple databases
with completely different schemas — each optimized for different queries.

Migrations become "build a new projection and cut over" rather than "transform the existing database in place and pray."

This means:
- You can build a new database with an alternative schema from the same
  events, without migrating the old one. Stand up the new projection,
  replay events, and you have a new view of the same data.
- Migrations become "build a new projection and cut over" rather than
  "transform the existing database in place and pray."
- Different teams or services can maintain their own models from the
  shared event stream — coordination happens through the event contract,
  not through shared database access.
- Federated subnetworks can subscribe to relevant event subsets and
  build local models suited to their own query patterns, without
  coupling to the producer's schema choices.

The event stream is the canonical representation. Every database is
just a cached, queryable projection of that truth — disposable and
rebuildable by design.


=== Procedures: Command Handlers

Procedures handle commands and emit events. They are not pure functions — they can query projections — but any external systems they connect to must either be modelled as another DIZZY component or have their effects logged within events. This is what makes procedures portable across languages and deployable in any topology.


== How It's Made: The Context Object - Callbacks, Queries, and Injection

Implementations of Procedures and Policies are just functions, but they don't have return types.
Data is forwarded via Emitters, which are functions injected via a context object in the argument list of the function.

This dependency injection is what enables Process Components to be decoupled from the infrastructure that runs them.

The Emitter callbacks map to channel routes such as gRPC, Kafka, ZeroMQ, or can even be ignored.


== Projections as the Bridge from Events to Models

Unlike traditional Domain Driven Design Event Sourcing, models are treated as ephemeral and require events to be built from.

This perspective allows the concept of "Aggregates" to be dropped.
(Aggregates are a standard way of bridging Event Driven Architecture to Object Oriented Design)

Events record the history of all application state changes, but cannot be queried efficiently. To address this, a Projection is trigged per event to update a specific set of model elements.

For example - in traditional EDA DDD, you may have a hard time using Aggregates or Dynamic Consistency Boundaries to represent an event such as "Author Published a Book" - as multiple tables must be adapted.


== Models as Disposable Views

Models are derived and rebuildable.
They exist to make queries fast, not to be the source of truth.
You can have as many models as you have questions to answer,
backed by whatever database technology makes sense for each question.

Connect to the Projection concept as the bridge from events to models.


= From Description to Deployment: The Generation Pipeline

Feature file -> def -> gen_def -> gen_impl -> impl

Change propagation


= Existing Disciplines, New Composition

DIZZY is nothing new.

// TODO: DIZZY is not inventing new computer science. It composes existing,
// proven disciplines into a coherent whole. Acknowledge the lineage and
// explain how DIZZY brings them together:

- Command Query Responsibility Separation (CQRS)
- Command Queuing
- Event Storming (for domain discovery)
- Event Sourcing (for truth)
- Functional Programming (for testable logic)
- Dependency Injection (for decoupling)
- Infrastructure as Code (for deployment)

// == The Spectrum from Structured Logging to Event Sourcing
// TODO: Structured logging is for more than just debugging.
// There is a spectrum from Change Data Capture <-> Event Sourcing.
// Many teams are already halfway to event sourcing without knowing it.
// Help readers see the continuum and understand where DIZZY sits on it.

// == Event Storming as the On-Ramp
// TODO: Event Storming is a collaborative workshop technique where
// domain experts and developers map out a system using sticky notes.
// Orange stickies for events ("OrderPlaced"), blue for commands
// ("PlaceOrder"), lilac for policies ("When order placed, reserve inventory"),
// and pink for procedures (the logic that handles a command).
//
// The key insight: these sticky notes map directly to DIZZY components.
// The orange stickies become your event definitions. The blue stickies
// become your command definitions. The lilac stickies become policies.
// The pink stickies become procedures.
//
// This means an Event Storming session doesn't just produce a wall of
// sticky notes that gets photographed and forgotten — it produces the
// skeleton of a feature definition. The gap between "we understand the
// domain" and "we have a working system" shrinks dramatically.
//
// For teams unfamiliar with Event Storming, see [reference to Brandolini
// or similar]. The practice is valuable independent of DIZZY, but DIZZY
// gives the output a direct path to implementation.


// = A Worked Example
// TODO: This is critical. Walk through a complete, concrete example at a
// conceptual level. Something simple enough to follow but rich enough to
// show the architecture working. Candidates:
// - A todo list app (simplest, most familiar)
// - A shopping cart (good for showing projections and multiple models)
// - An ETL pipeline (shows the non-web-app applicability)
//
// Show:
// 1. The domain events and commands (what happened, what we want to happen)
// 2. A procedure handling a command and emitting events
// 3. A policy reacting to an event and issuing a new command
// 4. A projection building a model from events
// 5. A query reading from that model
// 6. How swapping the database or deployment model doesn't touch any of the above


// = Organizing Work: From Architecture to Work Breakdown
// TODO: One of DIZZY's underappreciated benefits is how it structures
// the work of building software, not just the software itself.


// == Countable Flows, Not Spaghetti Traces
// TODO: In a DIZZY system, the flow of execution is _enumerable_.
// You can list every command, every procedure, every event, every policy.
// The feature definition is a complete map of how data and intent move
// through the system. Contrast this with traditional codebases where
// understanding "what happens when a user clicks X" requires tracing
// through layers of implicit function calls, middleware, and side effects.
//
// In DIZZY, the answer is always: "Command A is handled by Procedure B,
// which emits Events C and D, which trigger Policies E and F."
// The flow is a finite, countable set — not an emergent property of
// tangled code paths.


// == Components as Work Units
// TODO: Once a feature definition exists, the work items write themselves.
// Each procedure, policy, projection, and query implementation is a
// discrete, bounded unit of work with:
// - A clear input type (the command or event it handles)
// - A clear output contract (the events or commands it emits)
// - A clear context (which queries it can access)
// - No implicit dependencies on other implementations
//
// This means work can be parallelized naturally. Two developers (or agents)
// can implement different procedures for the same feature simultaneously,
// because the schema contracts define the boundaries.


// == The Technical Lead's View
// TODO: For a technical lead, the feature definition serves as a
// high-level map of the system. When a change request comes in, the lead
// can identify exactly which DIZZY components are affected:
// - Which commands need to change or be added?
// - Which events are new?
// - Which procedures and policies need updating?
// - Which projections and models are impacted?
//
// This produces a small, explicit set of work items — not a vague
// "go figure out what needs to change in the codebase." The waterfall-like
// structure of definition -> generation -> implementation provides
// a natural ordering, while the independence of components within each
// stage enables parallel execution.


// == Agents and Automated Workers
// TODO: The clear boundaries that help human teams also help AI agents
// and automated tools. An agent given a procedure to implement has:
// - The exact input type (generated from schema)
// - The exact output contract (which events to emit)
// - The exact query interface (what it can read)
// - No need to understand the rest of the system
//
// This is the minimal context needed to do useful work. The feature
// definition acts as a coordination protocol — agents don't need to
// understand the whole system, just their component's contract.


// = Testing by Construction
// == Chaos Testing



// = Addressing the Hard Problems
// TODO: Be honest about the challenges. Event sourcing has well-known
// difficulties. Addressing them head-on builds credibility.


// == Schema Evolution and Event Versioning
// TODO: Events are immutable, but schemas evolve. How does DIZZY handle
// adding fields, renaming events, or changing event semantics over time?


// == Eventual Consistency
// TODO: Models are eventually consistent with the event store. What does
// this mean in practice? What are the failure modes? When is eventual
// consistency acceptable, and when do you need stronger guarantees?
// How does DIZZY help teams reason about consistency boundaries?


// == Event Store Growth and Snapshots
// TODO: The event store grows without bound. What strategies exist for
// managing this? Snapshotting, compaction, archival. How does DIZZY's
// projection-rebuilding model interact with these strategies?


// == Ordering and Distribution
// TODO: When events are processed across distributed nodes, ordering
// guarantees become complex. What ordering guarantees does DIZZY provide?
// What does it leave to the infrastructure? How should teams reason about
// causal ordering vs. total ordering?


// == Change Propagation: The Arrows Point Backwards
// TODO: When you modify a component (add a field to a command, change an event),
// the ripple effects propagate backwards through the dependency graph. DIZZY
// tracks these relationships so you get an explicit list of everything affected.
// "The arrows propagate backwards when you add code elements or functionalities
// to your feature. And that's where that like high relational aspect comes in."
// This is the concrete mechanism behind "making changes responsibly."
// (See transcript 42:12 - 42:43)

// == Sagas and Long-Running Processes
// TODO: Some business processes span multiple commands and events over time.
// Durable execution
// Show an example where Event Started - Event Ended - Event Failed
// Entity ID's

= Conclusion

// TODO: In a future where writing software is 10000x cheaper, how do we
// structure the work? DIZZY's answer: define the domain precisely,
// generate the boilerplate, keep the logic portable, and never let an
// infrastructure choice become a prison.

For the formal specification of DIZZY components, schemas, and code generation pipeline, see the companion _DIZZY Specification_.



// = References
// Normative
// [RFC2119] Bradner, S., "Key words for use in RFCs to Indicate Requirement Levels", BCP 14, RFC 2119, March 1997.
// [LinkML] "Linked Data Modeling Language", https://linkml.io/
// [CQRS] Fowler, M., "CQRS", https://martinfowler.com/bliki/CQRS.html
// [EventSourcing] Fowler, M., "Event Sourcing", https://martinfowler.com/eaaDev/EventSourcing.html

// Informative
// [DDD] Evans, E., "Domain-Driven Design", Addison-Wesley, 2003.
// [CosmicPython] Percival, H. and Gregory, B., "Architecture Patterns with Python", O'Reilly, 2020. https://www.cosmicpython.com/
// [Conway] Conway, M., "How Do Committees Invent?", 1968.
// [Dijkstra] Dijkstra, E., "The Humble Programmer", ACM Turing Lecture, 1972.
// [Feathers] Feathers, M., "Working Effectively with Legacy Code", Prentice Hall, 2004.
// [Kleppmann] Kleppmann, M., "Designing Data-Intensive Applications", O'Reilly, 2017.
