#let title = [Addressing the Hard Problems]

#let body = [
// TODO: Be honest about the challenges. Event sourcing has well-known
// difficulties. Addressing them head-on builds credibility.

== Schema Evolution and Event Versioning

// TODO: Events are immutable, but schemas evolve. How does DIZZY handle
// adding fields, renaming events, or changing event semantics over time?

== Eventual Consistency

// TODO: Models are eventually consistent with the event store. What does
// this mean in practice? What are the failure modes? When is eventual
// consistency acceptable, and when do you need stronger guarantees?
// How does DIZZY help teams reason about consistency boundaries?

== Event Store Growth and Snapshots

// TODO: The event store grows without bound. What strategies exist for
// managing this? Snapshotting, compaction, archival. How does DIZZY's
// projection-rebuilding model interact with these strategies?

== Ordering and Distribution

// TODO: When events are processed across distributed nodes, ordering
// guarantees become complex. What ordering guarantees does DIZZY provide?
// What does it leave to the infrastructure? How should teams reason about
// causal ordering vs. total ordering?

== Change Propagation: The Arrows Point Backwards

// TODO: When you modify a component (add a field to a command, change an event),
// the ripple effects propagate backwards through the dependency graph. DIZZY
// tracks these relationships so you get an explicit list of everything affected.
// "The arrows propagate backwards when you add code elements or functionalities
// to your feature. And that's where that like high relational aspect comes in."
// This is the concrete mechanism behind "making changes responsibly."
// (See transcript 42:12 - 42:43)

== Sagas and Long-Running Processes

// TODO: Some business processes span multiple commands and events over time.
// Durable execution
// Show an example where Event Started - Event Ended - Event Failed
// Entity ID's
]
