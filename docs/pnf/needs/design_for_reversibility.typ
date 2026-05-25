// Citations and quotes:
//
// Mary & Tom Poppendieck, "Lean Software Development: An Agile Toolkit"
// (Addison-Wesley, 2003):
//   "Delay commitment until the last responsible moment, that is, the moment at which
//   failing to make a decision eliminates an important alternative."
//   — The canonical formulation of deferring irreversible decisions: commitment is not
//   free, and premature commitment forecloses options whose value hasn't been measured.
//
// Martin Fowler, "StranglerFigApplication" (martinfowler.com, June 2004):
//   "An alternative route is to gradually create a new system around the edges of the
//   old, letting it grow slowly over several years until the old system is strangled."
//   — The practical proof that infrastructure decisions *can* be reversed — incrementally,
//   without a big-bang rewrite — provided the system's seams allow rerouting.
//   Source: https://martinfowler.com/bliki/StranglerFigApplication.html
//
// Michael Feathers, "Working Effectively with Legacy Code" (Prentice Hall, 2004), p. 31:
//   "A seam is a place where you can alter behavior in your program without editing in
//   that place."
//   "Every seam has an enabling point, a place where you can make the decision to use
//   one behavior or another."
//   — Defines the structural precondition for reversibility: without seams, every early
//   infrastructure choice is load-bearing and cannot be replaced without modification.
//
// Robert C. Martin, "The Open-Closed Principle" (C++ Report, January 1996);
// also in "Agile Software Development" (Prentice Hall, 2002):
//   "Software entities (classes, modules, functions, etc.) should be open for extension,
//   but closed for modification."
//   Source: https://www.cs.utexas.edu/~downing/papers/OCP-1996.pdf
//   — The design-level mechanism for reversibility: a module whose behavior can be
//   extended (swap a database adapter) without modifying its domain logic keeps
//   infrastructure decisions permanently changeable.
//
// Nicole Forsgren, Jez Humble & Gene Kim, "Accelerate" (IT Revolution Press, 2018), Ch. 5:
//   "We found that high performance is possible with all kinds of systems, provided
//   that systems—and the teams that build and maintain them—are loosely coupled."
//   — The book's primary architectural finding: coupling is the determining structural
//   variable, not stack, age, or language. High confidence; consistently cited from Ch. 5
//   across multiple independent sources (Goodreads, DORA.dev, book reviews).
//
// Note — Eric Evans, "Domain-Driven Design" (2003), Ch. 14 (Anti-Corruption Layer):
//   The anti-corruption layer concept is well-established but the exact prose is not
//   safely verifiable from public web sources. Pull directly from the book before citing.

#let title = [Design Systems So Infrastructure Decisions Can Be Reversed]

#let body = [
The decision that felt cheap at project start — which database, which message broker, which deployment model — is cheap precisely because it has not yet been built around.
The moment code grows against it, dependencies accumulate on top of it, and team habits form around it, the cost of reversal compounds.
Within months, what was a choice is a constraint.
Within years, it is the foundation.

Architecture must treat early decisions as hypotheses, not commitments.
This requires deliberate seams: explicit boundaries between the logic of the domain and the infrastructure that serves it.
When domain logic does not know what database backs a model or what queue carries a command, those choices remain choices — they can be swapped, upgraded, or replaced as requirements evolve and better options emerge.

The discipline is not to defer decisions indefinitely, but to defer them to the last responsible moment — the moment at which further deferral would itself close off options.
Before that moment, the system should be structured to make the eventual choice easy.
After it, the choice should be made cleanly, with its consequences isolated to the infrastructure layer and invisible to the domain.
]
