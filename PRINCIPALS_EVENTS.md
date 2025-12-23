Content-Based Identity
Events representing external artifacts must include content hashes. Filenames, paths, and timestamps change—content defines identity.

Session Scoping
Group related events with session identifiers. Same operation executed multiple times produces different sessions, even if the underlying content is identical.

Deterministic Attributes Only
Event immutability requires that all attributes are deterministic. Timestamps must reflect when things happened, not when events were created. GUIDs/UUIDs belong to sessions and commands, not as primary content identity.

Metadata Enrichment
Include contextual metadata (source device, file timestamps, EXIF data) alongside content hashes. This supports policies that need to distinguish between "same content" and "same intent."

Let Policies Handle Duplication
Events should be honest about what was scanned/found. Let policies decide whether duplicate content triggers import, skip, or error commands.

Durable Execution
Procedures may fail and restart. Session identifiers must be deterministic and derived from the command that initiated the work. 
Same command replayed = same session_id. This enables:
- Deduplication of events from retries
- Recognition of partial work
- Idempotent replay of failed operations
