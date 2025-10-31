# Emitters

- Provide methods for emitting Events (from Procedures) or Commands (from Policies)
- Named with pattern: `{ProcedureName}Emitters` or `{PolicyName}Emitters`
- Each emitter method corresponds to a specific Event or Command type
- Methods have signature: `(payload: Event | Command) -> None`
- Injected into Contexts for use by Procedures and Policies
