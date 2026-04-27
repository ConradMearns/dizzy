#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#import "figures.typ": flow, c_map, e_map, d_map, y_map, j_map, m_map, Q_map, pipeline

// Whitepaper Configuration
#set page(
  paper: "us-letter",
  margin: (x: 1in, y: 1in),
  numbering: "1 / 1",
)

#set text(
  size: 12pt,
)

#set par(
  justify: true,
  // leading: 0.75em,
  spacing: 1.2em,
  // first-line-indent: (amount: 1.5em, all: true),
)


// Title
#align(center)[
  #text(24pt, weight: "bold")[D I Z Z Y]

  #text(12pt, weight: "bold")[
    A Philosophy and Schema System for the Development of Certain Event Driven Architectures with Deferred Interstitial Infrastructure
  ]

  // #v(0.5em)

  #text(12pt)[Conrad Mearns]
  
  #text(11pt)[#datetime.today().display()]
]


#figure(box[
  #set text(size: 0.9em)
  #flow
])

#quote(block: true, attribution: [Edsger W. Dijkstra, 2000])[
  "The required techniques of effective reasoning are pretty formal, but as long as programming is done by people that don't master them, the software crisis will remain with us and will be considered an incurable disease."
  // https://www.cs.utexas.edu/~EWD/transcriptions/EWD13xx/EWD1305.html
]

#v(3em)

= Abstract
#v(1em)

Software projects fail in predictable ways.
Infrastructure decisions made under pressure harden into permanent constraints.
Domain logic becomes inseparable from the languages that encode it.
Data and services become inseparable from the databases that serve.
The vocabulary used to describe a system drifts from the code that implements with every commit, requiring continuous and careful maintenance.
DIZZY is a philosophy for building event-driven software systems that keeps domain logic, data contracts and infrastructure permanently and deliberately separate.
It draws on established practices -
Command Query Responsibility Separation, Event Sourcing, and Domain-Driven Design - 
and composes them into a coherent discipline:
define the domain in a language-agnostic schema, generate typed contracts for data and code, and let infrastructure decisions follow rather than lead.
This paper is written for software practitioners and technical-decision-makers who have felt these problems firsthand.
It makes the case for why the separations DIZZY enforces matter, 
introduces a system of eight program components that illustrates the philosophy,
and describes a software generation pipeline that closes the gap between domain discovery and working, scalable software.

// For formal schemas, component specifications, and code generation details, see the companion _DIZZY Specification_ paper.


// #set heading(numbering: "1a1a1a1a")
// #set heading(numbering: "1.a.1.a.1.")
#set heading(numbering: "1.")

// Level 1: generous breathing room above, compact below
#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  block(above: 2em, below: 0.9em, it)
}

// Level 2: clear separation above, tight below
#show heading.where(level: 2): set block(above: 3.6em, below: 1.6em)

// Level 3+: lighter separation
#show heading.where(level: 3): set block(above: 1.8em, below: 1.2em)


#pagebreak()

#outline(
  title: [Table of Contents],
  indent: auto,
)

#pagebreak()

= The Burden of Software Architecture is...

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

// https://longnow.org/ideas/pace-layers/


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
and that 19% of projects fail completely. @standish2015

Melvin Conway states that systems designed by organizations are constrained to mirror the communication structures of those organizations. @conway1968 The Inverse Conway Maneuver turns this into a design tool: deliberately shape team boundaries and system architecture together, so that communication structures produce the architecture you want rather than constrain it. @skelton2019

As software begins, it's design only must necessitate the communication structure of the individual. As software grows, and it's design becomes becomes an argument of the individuals and the many. Boundaries are built around convince and practicality, rather than sustainability, maintainability.

As software scales to serve more, and it's features become uncountable, and the ability for developers, stakeholders, and leadership cannot retain the necessary mental models to make accurate predictions of change.


= Software Architectures Should... 

...deliberately shape the communication structures of the organizations that build them.

The Inverse Conway Maneuver says: if your system is going to mirror your organization anyway, design it to mirror the organization you _want_. 
DIZZY applies this as an architecture constraint. 
Its rigid component boundaries are deliberate seams that define where teams own work independently and where they must coordinate.


// (Guiding Principles)

// TODO: Introduce the philosophical foundation. These aren't just technical
// patterns — they're design values that inform every decision in DIZZY.
//

== Defer Deployment Decisions

The best decision is often the one you don't have to make yet.

DIZZY is a a philosophy of  software architecture that emphasizes the deference of choice.

Which databases, which message brokers, which languages and whatever other foundations that required are deferred until they are needed.

DIZZY prefers to answer and understand the business problems to solve from first principals first - and let the tradeoff space be explored at a different layer of the architecture.

