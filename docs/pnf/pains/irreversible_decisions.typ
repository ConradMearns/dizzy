// Citations and quotes:
//
// Barry Boehm, "Software Engineering Economics" (Prentice-Hall, 1981), Table 4-1:
//   "Finding and fixing a software problem after delivery is up to 100 times more expensive
//   than finding and fixing it during the requirements and early design phases."
//   — The cost-of-deferral curve: every architectural assumption left implicit is a bet
//   placed at worsening odds. Verified in NASA/JSC Error Cost Escalation (NTRS 20100036670).
//
// Fred Brooks, "The Mythical Man-Month" (Addison-Wesley, 1975):
//   "How does a project get to be a year late? One day at a time."
//   — Irreversibility accumulates gradually: no single decision looks catastrophic,
//   but each one narrows the solution space a little further.
//
// Ward Cunningham, OOPSLA '92 (1992) — origin of technical debt metaphor:
//   "Shipping first-time code is like going into debt. A little debt speeds development
//   so long as it is paid back promptly with a rewrite... The danger occurs when the debt
//   is not repaid. Every minute spent on not-quite-right code counts as interest on that
//   debt. Entire engineering organizations can be brought to a stand-still under the
//   debt load of an unconsolidated implementation."
//   — Technical debt is compounding interest on deferred decisions; the longer they sit,
//   the more of the codebase grows around them and depends on them.
//
// Bent Flyvbjerg & Dan Gardner, "How Big Things Get Done" (Crown Currency, 2023):
//   "Over budget, over time, under benefits — over and over again."
//   — Cost overruns follow a fat-tailed distribution: small overruns are common,
//   catastrophic ones are far more frequent than normal distributions predict. The
//   pattern holds because early wrong assumptions compound through the entire project.
//
// Nicole Forsgren, Jez Humble & Gene Kim, "Accelerate" (IT Revolution Press, 2018), Ch. 2, p. 23:
//   "We believe this new work could be occurring at the expense of ignoring critical
//   rework, thus racking up technical debt which in turn leads to more fragile systems
//   and, therefore, a higher change fail rate."
//   — Empirically links deferred decisions (technical debt) to system fragility and
//   delivery failure. Verified verbatim from the IT Revolution Press excerpt PDF.

#let title = [Early Decisions Become Permanent Constraints]

#let body = [
Every software system is built on a foundation of decisions made before the system was understood.
Database chosen before the access patterns were known.
Framework chosen before the team size was known.
Deployment topology chosen before the load profile was known.
These decisions feel cheap when made — they are made quickly, under pressure, with incomplete information.

They do not stay cheap.
Each subsequent decision is made in the context of all prior decisions.
The code grows around the early choices, depending on them, hiding them, making them load-bearing.
By the time the wrong choice is visible, reversing it means reversing every decision that was built on top of it.
The system that felt like a foundation has become a cage.

This is not a failure of foresight.
No team has the information at project start that would make every early decision correct.
The failure is architectural: building systems that treat early decisions as permanent rather than as hypotheses to be tested and revised.
]
