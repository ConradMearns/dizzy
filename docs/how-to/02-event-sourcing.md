01 Discusses the main architecture loop, and the core pieces for building a value flow,
but it's missing the details that enable it to compete with traditional architectures: databases.

The Dizzy Architecture is focused on Event Sourcing as the primary way information and facts get recorded.

At the same time - dizzy does not prescribe event sourcing or any specific technologies to accomplish this,
event sourcing must still be implemented by hand - or can be ignored if not needed. 

The principal of event sourcing is that we ought to be able to record a list of all events as they occured,
and then use them to regenerate databases as needed later.

For connecting databases to our system, we follow CQRS principals.
However, to do this, we need to model the Domain Entities that are related to the Events that change them.

The goal in this phase is not to create the "golden" entity schema - but rather, the most useful.
Often, we encounter multiple situation in a project where we may want the information which we have recorded to be represented in very different ways.
For example: do we need a graph to be represented by an adjacency matrix, an adjacency list, or a tuple of nodes and edges?
This answer depends solely on the algorithm used within the Procedure - and so we may not want to commit to any single representation.

By this, we aim to solve our issue by allowing the database systems to be a part of the implementation.
We decide to ignore the past 30 years of Object Oriented practices of layering and abstraction -
because often they prematurely ruin preformance and disallow future architectual changes.

The "facts" we store should be presented in a trusted and well established Event Store - an append only log.

The domain entity representations are merely snapshots of the culmination of facts, presented within a very particular machine. They are useful, but not perfect.

# Getting Started - Writing Procedures

To begin building this aspect of our system, start with the Procedures.
It's best to imagine each slice of the system seperately - and these aspects can be easily unit-tested because they require no state and no external dependencies that aren't already defined in the context.

Given a command, and some ideal Domain Entity - preform the work and emit the required Events to make a good test.
Allow yourself the freedom to derive the simplest (and perhaps overly-naive) domain entities first.

# Expanding to Databases - Writing Queriers (and Drivers ?)

The next series of tests should not be ran all the time - they should be for occasional integration testing.
At this point, we may want to manually constuct an entity withing a database (such as Postgres, DuckDB, Neo4j, etc) via a test,
and then begin to write a Querier

A querier is the simplest API you can make for _reading_ from a database.
A class is the easiest way to build one - but a functional approach can work just as well.
The API should hold no state (other that connection information - but this can always be baked into a partial function)

The functions provided should be built similarly to GraphQL queries. When providing inputs for complex queries, write an Input object.
Use ID's to refer to specific entities.

It's enough to write a Querier like "TodoListItemQuerierForDuckDB" - but if many of the same type of databse (all SQL for example),
you may consider creating a layer to abstract out the API layer from the Database Driver Layer.

Once the querier is started, it can be added to a ProcedureContext.

> Between Queriers and Mutators, ONLY Queriers can slot into a ProcedureContext!

At this point, you now have tests and fake data within real databases - you should be able to test all procedures manually.

(For more testing, consider writing a mock database that holds objects in-memory)

# Writing Mutators

Writing mutators is easier once queriers have been started. 
The entry point for all mutators is the Policy. Since Procedures themselves can never call to a mutator, they have to go somewhere!

Thew language is roughly When X Event happens, do Y command - and this holds true for mutations as well.
Policies are meant to be very simple.
Often, they will contain very little code at all - maybe a conditional.

Once an event activates a policy, it can call a mutation and change a database state before issuing new commands.

A conditional can be used to catch errors and issue new commands.