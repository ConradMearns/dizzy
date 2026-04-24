# Whitepaper Requirements

These requirements define what the DIZZY whitepaper must satisfy.
They are intentionally testable — each one can be evaluated against the document
and assigned a pass, partial, or fail verdict.

The whitepaper is a **philosophy and motivation document**. It is not a specification.
Its job is to make a reader care about DIZZY and understand what it is at a conceptual level.
The companion _DIZZY Specification_ handles "how."

---

## Audience

The target reader is a software practitioner or technical decision-maker who has never
heard of DIZZY. They should finish the paper with:
- A clear sense of the problem DIZZY addresses
- An understanding of DIZZY's six core concepts and their roles
- Enough conviction in the philosophy to want to read the Specification

---

## Requirements

### WP-001: Abstract is Present and Complete
**Category:** Structure  
**Statement:** The paper must have a non-empty Abstract section that stands alone.  
**Pass:** Abstract exists, is prose (not a TODO or stub), and answers: what problem DIZZY solves, who it's for, and what the reader will take away.  
**Fail:** Abstract is missing, empty, or consists only of comments/placeholders.

---

### WP-002: All Section Headings are Complete
**Category:** Structure  
**Statement:** Every heading must be a complete phrase or sentence.  
**Pass:** No heading is a sentence fragment or ends mid-thought.  
**Fail:** Any heading reads as incomplete (e.g. "The Burden of Software Architecture is").

---

### WP-003: No Visible Draft Artifacts
**Category:** Presentation  
**Statement:** The compiled PDF must contain no TODO comments, raw URLs embedded in prose, or placeholder text.  
**Pass:** Compiled output is clean. Source-level `//` comments are fine and do not count.  
**Fail:** Any TODO, stub, or bare URL appears in the rendered document.

---

### WP-004: No Implementation Specifics
**Category:** Scope  
**Statement:** The paper must not explain how any DIZZY component is implemented, configured, or wired together.  
**Clarification:** Mentioning a technology by name as an example is permitted. Explaining how to use it is not.  
**Examples of allowed:** "Events can be routed over a message queue such as Kafka or ZeroMQ."  
**Examples of not allowed:** Explaining how an emitter callback maps to a Kafka topic, how a context object is injected, how gRPC channels are configured.  
**Pass:** No section instructs the reader on implementation mechanics.  
**Fail:** Any section explains function signatures, callback injection, channel routing, or infrastructure configuration.

---

### WP-005: Core Ontology is Introduced
**Category:** Content  
**Statement:** The paper must introduce and define all six DIZZY concepts at a conceptual level.  
**Required concepts:** Commands, Events, Procedures, Policies, Projections, Models, Queriers, Queries (Query Inputs and Query Outputs).  
**Pass:** Each concept is named and its role described in plain language. A reader could explain each back to you after reading.  
**Fail:** Any concept is omitted, only implied, or described in implementation terms rather than conceptual ones.

---

### WP-006: Infrastructure Choices are Framed as Deferred
**Category:** Philosophy  
**Statement:** The paper must convey that infrastructure choices (database, message broker, deployment topology) are intentionally deferred — not prescribed.  
**Pass:** The paper explicitly states that DIZZY does not mandate specific infrastructure and that choices are made at a later layer.  
**Fail:** The paper implies a specific infrastructure stack is required, or omits the deferral principle entirely.

---

### WP-007: Problem Statement Precedes Solution
**Category:** Structure  
**Statement:** The paper's problem sections must diagnose without proposing DIZZY as the solution. The solution framing belongs in later sections.  
**Pass:** Section 1 (or equivalent problem section) focuses purely on articulating the pain. DIZZY is not mentioned as an answer until Section 2 or later.  
**Fail:** DIZZY is introduced as the fix inside the problem-diagnosis sections.

---

### WP-008: Self-Contained Without Prior Knowledge
**Category:** Accessibility  
**Statement:** A reader with no prior DIZZY exposure must be able to follow the paper without consulting external documents.  
**Pass:** All terms are explained or are standard industry terms. No section assumes familiarity with the DIZZY Specification or prior versions.  
**Fail:** Undefined jargon appears, or sections implicitly require knowledge from another document.

---

