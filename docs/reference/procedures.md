# Procedures

- Consume Commands
- CAN emit Events
- CAN query state (read-only)
- MUST NOT mutate state
- Have signature: `(context: ProcedureContext, command: Command) -> None`
- Stateless (all state via context or command)
- Contain business logic for processing commands
