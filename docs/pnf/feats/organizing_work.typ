#let title = [Organizing Work: From Architecture to Work Breakdown]

#let body = [
// TODO: One of DIZZY's underappreciated benefits is how it structures
// the work of building software, not just the software itself.

== Countable Flows, Not Spaghetti Traces

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

== Components as Work Units

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

== The Technical Lead's View

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

== Agents and Automated Workers

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
]
