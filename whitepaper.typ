#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge

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

#let flow = diagram(
  spacing: (1em, 1em),

  node((0,1), $c$),
  node((1,0), $d$),
  node((2,1), $e$),
  node((1,2), $y$),
  
  edge((0,1), (1,0), "->", $$),
  edge((1,0), (2,1), "->", $$),
  edge((2,1), (1,2), "->", $$),
  edge((1,2), (0,1), "->", $$),

  node((3,1), $j$),
  node((4,1), $m$),
  node((5,1), $Q$),

  edge((2,1), (3,1), "->", $$),
  edge((3,1), (4,1), "->", $$),
  edge((4,1), (5,1), "->", $$),

  edge((5,1), (1,0), "<-->", $$, bend: -20deg),
  edge((5,1), (1,2), "<-->", $$, bend: 20deg),
)

#figure(
  flow
)

abstract

= Problems and Needs

== No One Best architecture / cloud provider
- aws cost, lambda vs ec2, serverless, microservice, monolith
== Conway's Law
== No One Best Serialization format
== Need to Know vs Need to Share -> some things must be shared
== Managing risk and legacy applications with slow procedural drift
== where does risk lie in software development / scaling
- nvpsm
- Reliable Software Development
== Provenance
== Architecture for cost optimization, batching, and distribution
== Agentic Workflows -> terminal's have been crushing the game, how do we scale

// arge amounts of legacy and proprietary equipment for which automation is desirable, but access to an API isn't possible

= Guiding Principals

Everything in computing changes, it's just a matter of _when_.
Many systems are implemented to solve for specific problems in software development,
only to be usurped and made obsolete by advances in hardware development, 
or algorithms that change the objective completely.

The real issue with modern architectures is not whether Monoliths or Microservices are better;
it's that we force that decision upon ourselves and become shackled to its consequences for decades.

Truly modular software should work across
disciplines, languages, networks, and hardware.

What if we could rewrite _just_ the critical path in rust?
What if we could swap databases in and out of our system as easily as a feature flag?

We can accomplish this with existing disciplines

- Command Query Responsibility Separation
- Command Queuing
- Event Storming
- Event Sourcing
- Functional Programming
- Dependency Injection
- #strike[Infrastructure as Code] $->$ Infrastructure _from_ Code

How do we teach the philosophy?

- How do we know we understand the problem well enough to model it?
  - The Map is Not the Territory
- Structured Logging is for more than just debugging
  - The spectrum of Change Data Capture $<-->$ Event Sourcing
- How do we communicate how "good" a software is?
- In a future where writing software is 10000x cheaper, how do we structure the work?

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

// == concepts
// === CQRS
// - command query responsibility separation
// === Event Sourcing
// === The Database is an optimization


== components
=== data

why data; how data; LinkML + Katai schemas; semantics; transport

==== commands

imperative;
ephemeral;

==== events

immutable;
durable;
past tense;
data;

==== models

database primitives; linkml

=== processes

functional; procedures, policies, projections; execution context;

==== context

The general design philosophy of a process is that we don't want to wait to inform other components of the work we've completed.

Instead of relying on return codes, everything looks like a callback. How this callback is implemented is up to the deployment code. // TODO link to deployment section

In most cases, the callback is a simple `put` onto a queue.

```python
@dataclass
class Context:
    emit: BazCrunchedEmitter # Callable[[BazCrunched], None]
    query: BazQueriers # assuming has a .search(str) query
def process(input: Input, context: Context):
  baz = foo(input.bar, context.query.search("fubar term history"))
  context.emit(BazCrunched(baz))
```

==== procedures

can emit any number of events; meaningful work; at least 1 per command; R/W; effects

==== policies

can emit any number of commands; workflow logic; at least 1 per event; R/O

==== projections

model mapping; deployment location; api; crud; at least 1 per event;

=== queries

deployment location; database as an optimization; no one best storage solution; graphql query input; combination of processes and data

== event loop
== model loop
// === ecs

== context
== modelling recommendations

durable execution; sagas; identity;

== development recommendations

unit testing; chaos testing; 

def; gen; src; bin;

== deployment recommendations

event sourcing; queues; 

== user interfaces

similarities to model view controller; $c->d->Q$

== examples

todo with ui; rtos; k8s web app; etl;


= Figures

adjust:

#diagram(
  node-corner-radius: 4pt,

  // Event space elements
  node((0,0), $e_1$),
  node((0,1), $e_2$),
  node((0,2), $e_3$),
  node((0,3), $e_4$),
  node((0,4), $e_5$),
  node((0,5), $e_6$),

  // Model space elements
  node((3,0), $m_1$),
  node((3,1), $m_2$),
  node((3,2), $m_3$),

  {
    let tint(c) = (stroke: c, fill: rgb(..c.components().slice(0,3), 5%), inset: 8pt)
    node(enclose: ((0,0), (0,5)), ..tint(blue), name: <e>)
    node(enclose: ((3,0), (3,2)), ..tint(green), name: <m>)
  },

  edge(<e>, <m>, "->", $j$, stroke: 2pt),
)