### WP-009: Relationship to Existing Disciplines is Acknowledged
**Category:** Credibility  
**Statement:** The paper must acknowledge that DIZZY builds on established disciplines rather than claiming to invent them.  
**Minimum required:** CQRS and Event Sourcing must be named.  
**Pass:** At least two prior disciplines are cited with a clear statement that DIZZY composes rather than replaces them.  
**Fail:** The paper presents DIZZY's ideas as novel inventions without situating them in existing practice.

---

### WP-010: Events are Described as Immutable and Authoritative
**Category:** Content  
**Statement:** The paper must convey that events are the single source of truth and cannot be altered after the fact.  
**Pass:** Immutability and authoritative status of events is stated explicitly.  
**Fail:** Events are described ambiguously, as one of several truth sources, or as mutable records.

---

### WP-011: Reversibility is a Named Principle
**Category:** Philosophy  
**Statement:** The ability to reverse infrastructure and deployment decisions without touching business logic must be presented as a first-class design goal.  
**Pass:** Reversibility is named as a principle and explained in terms of what it enables (e.g., swapping databases, changing deployment topology).  
**Fail:** Reversibility is implied but never named, or is absent entirely.

---

### WP-012: Conclusion is Present and Complete
**Category:** Structure  
**Statement:** The paper must end with a non-empty conclusion that closes the argument.  
**Pass:** Conclusion exists in prose, references the thesis, and directs the reader toward next steps (e.g., the Specification).  
**Fail:** Conclusion is missing, empty, or a stub.

---

### WP-013: No Duplicate Content
**Category:** Presentation  
**Statement:** No figure, paragraph, or substantive passage should appear more than once in the compiled output.  
**Pass:** Each piece of content appears exactly once.  
**Fail:** Any figure or block of prose is repeated.

---

### WP-015: The Generation Pipeline is Described as a Philosophy, Not a Technical Process
**Category:** Content  
**Statement:** The paper must describe the journey from domain discovery to a deployable library artifact as a philosophical sequence of concerns, not a technical how-to.  
**The sequence to convey:**  
1. Domain thinking happens first — on whiteboards, in conversation, with subject matter experts — without requiring software engineers or code.  
2. Event Storming (or equivalent discovery) produces the shape of the system: what commands are issued, what events occur, what policies react.  
3. From that shape, schemas for the domain objects (commands, events, models, etc.) can be scaffolded and then populated with specifics.  
4. From those schemas, function protocols are generated — the typed interfaces that define what each procedure, policy, projection, and querier must do.  
5. Those protocols are packaged as a library artifact — a concrete, importable boundary between the business logic layer and the infrastructure layer.  
6. Engineers implement against that library. The library does not change unless the domain definitions change. Infrastructure cannot silently break the logical business layer.  
**Key philosophical point to land:** The library is the handoff. It allows domain experts and software engineers to work at different times, in different concerns, without stepping on each other. The hard part of the program — the logic — is reasoned about in the language of the domain, not in the language of infrastructure.  
**Pass:** The paper conveys this sequence and its philosophical significance without explaining how any specific tool, schema language, or infrastructure component works.  
**Fail:** The section either becomes a technical tutorial, omits the handoff concept entirely, or frames the pipeline as a feature of a specific tool rather than a consequence of the philosophy.

---

### WP-016: LinkML is Presented as a First-Class Part of the Philosophy
**Category:** Content / Exception to WP-004  
**Statement:** LinkML is an approved named technology in the whitepaper and should be presented as a core philosophical choice, not merely a tool mention. Kafka is also permissible as an illustrative example of a message queue.  
**Why LinkML is different:** LinkML represents a language-agnostic way to define domain schemas — exactly what DIZZY requires. Naming it is not a technical specification detail; it is a philosophical stance about how domain contracts should be written. The paper should make a genuine case for LinkML as the right kind of tool for this problem: it produces schemas that are not tied to any one programming language, framework, or runtime.  
**Pass:** LinkML is named, its role explained (language-agnostic schema definition), and the paper advocates for it with conviction. Kafka appears at most as a parenthetical example of a message queue.  
**Fail:** LinkML is absent, mentioned only in passing without advocacy, or treated the same as any other named technology. Kafka or any other infrastructure technology is explained in operational detail.

---

