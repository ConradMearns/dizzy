// Citations to consider:
// - Taleb (2012) "Antifragile" — systems that gain from disorder
// - Hollnagel et al. (2006) "Resilience Engineering" — robustness vs. brittleness
// - Basili & Hutchens (1983) "An Empirical Study of a Syntactic Complexity Family" — early experimentation value
// - Hammant & Shore (2010) "The Art of Agile Development" — exploratory testing and spikes
// - Humble et al. (2014) "Lean Enterprise" — build-measure-learn, validated learning
// - Freeman & Pryce (2009) "Growing Object-Oriented Software, Guided by Tests" — iterative development

#let title = [From Vibe-Checking to Robustness Engineering]

#let body = [
Every durable system starts as an experiment.
The question "is this even worth building?" must be answerable cheaply — before teams commit to architecture, before schemas are defined, before pipelines are generated.
A philosophy that skips this stage is a philosophy for organizations that have already made up their minds, and it will be discarded the moment it demands rigor before understanding.

DIZZY provides a graduated path.
Vibe-checking is the deliberate, low-cost phase of exploration: scripts, sketches, and structured log piping that let teams validate domain assumptions before any DIZZY formalism is applied.
When the vibe checks out, the same structured thinking that guided the experiment becomes the input to the full DIZZY pipeline — @feature-file, schemas, generated interfaces, and deployed components.
The rigor is not a gate; it is a destination.
]
