// Citations and quotes:
//
// Barry Boehm, "Software Engineering Economics" (Prentice-Hall, 1981), Table 4-1:
//   "Finding and fixing a software problem after delivery is up to 100 times more expensive
//   than finding and fixing it during the requirements and early design phases."
//   — The canonical cost-of-deferral argument: every uncommitted architectural decision is a
//   bet placed at worsening odds. Verified in NASA/JSC Error Cost Escalation report (NTRS
//   20100036670). Safe to cite as a direct quote.
//
// Bent Flyvbjerg & Dan Gardner, "How Big Things Get Done" (Crown Currency, 2023):
//   "Over budget, over time, under benefits — over and over again." (the "iron law")
//   Statistics: only 8.5% of projects hit both cost and time targets; only 0.5% achieve
//   cost, time, AND benefits. Solution: reference class forecasting — use empirical
//   distributions from comparable past projects, not inside-view optimism.
//
// Mike Cohn, "Agile Estimating and Planning" (Prentice Hall PTR, 2005), Ch. 4–5:
//   "Story points are a unit of measure for expressing an estimate of the overall effort
//   that will be required to fully implement a product backlog item or any other piece of
//   work." (verbatim from mountaingoatsoftware.com, mirrors book text)
//   Key argument: absolute estimates compound two uncertainties (size + time-allocation);
//   relative estimates isolate the one dimension teams can actually judge. Cite as finding
//   rather than page-level quote.
//
// Capers Jones, "Estimating Software Costs" 2nd ed. (McGraw-Hill, 2007), Preface:
//   "Software cost estimating is one of the most difficult tasks in the entire software
//   domain. Indeed, poor cost estimating is implicated in the majority of software projects
//   that come in over budget, over schedule, or are cancelled outright."
//   Empirical finding from ~13,000 projects: only ~15% of large software projects are
//   completed on time and within budget using manual estimation methods.
//   (Cite as attributed finding; the 15% figure is consistently from Jones's IFPUG papers.)

#let title = [Principled Methods for Sizing Work Before Committing to It]

#let body = [
Before a team commits to an architecture, a timeline, or a team structure, it needs a way to reason formally about the tradeoffs.
Scalability decisions made without cost models produce systems that are expensive to run at the wrong scale and expensive to change at the right one.
Effort estimates made without reference to historical data produce schedules that no one believes and everyone misses.

What is needed is not more estimation ceremony but a principled triage: a structured way to assess the scalability, cost, and effort implications of architectural choices before those choices harden into constraints.
]
