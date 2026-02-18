#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge

#set page(margin: 2cm)
#set text(size: 10pt)

// Helper function to create table-like content for database tables
#let db-table(title, fields) = {
  set align(left)

  table(
    columns: 1,
    // stroke: none,

    table.header(
      [
      #table.cell(
        [*#text(size: 9pt, title)*])
      ],
    ),

    table.cell(
      text(size: 7.5pt, font: "DejaVu Sans Mono", fields.join(linebreak()))
    ),
  )
}

= Database Diagram: Cart System

#diagram(
  node-shape: rect,
  node(circle(stroke: white, text(white, $Delta$)), name: <A>, fill: navy),
  node(<A.north-east>, circle(fill: white, radius: 6pt, $ plus.o $)),
  edge((<A.north-west>, 25%, <A.south-west>,), "l,u,l", "-O"),
  edge((<A.north-west>, 50%, <A.south-west>), "l,l", "-@"),
  edge((<A.north-west>, 75%, <A.south-west>), "l,d", "-O"),
  edge((<A.north-west>, 2%, <A.south-west>), "r,r,dr", "-O"),
)

#diagram(
  spacing: (3cm, 2.5cm),
  node-stroke: 1pt,
  edge-stroke: 1pt,
  node-inset: 0pt,

  node((0, 0),
    db-table("Users", (
      "user_id",
      "username",
      "email",
      "password_hash",
      "created_at"
    )),
    shape: rect,
    // width: 3cm,
    name: <users>
  ),

  node((1, 0),
    db-table("Carts", (
      "PK: cart_id",
      "FK: user_id",
      "status",
      "created_at",
      "updated_at"
    )),
    shape: rect,
    width: 4cm,
    name: <carts>
  ),

  node((2, 0),
    db-table("Products", (
      "PK: product_id",
      "name",
      "description",
      "price",
      "stock_quantity",
      "created_at"
    )),
    shape: rect,
    width: 4cm,
    name: <products>
  ),

  // Row 2: CartItems
  node((1, 1),
    db-table("CartItems", (
      "PK: cart_item_id",
      "FK: cart_id",
      "FK: product_id",
      "quantity",
      "added_at"
    )),
    shape: rect,
    width: 4cm,
    name: <cart_items>
  ),

  // Row 3: Orders, OrderItems
  node((0, 2),
    db-table("Orders", (
      "PK: order_id",
      "FK: user_id",
      "FK: cart_id",
      "total_amount",
      "status",
      "created_at"
    )),
    shape: rect,
    width: 4cm,
    name: <orders>
  ),

  node((1, 2),
    db-table("OrderItems", (
      "PK: order_item_id",
      "FK: order_id",
      "FK: product_id",
      "quantity",
      "price_at_time"
    )),
    shape: rect,
    width: 4cm,
    name: <order_items>
  ),

  // Relationships with arrows
  edge(<users>, <carts>, "->", [1:\*]),
  edge(<carts>, <cart_items>, "->", [1:\*]),
  edge(<products>, <cart_items>, "->", [1:\*], bend: -20deg),
  edge(<users>, <orders>, "->", [1:\*]),
  edge(<carts>, <orders>, "->", [1:0..1], bend: 20deg),
  edge(<orders>, <order_items>, "->", [1:\*]),
  edge(<products>, <order_items>, "->", [1:\*], bend: 20deg),

)

#v(1cm)

*Legend:*
- PK = Primary Key
- FK = Foreign Key
- 1:\* = One-to-Many relationship
- 1:0..1 = One-to-Zero-or-One relationship
