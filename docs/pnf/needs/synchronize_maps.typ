// Citations and quotes:
//
// Alfred Korzybski, "Science and Sanity" (1933), p. 58:
//   "A map is not the territory it represents, but, if correct, it has a similar
//   structure to the territory, which accounts for its usefulness."
//   — The qualifier "if correct, it has a similar structure" is load-bearing: the moment
//   correspondence breaks down, the map's usefulness collapses entirely.
//
// Eric Evans, "Domain-Driven Design" (Addison-Wesley, 2003):
//   "If developers don't realize that changing code changes the model, then their
//   refactoring will weaken the model rather than strengthen it."
//   — Names the exact drift failure mode: code changes silently erode the shared domain
//   model when model and code are treated as separate artifacts.
//
// Eric Evans, "Domain-Driven Design" (Addison-Wesley, 2003):
//   "Translation muddles model concepts and leads to destructive refactoring of code...
//   The effort of translation prevents the interplay of knowledge and ideas that lead to
//   deep model insights."
//   — Tolerating a gap between the language of the model and the language in code makes
//   the gap grow by design: the cognitive overhead of translation prevents correction.
//
// Ikujiro Nonaka & Hirotaka Takeuchi, "The Knowledge-Creating Company"
// (Oxford University Press, 1995), Ch. 3:
//   "Tacit knowledge is difficult to formalize and often time- and space-specific; it can
//   only be acquired by directly sharing work experiences."
//   — The structural reason architecture models drift: real system understanding lives as
//   tacit knowledge in developers' heads and resists capture in any explicit artifact.
//
// Note — Martin Fowler "PoEAA" (2002) and Russell Ackoff (1989): relevant but no
// independently verifiable verbatim quote surfaced. Fowler's PoEAA Ch. 1 ("the source
// code is the authoritative model of the system") and Ackoff's 1989 Journal of Applied
// Systems Analysis paper (16:3–9) are worth direct lookup if library access is available.

#let title = [Methods for Keeping the Map Synchronized with the Territory]

#let body = [
Every system starts with a map: a shared model of the domain, expressed in the vocabulary agreed on during design.
That map is wrong from the start — a simplification, necessarily — and it gets more wrong with every change to the system that is not reflected in the model.

Architecture needs mechanisms that detect and close the gap between the map and the territory on an ongoing basis: practices that treat the domain model not as a starting artifact but as a living document, and that make divergence between model and system visible before it becomes costly.
]
