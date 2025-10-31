# Contexts

- Provide dependency injection for Procedures and Policies
- Contain Emitters for output (events or commands)
- Contain Queriers for reading state
- MAY contain Mutators (for Policies only)
- Named with pattern: `{ProcedureName}Context` or `{PolicyName}Context`
- Specific to each Procedure or Policy type
