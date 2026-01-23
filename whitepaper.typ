#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge

// Whitepaper Configuration
#set page(
  paper: "us-letter",
  margin: (x: 1.5in, y: 1in),
)

#set text(
  font: "Linux Libertine",
  size: 11pt,
)

#set par(
  justify: true,
  leading: 0.65em,
)

// Title
#align(center)[
  #text(17pt, weight: "bold")[Whitepaper Title]

  #v(0.5em)

  #text(12pt)[Author Name]

  #text(11pt)[#datetime.today().display()]
]

#v(1em)

= Introduction

This is a whitepaper document using Typst with Fletcher diagrams.

= Diagram Example

Below is an example of a commutative diagram using Fletcher:

#align(center)[
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
]

= Content

Add your whitepaper content here.

= Problems and Needs

== No One Best Serialization format
== Need to Know vs Need to Share -> some things must be shared
== Workflow Discovery -> NVPSM -> where does risk lie in software development / scaling
== Provenance
== Architecture for cost optimization, batching, and distribution
== Agentic Workflows -> terminal's have been crushing the game, how do we scale

arge amounts of legacy and proprietary equipment for which automation is desirable, but access to an API isn't possible

= DIZZY
== components
=== events
=== commands
=== policies
=== procedures
=== projections
=== queries
== event loop
== model loop
// === ecs
== 