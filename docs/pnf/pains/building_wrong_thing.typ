// Citations and quotes:
//
// Standish Group, CHAOS Report 2020:
//   Of the 19% of projects that failed outright, cancellation — not technical failure —
//   was the primary cause. The system was delivered (or nearly so) and found to be wrong.
//   The 50% of "challenged" projects frequently delivered reduced scope not because the
//   team ran out of time but because the original scope was discovered to be unnecessary.
//
// Gojko Adzic, "Specification by Example" (Manning, 2011):
//   "Specification by Example is a collaborative method for specifying requirements
//   and tests."
//   — The implicit argument: without executable, collaboratively validated specifications,
//   the default is for teams to build confident implementations of the wrong requirements.
//
// Eric Ries, "The Lean Startup" (Crown Business, 2011):
//   "The question is not 'Can this product be built?' In the modern economy, almost any
//   product that is imagined can be built. The more relevant questions are 'Should this
//   product be built?' and 'Can we build a sustainable business around this set of
//   products and services?'"
//   — Execution capability has far outrun validation capability; the bottleneck is no
//   longer building, it is knowing what to build.
//
// Nicole Forsgren, Jez Humble & Gene Kim, "Accelerate" (IT Revolution Press, 2018), Ch. 2, pp. 23–24:
//   "Astonishingly, these results demonstrate that there is no tradeoff between improving
//   performance and achieving higher levels of stability and quality. Rather, high
//   performers do better at all of these measures. This is precisely what the Agile and
//   Lean movements predict, but much dogma in our industry still rests on the false
//   assumption that moving faster means trading off against other performance goals,
//   rather than enabling and reinforcing them."
//   — Challenges the speed/quality tradeoff assumption directly: teams that move fast
//   *and* build the right thing are not exceptional outliers — they are the natural result
//   of correct process. Verified verbatim from the IT Revolution Press excerpt PDF.
//
// Note — AI development context:
//   AI-assisted code generation amplifies this pain acutely. A model can produce
//   plausible-looking implementations of wrong requirements with high confidence and
//   high velocity. The faster the generation, the faster the wrong thing gets built,
//   tested, and shipped. Correctness validation becomes the rate-limiting step, not
//   implementation. No citation needed — this is an argument to be made directly.

#let title = [We Build the Wrong Thing, Faster Every Year]

#let body = [
A project can be delivered on time, within budget, with every feature on the roadmap — and still be completely wrong.
The software solves a problem the users do not have, in a way they would never choose, optimizing for metrics that do not reflect value.
This failure mode is distinct from the project management failures of cost and schedule: a project can pass every delivery milestone and still be a total waste.

The gap between "did we build it right?" and "did we build the right thing?" has always existed.
What has changed is the speed at which the wrong thing can be built.
AI-assisted development collapses the time between a requirement and a working implementation.
That is an enormous capability when the requirement is correct.
When it is wrong — when the problem is misunderstood, the stakeholder misheard, the specification ambiguous — the same speed produces confident, well-tested, thoroughly documented wrong software at a rate previously impossible.

Velocity without validation is not progress.
It is the acceleration of error.
]
