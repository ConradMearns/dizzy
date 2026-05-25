// Citations to consider:
// - Mearns (this work) — DIZZY data definitions and function interfaces
// - Sowa (1984) "Conceptual Structures" — formal ontology in software
// - Selman et al. (LinkML) — https://linkml.io / LinkML specification
// - Evans (2003) "Domain-Driven Design" — making implicit explicit
// - Fowler (2002) "Patterns of Enterprise Application Architecture" — data transfer objects, service interfaces
// - Kleppmann (2017) "Designing Data-Intensive Applications" — schema evolution, data contracts

#let title = [Explicit Schemas for All Data and Functions]

#let body = [
The most dangerous thing in a software system is the contract that no one wrote down.
Implicit assumptions about data shapes, calling conventions, and side effects accumulate silently until they break — and when they break, the error is far from the assumption that caused it.

DIZZY makes every @data contract and every @functions interface explicit and machine-readable.
There is no implicit coupling between components.
The schema of every @command, @event, @model, and @query is declared before any implementation is written, and those declarations are the authoritative specification from which implementations are derived.
]