// DIZZY is designed so that infrastructure choices (which database, which
// message broker, monolith vs. microservice, which language for which component)
// can be deferred until you have enough information to choose well —
// and reversed when that information changes.

== Architect for Reversibility

Reversibility is about maintaining the freedom to respond to new information.

DIZZY should not only empower modularization of our system, it should naturally enable A/B testing and hotswapping so that reversing decisions becomes a standard practice, rather than a hail mary.

Consider the questions that haunt every long-lived system.
What if the database vendor raises prices or discontinues the product?
What if the chosen query model turns out to be wrong for the data?
What if the deployment topology is generating too high of an operational cost?

In most architectures these are existential questions — 
answering them requires rewriting code that should never have known about infrastructure in the first place.
// DIZZY's goal is to make them routine.
// Because domain logic never knows which database backs its Models or which channel carries its Events,
// swapping one for another is a deployment concern, not a development one.


== Support (Almost) Any Programming Language

Truly modular software should work across disciplines, languages, networks, and hardware.
DIZZY achieves language independence through language-agnostic schemas and code generation.
By generating interfaces and protocols for the DIZZY Processes,
the bare minimum of guarantees can be made to show what components are capable of what tasks.

// The domain model is defined once; implementations can be generated for
// any target language. A Python policy can emit a command handled by a Rust procedure.


== Separate Data from Process

DIZZY is intentionally a mostly functional paradigm. Data (commands, events, models, and query IO) and processes (procedures, policies, projections, and queriers) are explicitly  separated. This is fundamentally different form the traditional Object Oriented Paradigm that traditional DDD is based upon.

This separation is what enables various components of the full DIZZY system to be deployed independently.


== Derive Infrastructure _from_ Code

// TODO: Expand on the idea of #strike[Infrastructure as Code] -> Infrastructure _from_ Code.
// Rather than separately defining infrastructure and hoping it matches your code,
// introduce as "interstitial architecture"

DIZZY derives infrastructure requirements separate from the domain model.

Just as Programming Languages translate human intent to machine code - so too should DIZZY translate business intent to infrastructure. Automatically, with optimizations for infrastructure that can be refined out of phase with business needs - just as GCC can improve compilation and optimizations without requiring changes to C.

DIZZY calls this an Interstitial Infrastructure. The goal is to treat Interstitial Infrastructure as a compilation problem.

Infrastructure decisions are the final step in a DIZZY deployment, and enable DIZZY to be built as either a monolith, microservices, or something in between.

Commands, Events, and Models are data. They can be communicated over any number or combinations of message passing channels, such as ZeroMQ, Kafka, HTTP, WebSocket, gRPC, etc.

The deployment of Processes support any potential target as long as it can satisfy channel connectivity requirements.

// TODO does this belong?
// == Event Driven Eventual Consistency

// Events are not records that are ever migrated - they are records of past actions and outcomes. As such, the past cannot be altered - events must be immutable.

// Schema evolution may still be a consideration for Queriers and databases, but not for events.
// Instead, any records of history that are intended to be augmented must be done so by the inclusion of additional events. Events cannot be deleted, but an event can notify that they're information is deprecated.

// The goal from this constraint is to enable Eventual Consistency for long horizons.
// As well as data reprocessing and auditing.


// This is not coherent
// == Consistent Communication

// The rigidity of the DIZZY schema is a constraint to enable naive parallelism for both machines, and the laborers who must adapt and add behavior into their system.

// Every component has clearly defined inputs and outputs, every dependency chain is already known - and can be agreed on and tested before deployment.

// Processes can be horizontally scaled with the same minimal effort as serverless.

// And work can scale according to the number of DIZZY flow segments that require change - a countable figure for a codebase, rather than someone arbitrarily derived from an "Agile" backlog.

= DIZZY Solves this Using...

... four Data Contracts and four Program Processes.

#let link_flow = diagram(
  spacing: (1.5em, 1.5em),

  node((0,0),       link(<commands>)[$c$],    name: <c>),
  node((0,-1),      link(<policies>)[$y$],    name: <y>),
  node((0,1),       link(<procedures>)[$d$],  name: <d>),
  node((-1,0),      link(<events>)[$e$],      name: <e>),
  node((1,0),       link(<queries>)[$q$],     name: <q>),
  node((0,-2),      link(<models>)[$m$],      name: <m>),
  node((-1.3,-1.3), link(<projections>)[$j$], name: <j>),
  node(( 1.3,-1.3), link(<queries>)[$Q$],     name: <Q>),

  edge(<c>, <d>,  bend: 0deg, "->"),
  edge(<d>, <e>,  bend: 0deg, "->"),
  edge(<e>, <y>,  bend: 0deg, "->"),
  edge(<y>, <c>,  bend: 0deg, "->"),
  edge(<q>, <y>,  bend: 0deg, "<-->"),
  edge(<q>, <d>,  bend: 0deg, "<-->"),
  edge(<e>, <j>,  bend: 15deg, "->"),
  edge(<j>, <m>,  bend: 15deg, "->"),
  edge(<m>, <Q>,  bend: 15deg, "<-->"),
  edge(<Q>, <q>,  bend: 15deg, "<-->"),

)



