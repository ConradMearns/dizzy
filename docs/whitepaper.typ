#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#import "@preview/glossy:0.9.1": *
#import "figures.typ": flow, c_map, e_map, d_map, y_map, j_map, m_map, Q_map, pipeline
#import "glossary.typ": dizzy-terms

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
    A Philosophy for the Development of Certain Event Driven Architectures with Deferred Interstitial Infrastructure
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

#show: init-glossary.with(dizzy-terms)

#pagebreak()

#outline(
  title: [Table of Contents],
  indent: auto,
)

#pagebreak()

#import "pnf/pains/irreversibility.typ":            title as pain_01, body as pain_01_body
#import "pnf/pains/false_dichotomies.typ":          title as pain_02, body as pain_02_body
#import "pnf/pains/applications_as_islands.typ":    title as pain_03, body as pain_03_body
#import "pnf/pains/mislabeled_territory.typ":       title as pain_04, body as pain_04_body
#import "pnf/pains/inadequate_support.typ":         title as pain_05, body as pain_05_body

#import "pnf/needs/defer_deployment.typ":           title as need_01, body as need_01_body
#import "pnf/needs/architect_for_reversibility.typ":title as need_02, body as need_02_body
#import "pnf/needs/any_language.typ":               title as need_03, body as need_03_body
#import "pnf/needs/separate_data_functions.typ":    title as need_04, body as need_04_body
#import "pnf/needs/derive_infra.typ":               title as need_05, body as need_05_body

#import "pnf/feats/separating_infra_domain.typ":    title as feat_01, body as feat_01_body

// PAINS
= The Burden of Software Architecture is...

== #pain_01
#pain_01_body

== #pain_02
#pain_02_body

== #pain_03
#pain_03_body

== #pain_04
#pain_04_body

== #pain_05
#pain_05_body

// NEEDS
= Software Architectures Should... 

...deliberately shape the communication structures of the organizations that build them.

The Inverse Conway Maneuver says: if your system is going to mirror your organization anyway, design it to mirror the organization you _want_. 
DIZZY applies this as an architecture constraint. 
Its rigid component boundaries are deliberate seams that define where teams own work independently and where they must coordinate.

== #need_01
#need_01_body

== #need_02
#need_02_body

== #need_03
#need_03_body

== #need_04
#need_04_body

== #need_05
#need_05_body

// FEATS
= DIZZY Solves this by...

...through it's philosophy

== #feat_01
#feat_01_body



= Implementation

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
  $d$, [Procedure],  [Handles a Command and may emit @event:pl],
  $e$, [Event],      [Immutable record of facts - the source of truth],
  $y$, [Policy],     [Reacts to an Event and may emit @command:pl],
  $j$, [Projection], [Listens for @event:pl and updates @model:pl],
  $m$, [Model],      [Queryable view of state, derived from @event:pl],
  $Q$, [Querier],    [Executes a Query against a Model],
  $q$, [Query],      [Typed contract for a call and its response],
))

// This is intended to be a very high level description of the DIZZY architecture.
// See the Specification for more detail.

DIZZY is therefor comprised of two dataflow loops.

Firstly, a reactivity loop; Where @command:pl trigger @procedure:pl, which emit @event:pl that trigger @policy:pl, that emit @command:pl.
Secondly, a data retrieval loop; Where Event are projected to @model:pl (databases), which can be queried by @procedure:pl and @policy:pl.
The reactivity loop enables processing, algorithms, and business logic to react and change to new information. The retrieval loop enables database decoupling while providing efficient value lookups.

As an example, suppose we processing financial transactions. 
Each @event:pl record debits and credits as the source of truth.
Transactions are initiated by users and the data is represented by a Command.
The Transaction Command triggers a procedure, 
which may need to Query for the normalized account balance to know whether to succeed or fail.
Thus, each debit and credit Event must also trigger a projection to keep this normalized account balance up-to-date in a Model.

// The data loop enables change information (@event:pl) to be recorded in highly specialized formats specifically for the purposes of efficient retrieval by @procedure:pl and @policy:pl.

== @command:pl ( $c$ ) that Represent Intent <commands>

#grid(
columns: (auto, 1fr),
column-gutter: 2em,
align: horizon,
figure(c_map),
[
#v(1em)

@command:pl represent expressions of intent, what users _want_ to happen.
They are ephemeral - not records of fact, and thus may be fire-and-forget and discarded.
This distinction matters: intent can be rejected, retried, or rerouted. 

Facts cannot.

Because @command:pl are ephemeral and may be discarded without consequence, 
the are useful for isolating the transmission of data must abide to different legal and business policies -
such as personally identifiable information.

Whether this information is recorded as an immutable fact is up to the design of @procedure:pl and @event:pl.

A policy may emit any number of @command:pl, of any @command sub-types.
Therefore policies and @command:pl are one-to-many; several policies may emit the same @command types.

// TODO: Can a Command be handled by more than one Procedure, or is it always 1:1?
A @command may trigger many @procedure:pl. This relation is typically best assigned at the Procedure definition.

// TODO: Is a rejected Command recorded anywhere — does rejection itself become an Event?
])

