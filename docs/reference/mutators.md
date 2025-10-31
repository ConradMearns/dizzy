# Mutators

- Perform write operations
- CAN mutate state (event store, databases, filesystems, etc.)
- MUST NOT emit events or commands directly
- Have signature: `(input: MutationInput) -> MutationResult`
- Idempotent when possible
- CAN have side effects
- Return confirmation or status of the mutation
