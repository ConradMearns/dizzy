// Citations and quotes:
//
// Eric Evans, "Domain-Driven Design" (Addison-Wesley, 2003):
//   "The effort of translation prevents the interplay of knowledge and ideas that leads
//   to deep model insights."
//   — Names the mechanism directly: every translation between domain language and code
//   destroys the conceptual fidelity needed to build correct software.
//
// Eric Evans, "Domain-Driven Design" (Addison-Wesley, 2003), Ch. 1 "Crunching Knowledge":
//   "Effective domain modelers are knowledge crunchers. They take a torrent of information
//   and probe for the relevant trickle. They try one organizing idea after another, searching
//   for the simple view that makes sense of the mass."
//   — Frames deep domain understanding as an exceptional, effortful skill — implying that
//   most software is built without it.
//
// Fred Brooks, "The Mythical Man-Month" (Addison-Wesley, 1975):
//   "Men and months are interchangeable commodities only when a task can be partitioned
//   among many workers with no communication among them. This is true of reaping wheat or
//   picking cotton; it is not even approximately true of systems programming."
//   — Establishes that software requires dense communication for shared understanding;
//   adding translators between domain and code compounds knowledge loss exponentially.
//
// Karl Wiegers & Joy Beatty, "Software Requirements" 3rd ed. (Microsoft Press, 2013):
//   "Errors introduced during requirements activities account for 40 to 50 percent of all
//   defects found in a software product."
//   — Quantitative anchor: nearly half of all defects trace to the domain translation phase,
//   before a single line of code is written.
//
// Alberto Brandolini, variously attributed to talks and "Introducing EventStorming"
// (Leanpub, 2017–present) — wording varies across sources, cite as paraphrase:
//   "It is not the domain experts' knowledge that goes into production. It is the
//   developers' assumption of that knowledge that goes into production."
//   — The sharpest encapsulation of the pain: what transfers in an informal handoff is
//   not shared understanding but each engineer's private misinterpretation of it.

#let title = [Domain Knowledge Doesn't Survive the Translation to Code]

#let body = [
The people who understand a problem most deeply — the domain experts, the operators, the scientists — almost never write the code.
And the engineers who write the code almost never develop the depth of domain understanding needed to make good architectural choices.
Every handoff between these two groups is an opportunity for meaning to be lost, and over the life of a system, those losses compound.

The code drifts from the domain model.
The domain model drifts from the domain.
And the software that results serves neither the experts who understand the problem nor the engineers who implemented it well.
]
