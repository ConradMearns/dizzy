// Citations to consider:
// - Putnam & Myers (1992) "Measures for Excellence" — SLIM model, software dynamics equations
// - Norden (1958) — Rayleigh staffing curve / project effort distribution
// - Boehm (1981) "Software Engineering Economics" — COCOMO, cost of change curve
// - Yourdon (1992) "Decline and Fall of the American Programmer" — software metrics
// - Royce (1970) "Managing the Development of Large Software Systems" — original waterfall
// - Beck et al. (2001) "Agile Manifesto" — iterative development and responding to change
// - NVPSM: [define and cite Conrad's own framework here]

#let title = [Predictable Scaling with NVPSM: Between Agile and Waterfall]

#let body = [
The debate between Agile and Waterfall has consumed decades of software methodology discussion, and both sides lose sight of the same thing: predictability is not about the process, it is about the model.
A team that can reason formally about how effort, cost, and team size interact as a system grows can make good scheduling decisions whether they call themselves Agile or not.
A team without such a model will fail regardless of ceremony.

DIZZY's explicit component structure enables formal application of the NVPSM framework: because the flows of a DIZZY system are enumerable and each component is a bounded unit of work, the relationship between scope, staffing, and schedule becomes tractable in ways that are impossible when execution paths are implicit.
]
