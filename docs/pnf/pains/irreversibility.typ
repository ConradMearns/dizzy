#let title = [The Irreversibility of Poor Decisions]

#let body = [
Everything in computing changes - it's just a matter of _when_ the change occurs. Our demands change, our platforms, capabilities, problems, fashions, and scale all change too.

We often see, especially in the most cursed software projects, that poor decisions will rear their heads to haunt us again later on.

Decisions that seemed either well intentioned, necessary, critical, or even genuinely brilliant can all turn into a curse when the conditions are right. And truly - I don't know what is worse: the number of projects people have retained as sunk costs, due to pride or politics - or the number of people who seemingly have no awareness of the curses they write.

(Though, hindsight punishes the early architects all too often.
There are too many such cases, when a developer succumbs to the pressures of the labor. When they break, integrity breaks too. We see mitigations, shortcuts, hacks and sloppy writing apparent as the evidence of such mental slips and burnouts.)

A decent Software Architecture is a ward against such curses. It is the draft of constraints that prevent the workarounds, the dirty hacks, and the "clever" tricks that inevitably cause confusion and harm later. A decent architecture promotes modularity for the sake of repairability.

Poor Architectures are those that attract curses rather than features. They are those whose structure itself is vile physarum of traces that span dozens of files, and couples itself to hardcoded strings, special conditionals, and ancient rituals of practices and patterns of by-gone developers.

We call this "Coupling"

// TODO: What happens when your database choice, your deployment model, your
// programming language, and your business logic are all entangled?
// Give concrete examples of real-world pain:
// - "We can't migrate off Postgres because our business logic is in stored procedures"
// - "We can't rewrite the hot path in Rust because our types are Python-only"
// - "We can't split this monolith because the modules share a database"
// Each of these represents an irreversible decision that constrains all future decisions.

// Key points to develop:
// Everything in computing changes, it's just a matter of _when_.
// Many systems are implemented to solve for specific problems in software development,
// only to be usurped and made obsolete by advances in hardware development,
// or algorithms that change the objective completely.

// https://longnow.org/ideas/pace-layers/
]
