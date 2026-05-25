// Citations to consider:
// - Brandolini (2021) "Introducing EventStorming" — collaborative domain discovery
// - Knuth (1984) "Literate Programming" — code and documentation as one artifact
// - Adzic (2011) "Specification by Example" — executable specifications
// - Evans (2003) "Domain-Driven Design" — ubiquitous language as living artifact
// - Wilson et al. (2017) "Good Enough Practices in Scientific Computing" — reproducibility
// - Humble & Farley (2010) "Continuous Delivery" — everything as code

#let title = [Producing Code and Documentation Simultaneously]

#let body = [
The gap between what domain experts understand and what engineers build is widest at the moment of handoff — when the words spoken in a discovery session must become a specification that code can be written against.
Most methodologies treat this translation as an afterthought, producing design documents that are obsolete before the first line of code is written.

DIZZY closes this gap by making the workshop output directly executable.
The @feature-file produced during a workshopping session is simultaneously a domain description readable by stakeholders and a formal input to the code generation pipeline.
The same artifact that a product owner can review is the one that produces the typed interfaces engineers implement against.
No translation step; no handoff loss.
]
