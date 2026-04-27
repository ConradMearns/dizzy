#let title = [The Same Data, Described a Dozen Times]

#let body = [
// TODO: The same domain primitives (a user, an order, a transaction) get
// redefined in Pydantic, SQL Alchemy, Protobuf, Rust structs, JSON schemas --
// each slightly different, each drifting out of sync. This isn't just tedious;
// it's a breeding ground for subtle bugs. And the underlying data types are
// often wrong too -- doubles for currency, 64-bit integers for 8-bit port numbers.
// The tooling doesn't prevent this; it multiplies it.
// (See transcript 34:18 - 35:36)
]
