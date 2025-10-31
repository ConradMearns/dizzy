# Policies

- Consume Events
- CAN emit Commands
- CAN query state (read-only)
- CAN mutate state (via mutations)
- Have signature: `(context: PolicyContext, event: Event) -> None`
- Stateless (all state via context or event)
- Contain business logic for reacting to events
