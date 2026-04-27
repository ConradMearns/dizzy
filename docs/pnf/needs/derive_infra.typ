#let title = [Derive Infrastructure _from_ Code]

#let body = [
// TODO: Expand on the idea of #strike[Infrastructure as Code] -> Infrastructure _from_ Code.
// Rather than separately defining infrastructure and hoping it matches your code,
// introduce as "interstitial architecture"

DIZZY derives infrastructure requirements separate from the domain model.

Just as Programming Languages translate human intent to machine code - so too should DIZZY translate business intent to infrastructure. Automatically, with optimizations for infrastructure that can be refined out of phase with business needs - just as GCC can improve compilation and optimizations without requiring changes to C.

DIZZY calls this an Interstitial Infrastructure. The goal is to treat Interstitial Infrastructure as a compilation problem.

Infrastructure decisions are the final step in a DIZZY deployment, and enable DIZZY to be built as either a monolith, microservices, or something in between.

Commands, Events, and Models are data. They can be communicated over any number or combinations of message passing channels, such as ZeroMQ, Kafka, HTTP, WebSocket, gRPC, etc.

The deployment of Processes support any potential target as long as it can satisfy channel connectivity requirements.
]