### WP-017: Language Agnosticism is an Explicit Goal
**Category:** Philosophy  
**Statement:** The paper must make clear that the generation pipeline produces library artifacts for multiple programming languages — not just one — and that this multi-language output is the mechanism by which DIZZY achieves programming language independence.  
**Key point to convey:** The reason for defining domain objects in a language-agnostic schema (LinkML) is precisely so that the contracts can be compiled into native libraries for Python, Rust, TypeScript, Go, or any other target. Teams working in different languages can each receive a library that speaks their language while conforming to the same domain contract.  
**Pass:** The paper names multi-language generation as an explicit goal and connects it to the language-agnosticism principle. A reader understands that the library artifact is not a single file but a family of generated outputs.  
**Fail:** The paper implies or states that a single language or runtime is required, or omits the multi-language generation goal entirely.

---

### WP-014: Readable Without the Flow Diagram
**Category:** Accessibility  
**Statement:** The paper's argument must be followable even if figures are not rendered.  
**Pass:** Every figure has a caption and the surrounding prose does not rely on the figure to carry meaning.  
**Fail:** A section's argument is incomprehensible without the figure.

---

### WP-018: Event Storming is Introduced as the Entry Point
**Category:** Content  
**Statement:** The paper must introduce Event Storming (or an equivalent domain discovery practice) as the recommended starting point for working with DIZZY — the moment where subject matter experts, not software engineers, lead the conversation.  
**Key point to convey:** Event Storming produces the vocabulary of the system — what commands are issued, what events occur, what policies react — without requiring anyone to write code. That vocabulary maps directly onto DIZZY's ontology. The gap between "we understand the domain" and "we have a working skeleton" shrinks dramatically.  
**Pass:** Event Storming is named, its role as a domain discovery practice briefly described, and its direct connection to DIZZY's component vocabulary made explicit.  
**Fail:** Event Storming is absent, or mentioned only in passing without connecting it to how DIZZY components emerge from the practice.

---

### WP-019: DIZZY's Ontology Serves as a Readable Map for Non-Engineers
**Category:** Philosophy  
**Statement:** The paper must close the loop between the "map mislabels the territory" problem (Section 1) and DIZZY's solution: an explicit, language-independent ontology that stakeholders, domain experts, and leadership can read and reason about — not just developers.  
**Key point to convey:** Traditional codebases teach us nothing about themselves. DIZZY's definitions — written in terms of commands, events, and policies rather than functions and classes — are legible to people who understand the business, regardless of whether they can read code.  
**Pass:** The paper explicitly connects the stakeholder-legibility problem to the ontology as its answer. A non-technical reader should understand that DIZZY gives them a map they can actually use.  
**Fail:** The paper diagnoses the map problem but never explains how DIZZY addresses it, or addresses it only in technical terms.

---

### WP-020: Policies are Explained as Reactive Logic
**Category:** Content  
**Statement:** The paper must explain policies as the reactive layer of DIZZY — the "when this event occurs, issue this command" mechanism — as a philosophical concept, not an implementation detail.  
**Key point to convey:** Policies are how the system responds to what has happened without human intervention. They encode business rules as reactions to facts. Because policies are triggered by events (immutable, already-happened facts), they are inherently decoupled from the commands they produce.  
**Pass:** Policies are named, their reactive role described in plain language, and their relationship to events and commands made clear conceptually.  
**Fail:** Policies are listed in the ontology but never explained, or explained only in terms of how they are implemented.

---

### WP-021: Execution Flows are Enumerable
**Category:** Philosophy  
**Statement:** The paper must convey that in a DIZZY system, the full path of execution is countable — every command, procedure, event, policy, and projection can be listed. This is a meaningful contrast to traditional codebases where execution paths are emergent and traced, not enumerated.  
**Key point to convey:** In most systems, understanding "what happens when a user does X" requires tracing through layers of implicit calls, middleware, and side effects. In DIZZY, the answer is always a finite, readable sequence. This makes reasoning, auditing, and change estimation tractable.  
**Pass:** The paper names enumerability as a benefit and contrasts it with the opacity of conventional architectures. A reader understands that DIZZY's flows are a map, not a maze.  
**Fail:** The enumerable nature of flows is implied but never stated, or absent entirely.

---

