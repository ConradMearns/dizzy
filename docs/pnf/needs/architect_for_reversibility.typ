#let title = [Architect for Reversibility]

#let body = [
Reversibility is about maintaining the freedom to respond to new information.

DIZZY should not only empower modularization of our system, it should naturally enable A/B testing and hotswapping so that reversing decisions becomes a standard practice, rather than a hail mary.

Consider the questions that haunt every long-lived system.
What if the database vendor raises prices or discontinues the product?
What if the chosen query model turns out to be wrong for the data?
What if the deployment topology is generating too high of an operational cost?

In most architectures these are existential questions —
answering them requires rewriting code that should never have known about infrastructure in the first place.

// TODO: DIZZY's goal is to make them routine.
// Because domain logic never knows which database backs its Models or which channel carries its Events,
// swapping one for another is a deployment concern, not a development one.
]
