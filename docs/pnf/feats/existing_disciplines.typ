#let title = [Existing Disciplines, New Composition]

#let body = [
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

== The Spectrum from Structured Logging to Event Sourcing

// TODO: Structured logging is for more than just debugging.
// There is a spectrum from Change Data Capture <-> Event Sourcing.
// Many teams are already halfway to event sourcing without knowing it.
// Help readers see the continuum and understand where DIZZY sits on it.

== Event Storming as the On-Ramp

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
]
