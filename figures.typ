#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge

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


#box[
  #set text(size: 2em)
  #flow
]


// TODO fix cardinality
#let flow_full = diagram(
  spacing: (5em, 2em),


  node((-1,1), $e$, name: <e>),

  node((1,1), $c$, name: <c>),

  node((1,0), $d$, name: <d>),
  node((1,2), $y$, name: <y>),

  node((0,-1), $j$, name: <j>),
  node((1,-1), $m$, name: <m>),

  node((2,-1), $Q$, name: <Q>),

  node((3,1), $q$, name: <q>),

  // 1 1! 1? n n! n?
  edge(<e>, <j>, bend: 0deg, "1-n"),
  edge(<j>, <m>, bend: 0deg, "1-n"),
  edge(<m>, <Q>, bend: 0deg, "1-n"),
  
  edge(<Q>, <q>, bend: 0deg, "1-n"),

  edge(<q>, <y>, bend: 0deg, "1-n"),
  edge(<q>, <d>, bend: 0deg, "1-n"),

  edge(<c>, <d>, bend: 0deg, "1-n"),
  edge(<c>, <y>, bend: 0deg, "1-n"),

  edge(<e>, <d>, bend:  0deg, "1-n"),
  edge(<e>, <y>, bend:  0deg, "1-n"),

)


#box[
  #set text(size: 2em)
  #flow_full
]

flow_full




#let pipeline = diagram(
  spacing: (1em, 3em),

  node((4,0), $"feat"$, name: <feat1> ),

  {
    let tint(c) = (
      stroke: c, 
      fill: rgb(..c.components().slice(0,3), 5%), 
      inset: 8pt
    )
    node(
      enclose: ((0,-0.2), (8,0.2)),
      ..tint(green), 
      name: <feat>
    )
  },

  // def
  node((0,1), $m_"def"$, name: <m1_def>),
  node((1,1), $e_"def"$, name: <e_def>),
  node((2,1), $c_"def"$, name: <c_def>),
  node((3,1), $q_"def"$, name: <q_def>),
  node((4,1), $m_"def"$, name: <m2_def>),
  node((7,1), $"definitions"$,   name: <gen_definitions>),


  // gen models
  node((0,2), $m_"gen"$, name: <m1_gen>),
  node((1,2), $e_"gen"$, name: <e_gen>),
  node((2,2), $c_"gen"$, name: <c_gen>),
  node((3,2), $q_"gen"$, name: <q_gen>),
  node((4,2), $m_"gen"$, name: <m2_gen>),
  node((7,2), $"classes"$,   name: <gen_classes>),


  // gen protocols
  node((0.5,3), $j_"gen"$,   name: <j_gen>),
  node((1.5,3), $y_"gen"$,   name: <y_gen>),
  node((2.5,3), $d_"gen"$,   name: <d_gen>),
  node((3.5,3), $Q_"gen"$,   name: <Q_gen>),
  node((7,3), $"interfaces"$,   name: <gen_interfaces>),
  
  edge(<m1_gen>, <j_gen>,  bend: 0deg, "->"),
  edge(<e_gen>, <j_gen>,   bend: 0deg, "->"),
  edge(<e_gen>, <y_gen>,   bend: 0deg, "->"),
  edge(<e_gen>, <d_gen>,   bend: 0deg, "->"),
  edge(<c_gen>, <y_gen>,   bend: 0deg, "->"),
  edge(<c_gen>, <d_gen>,   bend: 0deg, "->"),
  edge(<q_gen>, <y_gen>,   bend: 0deg, "->"),
  edge(<q_gen>, <d_gen>,   bend: 0deg, "->"),
  edge(<q_gen>, <Q_gen>,   bend: 0deg, "->"),
  edge(<m2_gen>, <Q_gen>,  bend: 0deg, "->"),

  node((0.5,4), $j_"src"$,   name: <j_src>),
  node((1.5,4), $y_"src"$,   name: <y_src>),
  node((2.5,4), $d_"src"$,   name: <d_src>),
  node((3.5,4), $Q_"src"$,   name: <Q_src>),
  node((7,4), $"source"$,   name: <src_source>),



  // src
  // node((5,3), $Q_"src"$,   name: <Q_src>),
  // node((6,3), $d_"src"$,   name: <d_src>),
  // node((7,3), $y_"src"$,   name: <y_src>),
  // node((8,3), $j_"src"$,   name: <j_src>),

  // edge(<feat>, <e_def>,   bend: 0deg, "->"),
  // edge(<feat>, <c_def>,   bend: 0deg, "->"),
  // edge(<feat>, <m_def>,   bend: 0deg, "->"),
  // edge(<feat>, <q_i_def>, bend: 0deg, "->"),
  // edge(<feat>, <q_o_def>, bend: 0deg, "->"),

  // edge(<feat>, <Q_gen>, bend: 0deg, "->"),
  // edge(<feat>, <d_gen>, bend: 0deg, "->"),
  // edge(<feat>, <y_gen>, bend: 0deg, "->"),
  // edge(<feat>, <j_gen>, bend: 0deg, "->"),

  // edge(<e_def>,   <e_gen>,   bend: 0deg, "->"),
  // edge(<c_def>,   <c_gen>,   bend: 0deg, "->"),
  // edge(<m_def>,   <m_gen>,   bend: 0deg, "->"),
  // edge(<q_i_def>, <q_i_gen>, bend: 0deg, "->"),
  // edge(<q_o_def>, <q_o_gen>, bend: 0deg, "->"),
  

  // 1 1! 1? n n! n?
  // edge(<e>, <j>, bend: 20deg, "1-n"),
  // edge(<j>, <m>, bend: 0deg, "1-n"),
  // edge(<m>, <Q>, bend: 20deg, "1-n"),
  
  // edge(<Q>, <q_i>, bend: 20deg, "1-n"),
  // edge(<Q>, <q_o>, bend: 20deg, "1-n"),

  // edge(<q_i>, <y>, bend: 20deg, "1-n"),
  // edge(<q_i>, <d>, bend: 20deg, "1-n"),
  // edge(<q_o>, <d>, bend: 20deg, "1-n"),
  // edge(<q_o>, <y>, bend: 20deg, "1-n"),

  // edge(<c>, <d>, bend: 0deg, "1-n"),
  // edge(<c>, <y>, bend: 0deg, "1-n"),

  // edge(<e>, <d>, bend:  20deg, "1-n"),
  // edge(<e>, <y>, bend: -20deg, "1-n"),

)

#box[
  #set text(size: 1.5em)
  #pipeline
]

pipeline

       




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
mapping e to m

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
mapping e to m sideways


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

mapping e to m full names


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

template