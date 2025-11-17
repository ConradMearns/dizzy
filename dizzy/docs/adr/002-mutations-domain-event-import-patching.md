# ADR 002: Mutations DomainEvent Import Patching

## Status

Accepted

## Context

The DIZZY framework uses LinkML schemas to generate Pydantic models for events, mutations, queries, and other domain objects. The generation process uses `gen-pydantic` which generates standalone Python files from LinkML YAML schemas.

When defining mutations that reference domain events (for event sourcing), we encountered a type incompatibility issue:

1. `def/events.yaml` defines concrete event classes that inherit from `DomainEvent`
2. `def/mutations.yaml` imports `events` and references `DomainEvent` in its mutation definitions
3. However, `gen-pydantic` generates **each file independently**, duplicating the `DomainEvent` base class in both `gen/events.py` and `gen/mutations.py`
4. This creates two distinct `DomainEvent` classes at runtime: `gen.events.DomainEvent` and `gen.mutations.DomainEvent`
5. Pydantic's strict type checking fails when a mutation expects `gen.mutations.DomainEvent` but receives an event instance of `gen.events.HardDriveDetected` (which inherits from `gen.events.DomainEvent`)

### Example Error

```python
# gen/events.py (generated)
class DomainEvent(ConfiguredBaseModel):
    ...

class HardDriveDetected(DomainEvent):
    ...

# gen/mutations.py (generated)
class DomainEvent(ConfiguredBaseModel):  # ← Different class!
    ...

class EventRecordInput(MutationInput):
    event: DomainEvent  # ← Expects gen.mutations.DomainEvent
```

When storing an event:
```python
event = HardDriveDetected(...)  # Instance of gen.events.DomainEvent
EventRecordInput(event=event)   # ❌ ValidationError: wrong DomainEvent type
```

## Decision

We will implement a **post-generation patching step** that modifies `gen/mutations.py` to import `DomainEvent` from `gen.events` instead of defining its own copy.

The solution consists of:

1. **New utility script**: `pkg/dizzy/src/dizzy/utils/patch_mutations_imports.py`
   - Automatically patches the generated mutations file after `gen-pydantic` runs
   - Adds: `from gen.events import DomainEvent`
   - Removes: The duplicate `DomainEvent` class definition

2. **Justfile integration**: Add the patch step to the `gen` recipe:
   ```just
   gen:
       uv run gen-pydantic def/mutations.yaml > gen/mutations.py
       uv run python -m dizzy.utils.patch_mutations_imports gen/mutations.py
       ...
   ```

3. **Idempotent operation**: The script detects if already patched and skips re-patching

## Consequences

### Positive

- **Type safety restored**: Events and mutations now share the same `DomainEvent` base class
- **No manual intervention**: Developers just run `just gen` and get correctly patched files
- **Explicit and auditable**: The patch script is version-controlled and well-documented
- **Minimal coupling**: Only requires a regex-based find-and-replace after generation
- **Preserves generated code benefits**: Still get strong Pydantic validation and IDE support

### Negative

- **Generation complexity**: Adds an extra step to the code generation pipeline
- **Fragility**: If `gen-pydantic` output format changes significantly, the patch might break
- **Not a pure LinkML solution**: Would be better if LinkML/gen-pydantic supported cross-file imports natively

### Neutral

- **Alternative considered - manual imports**: Editing `gen/mutations.py` by hand was rejected because generated files should never be manually edited (changes would be lost on next generation)
- **Alternative considered - wrapper classes**: Creating non-Pydantic wrapper classes was rejected because it loses validation benefits
- **Alternative considered - monomorphic events**: Using dicts instead of typed events was rejected because it loses type safety

## Implementation Notes

The patch script uses regex to:
1. Find the insertion point after pydantic imports
2. Add the import statement: `from gen.events import DomainEvent`
3. Remove the duplicate class definition using pattern matching

This ensures that all references to `DomainEvent` in `gen/mutations.py` resolve to the same class defined in `gen/events.py`, maintaining type compatibility across the event sourcing boundary.

## Future Considerations

- Monitor LinkML and gen-pydantic for native support of cross-module imports
- If multiple apps need this pattern, consider making it a standard DIZZY generation step
- Could be extended to patch other cross-schema dependencies if needed
