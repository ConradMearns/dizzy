# Commands

- Represent an intention or request to perform an action
- MUST be serializable (JSON, YAML, etc.)
- MUST be immutable
- Named in imperative form (e.g., `ScanPartition`, `InspectStorage`)
- MUST NOT contain business logic or behavior
- Self-contained with all required data for execution
