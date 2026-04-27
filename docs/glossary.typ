#let dizzy-terms = (
  command: (
    short: "Command",
    description: [An expression of intent — what a user or policy wants to happen. Commands are ephemeral; they may be rejected, retried, or discarded without consequence.],
    group: "DIZZY Components",
  ),
  event: (
    short: "Event",
    description: [An immutable record of a fact. Events are the single source of truth in a DIZZY system; once written, they cannot be altered or deleted.],
    group: "DIZZY Components",
  ),
  procedure: (
    short: "Procedure",
    description: [Handles a Command and may emit Events. Procedures are the site of critical work — where intent meets consequence.],
    group: "DIZZY Components",
  ),
  policy: (
    short: "Policy",
    description: [Reacts to an Event and may emit Commands. Policies encode business rules as reactions to facts, decoupled from the Procedures that produced those facts.],
    group: "DIZZY Components",
  ),
  projection: (
    short: "Projection",
    description: [Listens for specific Events and updates one or more Models. Translates the language of facts into queryable state.],
    group: "DIZZY Components",
  ),
  model: (
    short: "Model",
    description: [A queryable view of state, derived from Events via Projections. Models are ephemeral and rebuildable on demand — a cache, not the source of truth.],
    group: "DIZZY Components",
  ),
  querier: (
    short: "Querier",
    description: [Executes a Query against a Model using program code. Keeps database driver logic separate from data definitions and domain logic.],
    group: "DIZZY Components",
  ),
  query: (
    short: "Query",
    description: [A typed data definition for a call and its response — the interface between a Querier and a Model.],
    group: "DIZZY Components",
  ),
  feature-file: (
    short: "Feature File",
    description: [A structured declaration of every component the system requires: which Commands exist, which Procedures handle them, which Events are produced, which Policies react, and which Projections and @querier:pl serve the system. The output of a workshopping session and the input to the generation pipeline.],
    group: "Architecture",
  ),
  interstitial-infrastructure: (
    short: "Interstitial Infrastructure",
    description: [The wiring between DIZZY components — message queues, database connections, deployment topology. Kept deliberately separate from domain logic so any infrastructure choice can change without touching business rules.],
    group: "Architecture",
  ),
  data: (
    short: "Data",
    description: [Collective term for the data-definition components of a DIZZY system: Commands, Events, Models, and Queries.],
    group: "Collectives",
  ),
  functions: (
    short: "Functions",
    description: [Collective term for the executable components of a DIZZY system: Procedures, Policies, Projections, and @querier:pl.],
    group: "Collectives",
  ),
)
