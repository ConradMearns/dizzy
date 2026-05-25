// Citations and quotes:
//
// Eric Ries, "The Lean Startup" (Crown Business, 2011):
//   "The big question of our time is not Can it be built? but Should it be built?
//   This places us in an unusual historical moment: our future prosperity depends on
//   the quality of our collective imaginations."
//   — Names the inversion directly: the field's default question is the wrong one.
//   Validated learning answers "should it?" before "how?" consumes the budget.
//
// Donald G. Reinertsen, "The Principles of Product Development Flow"
// (Celeritas Publishing, 2009), p. 32:
//   "If you only quantify one thing, quantify the Cost of Delay."
//   — Deferring validation until late in development is not free; it has a compounding
//   price that most teams never measure. Making that cost visible is the first step
//   toward front-loading the validation that would have prevented it.
//
// Mary & Tom Poppendieck, "Lean Software Development" (Addison-Wesley, 2003):
//   "Decide as late as possible."
//   — One of the seven core lean principles. Often misread as license to delay action;
//   the Poppendiecks mean the opposite: preserve options by not committing to a solution
//   before the requirement is validated. Building before validating is deciding too early.
//
// Karl Popper, "The Logic of Scientific Discovery" (Routledge, 1959;
// translated from "Logik der Forschung," 1934):
//   "I shall certainly admit a system as empirical or scientific only if it is capable
//   of being tested by experience. These considerations suggest that not the verifiability
//   but the falsifiability of a system is to be taken as a criterion of demarcation."
//   — Applied to requirements: a requirement that cannot be expressed in a testable form
//   is not a requirement — it is a belief. Structured validation (acceptance criteria,
//   executable examples) is not bureaucracy; it is epistemology.
//
// Nicole Forsgren, Jez Humble & Gene Kim, "Accelerate" (IT Revolution Press, 2018), Ch. 2, p. 15:
//   "Shorter product delivery lead times are better since they enable faster feedback
//   on what we are building and allow us to course correct more rapidly."
//   — Frames short feedback cycles as the mechanism for catching wrong assumptions
//   before they harden. Verified verbatim from the IT Revolution Press excerpt PDF.
//
// Note — Gojko Adzic, "Specification by Example" (Manning, 2011):
//   Relevant throughout but no tight verbatim quote surfaced from public web sources.
//   Pull directly from the book; the "specifying collaboratively" and "illustrating
//   using examples" principles in Ch. 2 and 6 are the strongest anchors.

#let title = [Validate the Problem Before Committing to a Solution]

#let body = [
The question that consumes most of a team's energy — how do we build this? — is only worth asking once a prior question has been answered: should we build this at all?

Most development processes have no formal mechanism for the prior question.
Requirements are gathered, designs are produced, and implementation begins — all before any structured attempt is made to verify that the requirement reflects an actual need, that the design solves the stated problem, or that the problem is the one worth solving.
By the time the wrong answer becomes visible, it is embedded in a codebase.

The cost of unvalidated assumptions does not stay fixed.
Each layer of code built on an unvalidated requirement makes the requirement harder to change.
Each integration test written against a misunderstood specification hardens the misunderstanding into infrastructure.
Validation deferred is validation made expensive.

This problem is not new, but its severity is increasing.
AI-assisted development can now generate working, tested, documented implementations in hours.
That capability is transformative when the requirement is correct.
When it is wrong, it produces confident implementations of the wrong thing at a speed that outpaces any team's capacity to catch the error before it compounds.
The bottleneck is no longer building — it is knowing what to build.
Architecture must provide a formal answer to that problem before the build begins.
]