@command:pl express intent, and can be carefully designed to handle cases where lossy systems where retries are standard practice. See Durable Execution // TODO make a link!

== @procedure:pl ( $d$ ) that Perform the Critical Work <procedures>

#grid(
columns: (auto, 1fr),
column-gutter: 2em,
align: horizon,
figure(d_map),
[
#v(1em)

@procedure:pl handle #link(<commands>)[@command:pl] and may emit #link(<events>)[@event:pl].
They are the site of critical work in a DIZZY system — the place where intent meets consequence.

@procedure:pl are not required to be pure functions. They may query #link(<models>)[@model:pl] to inform their decisions.
But any external system a Procedure touches must either be modelled as another DIZZY component,
or its effects must be recorded in @event:pl.
This constraint is what makes @procedure:pl portable across languages and deployable in any topology:
their behavior is fully described by what they receive, what they query, and what they emit.

When a Procedure performs IO or causes effects in the world, it should emit @event:pl
to record the attempt, progress, and result.
An effect that is not recorded in an Event is invisible to the rest of the system —
and invisible effects undermine the audit guarantee that @event:pl provide.

// TODO: Can a single Command trigger multiple @procedure:pl, or is the relationship always 1:1?
// TODO: Are @procedure:pl allowed to call each other directly, or must all coordination
// flow through @command:pl and @event:pl?
])

== @event:pl ( $e$ ) that are the Source of Truth <events>

#grid(
columns: (auto, 1fr),
column-gutter: 2em,
align: horizon,
figure(e_map),
[
#v(1em)
@event:pl are the single source of truth.
Everything else — every model, every view, every report — must be derived from events.
@event:pl are immutable records of what _happened_: once written, they cannot be altered or deleted.

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




== @policy:pl ( $y$ ) that React and Initiate <policies>

#grid(
columns: (auto, 1fr),
column-gutter: 2em,
align: horizon,
figure(y_map),
[
#v(1em)
@policy:pl are the reactive logic of a DIZZY system.
Where @procedure:pl respond to intent, @policy:pl respond to fact:
they are triggered by #link(<events>)[@event:pl] that have already occurred,
and they may emit #link(<commands>)[@command:pl] in response.
A Policy asks: _given that this happened, what should happen next?_

This distinction is not incidental.
Because a Policy reacts to an Event — an immutable, already-happened fact —
it is inherently decoupled from the Procedure that produced it.
The Policy does not know or care how the Event came to exist.
It knows only what happened, and responds accordingly.

@policy:pl may also query #link(<models>)[@model:pl] to inform their decisions,
allowing the system to react differently depending on current state.
A Policy that always emits the same Command is a simple rule.
A Policy that queries a Model first is a conditional one — but the conditionality
lives in the Policy, not scattered through unrelated code.

// TODO: Can a single Policy react to multiple Event types, or is it always bound to one?
// TODO: Can a Policy emit multiple @command:pl, or at most one per triggering Event?
// TODO: What is the relationship between @policy:pl and long-running processes / sagas?
// A saga that spans multiple @event:pl over time seems like it would require Policy state —
// how does DIZZY handle that without violating the stateless reactive model?
])

== @projection:pl ( $j$ ) that Map @event:pl to @model:pl <projections>

#grid(
columns: (auto, 1fr),
column-gutter: 2em,
align: horizon,
figure(j_map),
[
#v(1em)

#link(<events>)[@event:pl] are the authoritative record of everything that has happened,
but they are not optimized for retrieval.
A Projection solves this: it listens for specific @event:pl and updates one or more
#link(<models>)[@model:pl] in response,
translating the language of facts into the language of efficient queries.

This approach eliminates the need for Aggregates — the construct traditional Domain-Driven Design
uses to bridge event-driven architecture to object-oriented state.
Because @model:pl in DIZZY are treated as ephemeral and rebuildable from @event:pl,
there is no need for an object that holds and manages state on behalf of a set of related entities.

The practical consequence is significant: if a Model turns out to be wrong for its purpose,
it can be replaced without touching the event history.
Write a new Projection, replay the @event:pl, and a new Model emerges from the same source of truth.

// TODO: Is a Projection always bound to a specific set of Event types, or can it subscribe broadly?
// TODO: What is the failure model — if a Projection crashes mid-replay, how does it recover?
// TODO: Can multiple @projection:pl write to the same Model, or is it always 1:1?
])

