// Citations and quotes:
//
// Eric Evans, "Domain-Driven Design" (Addison-Wesley, 2003), Ch. on Ubiquitous Language:
//   "A project faces serious problems when its language is fractured. Domain experts use
//   their jargon while technical team members have their own language tuned for discussing
//   the domain in terms of design. The terminology of day-to-day discussions is disconnected
//   from the terminology embedded in the code (ultimately the most important product of a
//   software project). Translation blunts communication and makes knowledge crunching
//   anemic."
//   — Diagnoses precisely why informal conversation fails: without a formal shared language
//   anchored in durable artifacts, the gap between experts and engineers corrupts the code.
//
// Alberto Brandolini, variously attributed to talks and "Introducing EventStorming"
// (Leanpub, 2017–present) — cite as paraphrase, wording varies across sources:
//   "It is not the domain experts' knowledge that goes into production. It is the
//   developers' assumption of that knowledge that goes into production."
//   — The case for structured artifacts: informal conversation transfers assumptions,
//   not understanding.
//
// Gojko Adzic, "Specification by Example" (Manning, 2011), Ch. 2 & 6:
//   "Specification by Example is a collaborative method for specifying requirements
//   and tests."
//   Core argument: informal requirements discussions produce no usable artifact; only
//   collaborative, example-driven specifications — executable and readable by both business
//   and engineering — survive the development process as "living documentation."
//
// Gene Kim, Jez Humble, Patrick Debois & John Willis, "The DevOps Handbook"
// (IT Revolution Press, 2016), Part II (The Second Way — Feedback):
//   "The goal is to shorten and amplify feedback loops so that necessary corrections can
//   be continually made."
//   — Frames absent or slow feedback between business and engineering as an organizational
//   failure mode; structured stakeholder engagement is the mechanism that makes feedback
//   loops short, visible, and durable.

#let title = [A Formal Process for Stakeholder Engagement and Communication]

#let body = [
A conversation between a domain expert and an engineer is not an artifact.
When it ends, the understanding it produced exists only in two people's heads — and those heads diverge from each other with every day that passes.

Software development needs structured practices for stakeholder engagement that produce durable, shared artifacts: artifacts that are readable by the domain expert, actionable by the engineer, and authoritative enough that both parties can return to them when disagreements arise.
Without such a process, the stakeholder relationship is reset with every new conversation.
]