#grid(
columns: (auto, auto),
column-gutter: 2em,
align: horizon,
figure(link_flow),
[
DIZZY is Data Oriented and Functional.
We explicitly outline each data contract component and each program process component separately. 
// TODO figure captions?
The diagram to the left shows the general data flow between each DIZZY data and process component. 
Solid arrows show message passing,
dashed arrows show call and response communication.
],
)

#v(2em)

#figure(
table(
  columns: (auto, auto, auto),
  align: (center, left, left),
  table.header([*Symbol*], [*Component*], [*Role*]),
  $c$, [Command],    [Represent intent - what a user or policy wants to happen],
  $d$, [Procedure],  [Handles a Command and may emit Events],
  $e$, [Event],      [Immutable record of facts - the source of truth],
  $y$, [Policy],     [Reacts to an Event and may emit Commands],
  $j$, [Projection], [Listens for Events and updates Models],
  $m$, [Model],      [Queryable view of state, derived from Events],
  $Q$, [Querier],    [Executes a Query against a Model],
  $q$, [Query],      [Typed contract for a call and its response],
))

// This is intended to be a very high level description of the DIZZY architecture.
// See the Specification for more detail.

DIZZY is therefor comprised of two dataflow loops.

Firstly, a reactivity loop; Where Commands trigger Procedures, which emit Events that trigger Policies, that emit Commands.
Secondly, a data retrieval loop; Where Event are projected to Models (databases), which can be queried by Procedures and Policies.
The reactivity loop enables processing, algorithms, and business logic to react and change to new information. The retrieval loop enables database decoupling while providing efficient value lookups.

As an example, suppose we processing financial transactions. 
Each Events record debits and credits as the source of truth.
Transactions are initiated by users and the data is represented by a Command.
The Transaction Command triggers a procedure, 
which may need to Query for the normalized account balance to know whether to succeed or fail.
Thus, each debit and credit Event must also trigger a projection to keep this normalized account balance up-to-date in a Model.

// The data loop enables change information (Events) to be recorded in highly specialized formats specifically for the purposes of efficient retrieval by Procedures and Policies.

== Commands ( $c$ ) that Represent Intent <commands>

#grid(
columns: (auto, 1fr),
column-gutter: 2em,
align: horizon,
figure(c_map),
[
#v(1em)

Commands represent expressions of intent, what users _want_ to happen.
They are ephemeral - not records of fact, and thus may be fire-and-forget and discarded.
This distinction matters: intent can be rejected, retried, or rerouted. 

Facts cannot.

Because Commands are ephemeral and may be discarded without consequence, 
the are useful for isolating the transmission of data must abide to different legal and business policies -
such as personally identifiable information.

Whether this information is recorded as an immutable fact is up to the design of Procedures and Events.

A policy may emit any number of commands, of any command sub-types.
Therefore policies and commands are one-to-many; several policies may emit the same command types.

// TODO: Can a Command be handled by more than one Procedure, or is it always 1:1?
A Command may trigger many Procedures. This relation is typically best assigned at the Procedure definition.

// TODO: Is a rejected Command recorded anywhere — does rejection itself become an Event?
])

Commands express intent, and can be carefully designed to handle cases where lossy systems where retries are standard practice. See Durable Execution // TODO make a link!

== Procedures ( $d$ ) that Perform the Critical Work <procedures>

#grid(
columns: (auto, 1fr),
column-gutter: 2em,
align: horizon,
figure(d_map),
[
#v(1em)

Procedures handle #link(<commands>)[Commands] and may emit #link(<events>)[Events].
They are the site of critical work in a DIZZY system — the place where intent meets consequence.

Procedures are not required to be pure functions. They may query #link(<models>)[Models] to inform their decisions.
But any external system a Procedure touches must either be modelled as another DIZZY component,
or its effects must be recorded in Events.
This constraint is what makes Procedures portable across languages and deployable in any topology:
their behavior is fully described by what they receive, what they query, and what they emit.

When a Procedure performs IO or causes effects in the world, it should emit Events
to record the attempt, progress, and result.
An effect that is not recorded in an Event is invisible to the rest of the system —
and invisible effects undermine the audit guarantee that Events provide.

// TODO: Can a single Command trigger multiple Procedures, or is the relationship always 1:1?
// TODO: Are Procedures allowed to call each other directly, or must all coordination
// flow through Commands and Events?
])