== @model:pl ( $m$ ) that Serve Data for @query:pl <models>

#grid(
columns: (auto, 1fr),
column-gutter: 2em,
align: horizon,
figure(m_map),
[
#v(1em)

A Model is a schema for queryable state, backed by a database chosen for the specific access
patterns that Model must serve.
@model:pl are derived from #link(<events>)[@event:pl] via #link(<projections>)[@projection:pl],
and are rebuildable on demand.

@model:pl exist to make queries fast, not to be the source of truth.
You can have as many @model:pl as you have distinct questions to answer —
each backed by whatever database technology best suits those questions.
A time-series store for metrics, a graph database for relationships, a search index for full-text:
all derived from the same Event stream.

// TODO: Should a Model ever be written to by anything other than @projection:pl?
// TODO: Is there a constraint on how many @projection:pl can write to a single Model?
])


== @query:pl ( $q$ ) and @querier:pl ( $Q$ ) for efficient computation <queries> //<queriers>

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
We call the data contracts @query:pl, which are typically represented as a tuple of Input and Output, or Call and Response.
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

@event:pl ( #box(es("e", "", size: 9pt, text_size: 10pt)) ) pin the most important facets of the process, and are recorded in past tense: "order placed," "payment declined," "shipment dispatched." These records are facts by which we represent all state changes.

@command:pl ( #box(es("c", "", size: 9pt, text_size: 10pt)) ) hook process automation and users into the ecosystem by capturing an intent. They are written imperatively: "place order", "submit payment." These @command:pl may represent a button, API call, a form, or any other method of supplying new instruction to a software system.

@procedure:pl ( #box(es("d", "", size: 9pt, text_size: 10pt)) ),
@policy:pl ( #box(es("y", "", size: 9pt, text_size: 12pt)) ),
@projection:pl ( #box(es("j", "", size: 9pt, text_size: 12pt)) ),
and 
@query:pl ( #box(es("q", "", size: 9pt, text_size: 12pt)) ),
replace the "Aggregate", "View", and "Process/Policy" systems of the DDD-inspired Event Storming model.


After the workshop, the DIZZY workflow guides the progressive development of each component until a software artifact is produced. This allows stakeholders to build the software visually and without confounding details that aren't important to those stakeholders.
 
// Event Storming is a collaborative workshop technique, originated by Alberto Brandolini @brandolini2021, where domain experts and engineers narrate a system in the language of facts and intentions.
// Participants post events on a wall in past tense: "order placed," "payment declined," "shipment dispatched."
// From those events, they identify the @command:pl that initiated them, the actors who issued those @command:pl, and the policies that react when facts are established.

No database is chosen.
No framework is selected.
The output is a shared vocabulary in regards to the domain at hand.

That vocabulary maps directly onto DIZZY's component schema.
// Past-tense stickies become Event definitions. Imperative @command:pl become @command definitions. The reactive "when X, do Y" cards become @policy:pl. 
// The work that transforms a command into events identifies the @procedure:pl.
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
Start by pinning @command:pl and @event:pl.
This naturally exposes what procedures and policies may be required.
In turn, this can expose new @command:pl and @event:pl that my be required for consistency,
which prompts more @procedure:pl and @policy:pl - etc.


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


When it is becomes time to define the gist of how @procedure:pl and @policy:pl function - 
this is where @projection:pl and @query:pl come in.

Upon these notes, write the name of Model (representative of a database schema or ontology), 
and the name of the projection or query if it helps for disambiguation.

For instance, after an "Order Placed" Event, we may need to project the result to two @model:pl -
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

// It's common to start with Command and @event:pl, and only model the procedures in between as a second step.
// However, I find it to be helpful to move back and forth between a Data-First and Program-First modelling approach, as we will see later.


// === Recording the Facts - @command:pl and @event:pl

// The first pass focuses on what happens and why. What does a user want? What are the facts the system must record? At this stage, teams are only naming things — not defining their shape. The names, and the relationships between them, are the output.

// === Adding detail - @procedure:pl and @policy:pl

// Once the events and @command:pl are named, the question becomes: what mediates each transition? @procedure:pl and @policy:pl are identified here — the work of each Procedure, and the reactions encoded in each Policy.

// === Identifying @query:pl and Marking @model:pl

// When a Procedure or Policy needs to consult state — "what is the current balance?" or "has this request been seen before?" — a Query is identified. The answer to that Query comes from a Model. Marking these in the discovery session surfaces the retrieval concerns that will need to be addressed in the data layer.

// === Populating @model:pl with @event:pl and @projection:pl

// Each Model named in the session needs a mechanism for staying current. A Projection listens to the @event:pl that affect a Model's state and writes updates accordingly. Identifying the @projection:pl completes the picture: for each Model, which @event:pl change it?

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
We can fit the DIZZY components to fit the guise of UNIX by composing @procedure:pl and @projection:pl.

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
    @policy:pl ($y$) aren't explicitly required, but still encode some level of reactivity to events that have taken place.
  ]
)

The goal is _not_ to write software like this.
Rather, it's to identify that the UNIX philosophy was indeed the standard pattern for writing software, an explicit Structure Log Piping system expresses better flexibility in building small scripts, which can be more easily translated into scalable architectures later.

Using this abstraction, we can now peer into the black box which may be our script - and identify when and where changes to @model:pl (file outputs, database calls) are made.

We can identify IO reads and assign them names as @query:pl, 
and we can begin to imagine what @event:pl must exist in order to become DIZZY compatible.

In practice, this can be fairly simple.
Often, it is enough to transform the base logging system into one which traces Side-Effects as DEBUG logs.
When those logs are structured, and consistent, then we can begin to use the logs themselves as a sort of pseudo Change Data Capture / "Event Store" for projections.

This exercise allows for legacy software to be transformed to become DIZZY compatible.

== Automation

#figure(
  pipeline,
  caption: [
    The DIZZY generation pipeline.
    A @feature-file (green) is authored during domain discovery. 
    Data Contract Definitions (blue) are then populated with field-level detail. 
    The generator compiles these into typed Data Contract Implementations and Process Interfaces (purple),
    which are packaged as runtime-specific library artifacts (blue) that engineers implement against.
  ]
)

The outcome of workshopping is a @feature-file.
The @feature-file is a structured declaration of every component the system requires:
which @command:pl exist, which @procedure:pl handle them, which @event:pl are then produced, which @policy:pl react, which @projection:pl maintain which @model:pl, and which @query:pl serve those @procedure:pl and @policy:pl.

The @feature-file is a map.
It documents the high level structures which are then resolved into LinkML schemas and language-specific interfaces.

A developer, a technical lead, or the DIZZY automation tool can look at a @feature-file and list exactly what needs to be built.
Each Procedure and Policy is a bounded unit of work with explicitly declared inputs, outputs, and data dependencies.
// The flows are not an emergent property of the code - they are a finite, readable list, agreed on before a single implementation is written.

The generation pipeline then takes this map and produces the scaffolding that engineers implement against.

=== Building Data Definition Schemas

The @feature-file names components but does not describe the shape of the data they carry. 
Building data definitions is the step that gives those names their structure. 
What fields does a "receipt ingested" event carry?
What is the schema of the "receipts" model?
These questions are answered by authoring definitions in LinkML - a language-agnostic schema language that represents domain objects in YAML, independent of any particular programming language, framework, or runtime.
The @feature-file is used to generate LinkML stubs for every Data Definition that is required, details can be filed in after.

// The choice of LinkML is not incidental. 
// Most schema systems are bound to a language or an ecosystem: a Pydantic model is Python; a TypeScript interface is TypeScript; a Protobuf definition belongs to gRPC.
// LinkML occupies a different position.
// It describes the domain in terms that belong to no runtime - the same event definition can be compiled to native types in Python, Rust, TypeScript, or any other target without modifying the source definition. Domain objects are written once. Their implementations are derived. 
// This is the mechanism that makes the rest of the pipeline possible: a single source of truth for what each data contract means, expressed in a form that any language toolchain can consume.

=== Building Program Processes

After Data Definitions are built, and the component wiring declared in the @feature-file, typed interfaces are generated for every process. 
The interface for a Procedure declares exactly which Command it receives, which @query:pl it is permitted to call, and which @event:pl it may emit. 
The interface for a Policy declares the Event that triggers it and the @command:pl it is allowed to dispatch.

At this stage, the The @feature-file becomes a compile-time constraints for the architecture.
An implementation that exceeds its declared scope is a type error, and can be caught before deployment rather than after.

This generation step makes an explicit claim: the hard architectural decisions have already been made.
By the time an engineer receives a generated interface, the question of what each component does -
and what it is forbidden from doing -
has been resolved at the domain level. 
What remains is writing the @interstitial-infrastructure to tie the component flows together.
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

// autodocs!

#glossary(
  // theme: theme-twocol,
  groups: ("DIZZY Components", "Architecture", "Collectives"),
)

#bibliography("refs.bib")

// https://maggieappleton.com/garden-history
// https://veilid.com/Launch-Slides-Veilid.pdf
// https://www.cs.utexas.edu/~EWD/transcriptions/EWD13xx/EWD1305.html 
// https://github.com/ConradMearns/without-objective/tree/main/Structured-Log-Pipes