#diagram(
  node-corner-radius: 4pt,

  // Event space elements (on top)
  node((0,0), $e_1$),
  node((1,0), $e_2$),
  node((2,0), $e_3$),
  node((3,0), $e_4$),
  node((4,0), $e_5$),
  node((5,0), $e_6$),

  // Model space elements (on bottom)
  node((0,3), $m_1$),
  node((1,3), $m_2$),
  node((2,3), $m_3$),

  {
    let tint(c) = (stroke: c, fill: rgb(..c.components().slice(0,3), 5%), inset: 8pt)
    node(enclose: ((0,0), (5,0)), ..tint(blue), name: <e>)
    node(enclose: ((0,3), (2,3)), ..tint(green), name: <m>)
  },

  // Complex mapping between events and models
  edge((0,0), (0,3), "->", stroke: .5pt),
  edge((0,0), (1,3), "->", stroke: .5pt),
  edge((1,0), (1,3), "->", stroke: .5pt),
  edge((2,0), (0,3), "->", stroke: .5pt),
  edge((2,0), (2,3), "->", stroke: .5pt),
  edge((3,0), (2,3), "->", stroke: .5pt),
  edge((4,0), (0,3), "->", stroke: .5pt),
  edge((4,0), (1,3), "->", stroke: .5pt),
  edge((4,0), (2,3), "->", stroke: .5pt),
  edge((5,0), (1,3), "->", stroke: .5pt),
)

#diagram(
  node-corner-radius: 4pt,
  spacing: (2em, 1.5em),

  // Event space elements with examples
  node((0,0), [$e_1$: ItemAddedToCart]),
  node((0,1), [$e_2$: ItemRemovedFromCart]),
  node((0,2), [$e_3$: OrderPlaced]),
  node((0,3), [$e_4$: PaymentReceived]),
  node((0,4), [$e_5$: ItemShipped]),

  // Model space elements (database tables)
  node((3,0), [$m_1$: CartItems]),
  node((3,1), [$m_2$: Orders]),
  node((3,2), [$m_3$: Inventory]),
  node((3,3), [$m_4$: Analytics]),

  {
    let tint(c) = (stroke: c, fill: rgb(..c.components().slice(0,3), 5%), inset: 8pt)
    node(enclose: ((0,0), (0,4)), ..tint(blue), name: <e>)
    node(enclose: ((3,0), (3,3)), ..tint(green), name: <m>)
  },

  // Complex mapping between events and models
  edge((0,0), (3,0), "->", stroke: .5pt),
  edge((0,0), (3,2), "->", stroke: .5pt),
  edge((0,0), (3,3), "->", stroke: .5pt),
  edge((0,1), (3,0), "->", stroke: .5pt),
  edge((0,1), (3,2), "->", stroke: .5pt),
  edge((0,1), (3,3), "->", stroke: .5pt),
  edge((0,2), (3,0), "->", stroke: .5pt),
  edge((0,2), (3,1), "->", stroke: .5pt),
  edge((0,2), (3,3), "->", stroke: .5pt),
  edge((0,3), (3,1), "->", stroke: .5pt),
  edge((0,3), (3,3), "->", stroke: .5pt),
  edge((0,4), (3,1), "->", stroke: .5pt),
  edge((0,4), (3,2), "->", stroke: .5pt),
  edge((0,4), (3,3), "->", stroke: .5pt),
)

template:



#diagram(
  node-corner-radius: 4pt,
  node((0,0), $S a$),
  node((1,0), $T b$),
  node((0,1), $S a'$),
  node((1,1), $T b'$),
  edge((0,0), (1,0), "->", $f$),
  edge((0,1), (1,1), "->", $f'$),
  edge((0,0), (0,1), "->", $alpha$),
  edge((1,0), (1,1), "->", $beta$),

  node((2,0), $(a, b, f)$),
  edge("->", text(0.8em, $(alpha, beta)$)),
  node((2,1), $(a', b', f')$),

  node((0,2), $S a$),
  edge("->", $f$),
  node((1,2), $T b$),

  node((2,2), $(a, b, f)$),

  {
      let tint(c) = (stroke: c, fill: rgb(..c.components().slice(0,3), 5%), inset: 8pt)
      node(enclose: ((0,0), (1,1)), ..tint(teal), name: <big>)
      node(enclose: ((2,0), (2,1)), ..tint(teal), name: <tall>)
      node(enclose: ((0,2), (1,2)), ..tint(green), name: <wide>)
      node(enclose: ((2,2),), ..tint(green), name: <small>)
  },

  edge(<big>, <tall>, "<==>", stroke: teal + .75pt),
  edge(<wide>, <small>, "<==>", stroke: green + .75pt),
  edge(<big>, <wide>, "<=>", stroke: .75pt),
  edge(<tall>, <small>, "<=>", stroke: .75pt),
)