### WP-022: Architecture Shapes the Organization, Not Just the Code
**Category:** Philosophy  
**Statement:** The paper must address Conway's Law — that systems mirror the communication structures of the organizations that build them — and argue that DIZZY's component boundaries deliberately shape how teams divide and coordinate work.  
**Key point to convey:** DIZZY's rigid separation of commands, events, procedures, policies, projections, and queriers is not just a technical constraint — it is an organizational one. Teams can own components. Work can be divided by flow segment. The architecture creates natural seams that align with how people communicate, rather than fighting it.  
**Pass:** Conway's Law is named or paraphrased, and the paper argues that DIZZY's component boundaries are a conscious response to it — making team coordination a property of the architecture, not an afterthought.  
**Fail:** Conway's Law is mentioned without connecting it to DIZZY's design intent, or absent entirely.

---

### WP-023: Tone is Authoritative and Persuasive
**Category:** Writing  
**Statement:** The paper must take a position and argue it. It should read as a thoughtful practitioner making a case, not an academic describing a system or a marketer selling a product.  
**Guidelines:** Use direct, declarative sentences. Prefer active voice. Do not hedge unnecessarily. Acknowledge tradeoffs honestly rather than avoiding them — this builds credibility. The paper should feel like it was written by someone who has felt the pain it describes.  
**Pass:** A reader finishes the paper feeling that the author has a point of view and has earned it.  
**Fail:** The paper reads as neutral description, sales copy, or academic abstraction without a clear argument.

---

### WP-024: Terminology is Consistent Throughout
**Category:** Writing  
**Statement:** Every DIZZY concept must be referred to by exactly one name, used consistently from first introduction to conclusion.  
**Canonical terms:** Command, Event, Procedure, Policy, Projection, Model, Querier, Query Input, Query Output. No synonyms, aliases, or informal variants (e.g. "message" for Command, "handler" for Procedure, "request" for Query).  
**Pass:** Each term appears under one name throughout. The first use of each term reads as a deliberate introduction.  
**Fail:** Any DIZZY concept is referred to by more than one name, or terms are used before being introduced.

---

### WP-025: The Argument is Made in Prose
**Category:** Writing  
**Statement:** The paper's core argument must be carried by prose paragraphs, not bullet lists. Bullets are permitted only when genuinely enumerating discrete items (e.g. a list of prior disciplines DIZZY builds on). They must not substitute for an argument that should be written out.  
**Pass:** Every major claim is developed in full sentences. Bullet lists, when present, enumerate rather than argue.  
**Fail:** Any section uses bullets as a shortcut to avoid writing the argument in full, or the paper reads more like a slide deck than an essay.

---

### WP-026: The Paper Follows a Clear Narrative Arc
**Category:** Structure  
**Statement:** The paper must follow a coherent three-act structure: (1) the problem — why software architecture so often fails; (2) the philosophy — the principles DIZZY is built on and why they address the problem; (3) the system — what DIZZY is, what its components are, and how the generation pipeline connects domain thinking to implementation.  
**Pass:** Each act is clearly present, transitions between acts are explicit, and the conclusion closes the arc by connecting back to the opening problem.  
**Fail:** Acts are present but bleed into each other without clear transitions, the problem and solution are interleaved, or the conclusion does not reference the opening argument.

---

### WP-027: The Paper Defers to the Specification Cleanly
**Category:** Scope  
**Statement:** When a topic belongs in the Specification rather than the whitepaper, the paper must say so explicitly and move on — never half-explain, never silently omit.  
**Pass:** Any reference to implementation mechanics, schema syntax, or deployment specifics is accompanied by a clean deferral ("for the full specification of X, see the companion DIZZY Specification") without attempting to summarize it.  
**Fail:** The paper either silently omits topics that a reader would naturally expect (leaving gaps), or partially explains them in a way that creates confusion without the Specification in hand.

---

### WP-028: The Reader Takeaway is Singular and Clear
**Category:** Writing  
**Statement:** The paper must be written toward a single takeaway that a reader can state in one sentence after finishing. That sentence should be derivable from the conclusion.  
**Target takeaway (suggested):** DIZZY is a philosophy for building software systems where the domain logic, the data contracts, and the infrastructure are kept permanently separate — so that any one of them can change without breaking the others.  
**Pass:** The conclusion lands a clear, singular thesis. A reader who skims only the abstract and conclusion can state what DIZZY is and why it matters.  
**Fail:** The conclusion lists multiple disconnected points, the thesis is buried mid-paper, or a reader finishing the paper cannot summarize what DIZZY is in a sentence.