== Events ( $e$ ) that are the Source of Truth <events>

#grid(
columns: (auto, 1fr),
column-gutter: 2em,
align: horizon,
figure(e_map),
[
#v(1em)
Events are the single source of truth.
Everything else — every model, every view, every report — must be derived from events.
Events are immutable records of what _happened_: once written, they cannot be altered or deleted.

Because events capture what happened independently of any particular database schema,
the same event stream can power multiple databases with completely different schemas —
each optimized for different queries.
Different teams or services can maintain their own models from the shared event stream;
coordination happens through the event contract, not through shared database access.

This also makes migrations tractable.
Rather than transforming a live database in place, a new Model can be built alongside the old one
from the same event history, and cut over when ready.
If the new schema turns out to be wrong, the events remain — and the next attempt costs only a new Projection.

The event stream is the canonical representation.
Every database is just a cached, queryable projection of that truth — disposable and rebuildable by design.
],
)




== Policies ( $y$ ) that React and Initiate <policies>

#grid(
columns: (auto, 1fr),
column-gutter: 2em,
align: horizon,
figure(y_map),
[
#v(1em)
Policies are the reactive logic of a DIZZY system.
Where Procedures respond to intent, Policies respond to fact:
they are triggered by #link(<events>)[Events] that have already occurred,
and they may emit #link(<commands>)[Commands] in response.
A Policy asks: _given that this happened, what should happen next?_

This distinction is not incidental.
Because a Policy reacts to an Event — an immutable, already-happened fact —
it is inherently decoupled from the Procedure that produced it.
The Policy does not know or care how the Event came to exist.
It knows only what happened, and responds accordingly.

Policies may also query #link(<models>)[Models] to inform their decisions,
allowing the system to react differently depending on current state.
A Policy that always emits the same Command is a simple rule.
A Policy that queries a Model first is a conditional one — but the conditionality
lives in the Policy, not scattered through unrelated code.

// TODO: Can a single Policy react to multiple Event types, or is it always bound to one?
// TODO: Can a Policy emit multiple Commands, or at most one per triggering Event?
// TODO: What is the relationship between Policies and long-running processes / sagas?
// A saga that spans multiple Events over time seems like it would require Policy state —
// how does DIZZY handle that without violating the stateless reactive model?
])

== Projections ( $j$ ) that Map Events to Models <projections>

#grid(
columns: (auto, 1fr),
column-gutter: 2em,
align: horizon,
figure(j_map),
[
#v(1em)

#link(<events>)[Events] are the authoritative record of everything that has happened,
but they are not optimized for retrieval.
A Projection solves this: it listens for specific Events and updates one or more
#link(<models>)[Models] in response,
translating the language of facts into the language of efficient queries.

This approach eliminates the need for Aggregates — the construct traditional Domain-Driven Design
uses to bridge event-driven architecture to object-oriented state.
Because Models in DIZZY are treated as ephemeral and rebuildable from Events,
there is no need for an object that holds and manages state on behalf of a set of related entities.

The practical consequence is significant: if a Model turns out to be wrong for its purpose,
it can be replaced without touching the event history.
Write a new Projection, replay the Events, and a new Model emerges from the same source of truth.

// TODO: Is a Projection always bound to a specific set of Event types, or can it subscribe broadly?
// TODO: What is the failure model — if a Projection crashes mid-replay, how does it recover?
// TODO: Can multiple Projections write to the same Model, or is it always 1:1?
])

== Models ( $m$ ) that Serve Data for Queries <models>

#grid(
columns: (auto, 1fr),
column-gutter: 2em,
align: horizon,
figure(m_map),
[
#v(1em)

A Model is a schema for queryable state, backed by a database chosen for the specific access
patterns that Model must serve.
Models are derived from #link(<events>)[Events] via #link(<projections>)[Projections],
and are rebuildable on demand.

Models exist to make queries fast, not to be the source of truth.
You can have as many Models as you have distinct questions to answer —
each backed by whatever database technology best suits those questions.
A time-series store for metrics, a graph database for relationships, a search index for full-text:
all derived from the same Event stream.

// TODO: Should a Model ever be written to by anything other than Projections?
// TODO: Is there a constraint on how many Projections can write to a single Model?
])


== Queries ( $q$ ) and Queriers ( $Q$ ) for efficient computation <queries> //<queriers>

