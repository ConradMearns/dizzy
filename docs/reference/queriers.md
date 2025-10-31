# Queriers

- Perform read-only operations
- MUST NOT mutate state
- MUST NOT emit events or commands
- Have signature: `(input: QueryInput) -> QueryResult`
- Deterministic when possible
- CAN access external systems (databases, filesystems, APIs)
- Return serializable data structures