#grid(
columns: (auto, 1fr),
column-gutter: 2em,
align: horizon,
figure(Q_map),
[
#v(1em)

Querying can often be the most confused aspect of software engineering,
because the retrieval of information tends to occur at the confluence of database requirements, data shape requirements, and downstream alignment.

DIZZY systems demand the distinction between database drivers, data contracts, and the program that 'executes' the query.
We call the data contracts Queries, which are typically represented as a tuple of Input and Output, or Call and Response.
The process that uses program code to execute the query is what we call the Querier.
])

= How to Structure Software Development Workflows with DIZZY

DIZZY is a complete philosophy for software development;
it covers the flow from ideation, vibe-checking, workshopping, integration, to production deployment. 
This whitepaper will cover the workshopping method, and less of vibe-checking. 
From there, it will show the tooling to illustrate what steps can be automated algorithmically and which need intervention.

// Most DIZZY implementations rely on Queues for scalable implementation.

// == Studying Vibes and Experiments
== Workshopping


#let es(variant, label, size: 25pt, text_size: 12pt) = {
    let color = if variant == "c" { rgb("#4ab6d9") } 
    else if variant == "e" { rgb("#abcc51") }
    else if variant == "d" { rgb("#f39a4f") }
    else if variant == "y" { rgb("#eb6092") }
    else if variant == "j" { rgb("#f5d341") }
    else if variant == "q" { rgb("#c2a1c7") }
    else if variant == "W" { rgb("#00000000") } // transparent for spacing
    else { rgb("#FFEBA1") }
    rect(width: size, height: size, fill: color)[
      #set text(hyphenate: false)
      #align(center + horizon)[
        #text(weight: "bold", size: text_size)[#label]
    ]
  ]
}

#figure(
grid(columns: 4, gutter: 0.2em,
  none,
  es("q", $q$),
  none,
  es("q", $q$),
  
  es("c", $c$),
  es("d", $d$),
  es("e", $e$),
  es("y", $y$),

  none,
  none,
  es("j", $j$),
))

DIZZY uses a workshop to bring business stakeholders, customers, scientists, 
and other domain experts together to find consensus around software processes.
Computation and Systems experts should serve only to teach, ask questions, and suggest symbolic solutions to process gaps,
NOT to define or suggest what would otherwise be the process flow.

The workshop is largely based on Event Storming @brandolini2021 by Alberto Brandolini and uses many of the same techniques.
Attendees write on sticky notes and place them on a wall next to other notes.
Note colors are semantic symbols.
Notes convey and narrate a system in the language of facts and intentions.
Unlike Event Storming, DIZZY notes represent _real_ system components.

Events ( #box(es("e", "", size: 9pt, text_size: 10pt)) ) pin the most important facets of the process, and are recorded in past tense: "order placed," "payment declined," "shipment dispatched." These records are facts by which we represent all state changes.

Commands ( #box(es("c", "", size: 9pt, text_size: 10pt)) ) hook process automation and users into the ecosystem by capturing an intent. They are written imperatively: "place order", "submit payment." These commands may represent a button, API call, a form, or any other method of supplying new instruction to a software system.

Procedures ( #box(es("d", "", size: 9pt, text_size: 10pt)) ),
Policies ( #box(es("y", "", size: 9pt, text_size: 12pt)) ),
Projections ( #box(es("j", "", size: 9pt, text_size: 12pt)) ),
and 
Queries ( #box(es("q", "", size: 9pt, text_size: 12pt)) ),
replace the "Aggregate", "View", and "Process/Policy" systems of the DDD-inspired Event Storming model.


After the workshop, the DIZZY workflow guides the progressive development of each component until a software artifact is produced. This allows stakeholders to build the software visually and without confounding details that aren't important to those stakeholders.
 
// Event Storming is a collaborative workshop technique, originated by Alberto Brandolini @brandolini2021, where domain experts and engineers narrate a system in the language of facts and intentions.
// Participants post events on a wall in past tense: "order placed," "payment declined," "shipment dispatched."
// From those events, they identify the commands that initiated them, the actors who issued those commands, and the policies that react when facts are established.

No database is chosen.
No framework is selected.
The output is a shared vocabulary in regards to the domain at hand.

That vocabulary maps directly onto DIZZY's component schema.
// Past-tense stickies become Event definitions. Imperative commands become Command definitions. The reactive "when X, do Y" cards become Policies. 
// The work that transforms a command into events identifies the Procedures.
A workshop session does not merely produce a pile of forgettable photographs;
it produces the skeleton of a _feature definition_ which the rest of DIZZY transforms into functioning, scalable software.

This directness is intentional.
DIZZY's eight components exist precisely so that the output of domain discovery can be written down without loss of meaning.
A feature defined in DIZZY's vocabulary is still readable by the domain expert who participated in the session.
The command names, event names, and policy reactions are their words - not a translation of them.

This couples the language of the Computationalists and the Domain Experts - allowing both to have a concrete and shared artifact that communicate bidirectionally between abstract graphs and charts - and deployed and running systems.

DIZZY borrows the collaborative spirit of Brandolini's original technique, 
but adapts the semantic and pragmatic functional paradigm.
Aggregates, read models, and the object-oriented constructs of traditional Domain-Driven Design are absent.
Every DIZZY component is either a data contract or a stateless process - 
another distinction that makes components independently deployable, testable, and replaceable in ways the original framing does not require.

Like Event Storming though, the practice is intended to be simple and progressive.
Start by pinning Commands and Events.
This naturally exposes what procedures and policies may be required.
In turn, this can expose new Commands and Events that my be required for consistency,
which prompts more Procedures and Policies - etc.


// The exact placement does not matter as long as the intended connections between components are clear.
// Typically, I place my sticky-notes in this configuration as I go -

#figure(
grid(columns: 3, gutter: 5em,
// events and commands
grid(columns: 2, gutter: 0.2em,
  es("W", ""),
  es("W", ""),

  es("c", $c$),
  es("e", $e$),
),
// procedures
grid(columns: 4, gutter: 0.2em,
  es("W", ""),
  es("W", ""),
  es("W", ""),
  es("W", ""),

  es("c", $c$),
  es("d", $d$),
  es("e", $e$),
  es("y", $y$),
),
// queries and projections
grid(columns: 4, gutter: 0.2em,
  none,
  es("q", $q$),
  none,
  es("q", $q$),
  
  es("c", $c$),
  es("d", $d$),
  es("e", $e$),
  es("y", $y$),

  none,
  none,
  none,
  es("j", $j$),
)
)
)


When it is becomes time to define the gist of how Procedures and Policies function - 
this is where Projections and Queries come in.

Upon these notes, write the name of Model (representative of a database schema or ontology), 
and the name of the projection or query if it helps for disambiguation.

For instance, after an "Order Placed" Event, we may need to project the result to two Models -
one for "Shipping", and another for "Inventory". 
Naming these projections further is optional at this phase, 
but is useful later when the projections require disambiguation.


#figure(
grid(columns: 1, gutter: 5em,
// queries and projections
grid(columns: 4, gutter: 0.2em,
  none,
  es("q", $q$),
  none,
  none,
  // es("q", $q$),
  
  es("c", $c$),
  es("d", $d$),
  es("e", $e_1$),
  es("y", $y$),

  none,
  none,
  es("e", $e_2$),
  none,

  none,
  none,
  es("e", $e_3$),
  es("j", $j_1$),

  none,
  none,
  none,
  es("j", $j_2$),
)
)
)

An exact semantics for organizing notes is not needed.
If the workshop gets crowded - make copies of notes and spread things out until things make sense.

// It's common to start with Command and Events, and only model the procedures in between as a second step.
// However, I find it to be helpful to move back and forth between a Data-First and Program-First modelling approach, as we will see later.


// === Recording the Facts - Commands and Events

// The first pass focuses on what happens and why. What does a user want? What are the facts the system must record? At this stage, teams are only naming things — not defining their shape. The names, and the relationships between them, are the output.

// === Adding detail - Procedures and Policies

// Once the events and commands are named, the question becomes: what mediates each transition? Procedures and Policies are identified here — the work of each Procedure, and the reactions encoded in each Policy.

// === Identifying Queries and Marking Models

// When a Procedure or Policy needs to consult state — "what is the current balance?" or "has this request been seen before?" — a Query is identified. The answer to that Query comes from a Model. Marking these in the discovery session surfaces the retrieval concerns that will need to be addressed in the data layer.

// === Populating Models with Events and Projections

// Each Model named in the session needs a mechanism for staying current. A Projection listens to the Events that affect a Model's state and writes updates accordingly. Identifying the Projections completes the picture: for each Model, which Events change it?

== Studying Vibes and Experiments

#let flow2_dj = diagram(
  spacing: (2em, 2em),
  node-inset: 10pt,


  node((-1, 0), $c$, name: <c>),
  node(( 0, 0), $d j$, name: <dj>),
  node((1,0), $m$, name: <m>),
  
  node(( 0, 1), $e$, name: <e>),
  node((-1, 1), $y$, name: <y>),
  node(( 1,-1), $Q$, name: <Q>),
  node(( 0,-1), $q$, name: <q>),

  edge(<dj>, <e>, bend: 0deg, "->"),
  edge(<e>, <y>, bend: 0deg, "->"),
  edge(<y>, <c>, bend: 0deg, "->"),
  edge(<c>, <dj>, bend: 0deg, "->"),
  edge(<dj>, <m>, bend: 0deg, "->"),
  edge(<m>, <Q>, bend: 0deg, "->"),
  edge(<Q>, <q>, bend: 0deg, "<-->"),
  edge(<q>, <dj>, bend: 0deg, "<-->"),
  edge(<q>, <y>, bend: -70deg, "<-->"),
)

DIZZY is hard to emulate with simple scripts,
because a simple script is usually one that follows the UNIX Philosophy: file in, file out, do one job and do it well.
We can fit the DIZZY components to fit the guise of UNIX by composing Procedures and Projections.

$d j$ scripts sacrifice rigidity of the DIZZY core model to serve as an exercise of Intent and Event Extraction.

More on this: https://github.com/ConradMearns/without-objective/tree/main/Structured-Log-Pipes

#grid(
  column-gutter: 2em,
  // align: horizon,
  columns: (auto, auto),
  flow2_dj,
  [
    Here, $Q$ typically reflects a FileSystem. 
    $q$ represents read operations,
    while $j$ represents writes.
    Policies ($y$) aren't explicitly required, but still encode some level of reactivity to events that have taken place.
  ]
)

The goal is _not_ to write software like this.
Rather, it's to identify that the UNIX philosophy was indeed the standard pattern for writing software, an explicit Structure Log Piping system expresses better flexibility in building small scripts, which can be more easily translated into scalable architectures later.

Using this abstraction, we can now peer into the black box which may be our script - and identify when and where changes to Models (file outputs, database calls) are made.

We can identify IO reads and assign them names as Queries, 
and we can begin to imagine what Events must exist in order to become DIZZY compatible.

In practice, this can be fairly simple.
Often, it is enough to transform the base logging system into one which traces Side-Effects as DEBUG logs.
When those logs are structured, and consistent, then we can begin to use the logs themselves as a sort of pseudo Change Data Capture / "Event Store" for projections.

This exercise allows for legacy software to be transformed to become DIZZY compatible.

== Automation

#figure(
  pipeline,
  caption: [
    The DIZZY generation pipeline.
    A Feature File (green) is authored during domain discovery. 
    Data Contract Definitions (blue) are then populated with field-level detail. 
    The generator compiles these into typed Data Contract Implementations and Process Interfaces (purple),
    which are packaged as runtime-specific library artifacts (blue) that engineers implement against.
  ]
)

The outcome of workshopping is a _Feature File_.
The _Feature File_ is a structured declaration of every component the system requires:
which Commands exist, which Procedures handle them, which Events are then produced, which Policies react, which Projections maintain which Models, and which Queries serve those Procedures and Policies.

The _Feature File_ is a map.
It documents the high level structures which are then resolved into LinkML schemas and language-specific interfaces.

A developer, a technical lead, or the DIZZY automation tool can look at a Feature File and list exactly what needs to be built.
Each Procedure and Policy is a bounded unit of work with explicitly declared inputs, outputs, and data dependencies.
// The flows are not an emergent property of the code - they are a finite, readable list, agreed on before a single implementation is written.

The generation pipeline then takes this map and produces the scaffolding that engineers implement against.

=== Building Data Definition Schemas

The Feature File names components but does not describe the shape of the data they carry. 
Building data definitions is the step that gives those names their structure. 
What fields does a "receipt ingested" event carry?
What is the schema of the "receipts" model?
These questions are answered by authoring definitions in LinkML - a language-agnostic schema language that represents domain objects in YAML, independent of any particular programming language, framework, or runtime.
The Feature File is used to generate LinkML stubs for every Data Definition that is required, details can be filed in after.

// The choice of LinkML is not incidental. 
// Most schema systems are bound to a language or an ecosystem: a Pydantic model is Python; a TypeScript interface is TypeScript; a Protobuf definition belongs to gRPC.
// LinkML occupies a different position.
// It describes the domain in terms that belong to no runtime - the same event definition can be compiled to native types in Python, Rust, TypeScript, or any other target without modifying the source definition. Domain objects are written once. Their implementations are derived. 
// This is the mechanism that makes the rest of the pipeline possible: a single source of truth for what each data contract means, expressed in a form that any language toolchain can consume.

=== Building Program Processes

After Data Definitions are built, and the component wiring declared in the Feature File, typed interfaces are generated for every process. 
The interface for a Procedure declares exactly which Command it receives, which Queries it is permitted to call, and which Events it may emit. 
The interface for a Policy declares the Event that triggers it and the Commands it is allowed to dispatch.

At this stage, the The Feature File becomes a compile-time constraints for the architecture.
An implementation that exceeds its declared scope is a type error, and can be caught before deployment rather than after.

This generation step makes an explicit claim: the hard architectural decisions have already been made.
By the time an engineer receives a generated interface, the question of what each component does -
and what it is forbidden from doing -
has been resolved at the domain level. 
What remains is writing the Interstitial Infrastructure to tie the component flows together.
The interface enforces the boundary between domain thinking and implementation.

=== Packaging and Using Libraries

The final step packages the generated interfaces and their compiled data types into importable library artifacts.
A Procedure in Python receives a Python library.
A Policy in Rust receives a Rust library.
A Querier in TypeScript receives a TypeScript library.
Each library contains the same domain contracts, as generated by LinkML.

This is the handoff between the Domain and the Deployment.

Engineers implement against the library.
The library does not change unless the domain definitions change.
Infrastructure decisions, such as which database backs a Model, which message queue carries a Command - are made after the library is built, and they are made at a different layer of the architecture.
Domain logic never knows where its inputs came from or where its outputs go.

// Testing strategies at various levels?
// L3 L2 L1 LLM involvement?

// = Existing Disciplines, New Composition

// DIZZY is nothing new.
// Every idea in this paper has predecessors — some decades old, some still actively evolving.
// What DIZZY contributes is not invention but composition:
// a deliberate arrangement of existing disciplines into a coherent whole,
// where each one addresses a specific failure mode described in Section 1.

// The lineage includes:

// - Command Query Responsibility Separation (CQRS)
// - Command Queuing
// - Event Storming (for domain discovery)
// - Event Sourcing (for truth)
// - Functional Programming (for testable logic)
// - Dependency Injection (for decoupling)
// - Infrastructure as Code (for deployment)

// TODO: This section needs a paragraph per discipline (or at least the major ones)
// explaining *why* DIZZY adopts it and what problem it solves in the DIZZY context.
// The list satisfies WP-009 minimally — but WP-023 (authoritative, persuasive tone)
// requires making the case, not just naming the influences.
// Key claim to land: DIZZY does not replace these disciplines.
// It is an opinion about how they fit together.

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

// TODO: This section needs full prose to satisfy WP-012 and WP-028.
// Requirements:
// — Must reference the thesis from the Abstract (close the arc)
// — Must return to the problem opened in Section 1:
//   the map mislabels the territory; decisions harden into constraints
// — Must land the singular takeaway (WP-028):
//   DIZZY is a philosophy for building software where domain logic, data contracts,
//   and infrastructure are kept permanently separate — so any one can change
//   without breaking the others.
// — Must direct the reader to the Specification (WP-027)
//
// Suggested framing: return to the Dijkstra epigraph.
// The software crisis is not a tools problem — it is a reasoning problem.
// DIZZY is a bet that if you give teams a precise vocabulary for their domain,
// the reasoning becomes tractable.
// Close with the Specification pointer below.

For the formal specification of DIZZY components, schemas, and code generation pipeline, see the companion _DIZZY Specification_.



= Appendix

== Common Patterns

=== Durable Execution

A procedure can _preform work_ if and only if the work has never been started, 
or in the cases where a previous fault or outage interrupted the runtime.

An explicit failure-as-ended state helps to disambiguate between runtime failures of the procedure and external failures like network interruption, power loss, etc.



For some procedure $d_w$ a durable version $d_d$ is a procedure that wraps $d_w$ such that
1. *Durable Execution Procedure* queries for *Activity Started*
  1. If no *Activity Started*, then emit *Activity Started*
  2. If any *Activity Started*, then query for *Activity Ended* on ID
    1. If no *Activity Ended* - do $d_w$.
    2. If any *Activity Ended* - return


#figure(
grid(columns: 2, gutter: 5em,
// queries and projections
grid(columns: 4, gutter: 0.2em,
  es("c", $c_1$),
  es("d", $d_w$),
  es("e", $e_1$),
  none,none,none,
  es("e", $e_2$),
  none,none,none,
  es("e", $e_3$),
  none,none,none,
  es("e", $e_w$),
),
// definitions
table(
  columns: (auto, auto, auto),
  align: (center, left, left),
  table.header([*Symbol*], [*Component*], [*Role*]),
  $c_1$, [Command],    [Start Activity with ID],
  $d_d$, [Procedure],  [Durable Execution Procedure],
  $e_1$, [Event],      [Activity Started],
  $e_2$, [Event],      [Activity Ended (Succeeded)],
  $e_3$, [Event],      [Activity Ended (Failed)],
  $e_w$, [Event],      [Existing $d_w$ events],
),
)
)


=== Provenance

- Activities
- Entities
- Agents (Human and LLM)



#bibliography("refs.bib")
