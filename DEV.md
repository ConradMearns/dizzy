# 6. generate procedure without events 

## `lcpc_a_py`

dizzy is a methodology for writing software

Built out of composable pieces:
2 types of data: commands and events. 
2 types of functions: procedures and policies.

Procedures do all of the work.
Anytime they do any effect based code, they write events.
Anytime they do anything that we wanna record as a fact, they write events.
And anytime there is a, like, business level error, they record events.

You're goal is to read the command LinkML, procedure protocol and context and generate an implementation of the procedure.

The dizzy runtime will wrap all procedure calls in error handling.
Your implementation should focus solely on the success case and the explicit events supported by the context.
If anything fails, let the exception propagate and the runtime will handle it.

This is a first pass - so forgo all Event Emits - instead, just log around effects at the debug level

Procedure:
```yaml
commands:
  start_scan: Initiates a scan to discover files

events:
  scan_item_found: Found a file (not folder) while scanning
  scan_complete: Finished scanning
  scan_item_failed: Something went reading a single item

procedures:
  partition_scan:
    description: Scans partition for items, does the work of discovery. Hashes each item to ensure referential integrity
    command: start_scan
    emits:
      - scan_item_found
      - scan_complete
      - scan_item_failed
```
Using
@app/dedupe/scan_and_upload/def/commands/start_scan.yaml
@app/dedupe/scan_and_upload/gen/procedure/py/partition_scan_protocol.py
@app/dedupe/scan_and_upload/gen/procedure/py/partition_scan_context.py

Create
app/dedupe/scan_and_upload/src/procedure/lcpc_a_py/partition_scan.py

# 6a. generate procedure without events 

## `lcpc_b_py`

dizzy is a methodology for writing software

Built out of composable pieces:
2 types of data: commands and events. 
2 types of functions: procedures and policies.

Procedures do all of the work.
Anytime they do any effect based code, they write events.
Anytime they do anything that we wanna record as a fact, they write events.
And anytime there is a, like, business level error, they record events.

You're goal is to read the command LinkML, procedure protocol and context and generate an implementation of the procedure.

The dizzy runtime will wrap all procedure calls in error handling.
Your implementation should focus solely on the success case and the explicit events supported by the context.
If anything fails, let the exception propagate and the runtime will handle it.

This is a first pass - so forgo all Event Emits - instead, just log around effects at the debug level

Procedure:
```yaml
commands:
  start_scan: Initiates a scan to discover files

events:
  scan_item_found: Found a file (not folder) while scanning
  scan_complete: Finished scanning
  scan_item_failed: Something went reading a single item

procedures:
  partition_scan:
    description: Scans partition for items, does the work of discovery. Hashes each item to ensure referential integrity
    command: start_scan
    emits:
      - scan_item_found
      - scan_complete
      - scan_item_failed
```
Using
@app/dedupe/scan_and_upload/def/commands/start_scan.yaml
@app/dedupe/scan_and_upload/gen/procedure/py/partition_scan_protocol.py
@app/dedupe/scan_and_upload/gen/procedure/py/partition_scan_context.py

Create
app/dedupe/scan_and_upload/src/procedure/lcpc_b_py/partition_scan.py

use xx hash for this



# 7 testing

```bash

uv run python run_procedure.py \
  --feature app/dedupe/scan_and_upload.feat.yaml \
  --procedure-name partition_scan \
  --procedure app/dedupe/scan_and_upload/src/procedure/lcpc_a_py/partition_scan.py \
  --command '{"path": "/home/conrad/Pictures/xperia-iii"}'
```

# 7a testing

```bash

uv run python run_procedure.py \
  --feature app/dedupe/scan_and_upload.feat.yaml \
  --procedure-name partition_scan \
  --procedure app/dedupe/scan_and_upload/src/procedure/lcpc_b_py/partition_scan.py \
  --command '{"path": "/home/conrad/Pictures/xperia-iii"}'
```

> as a note, sha256 took
> real    0m17.608s
> user    0m14.956s
> sys     0m2.405s
> as a note, xxhash took
> real    0m5.311s
> user    0m2.487s
> sys     0m2.131s

# 8. generate events from text (assuming no procedure code)

## principals

@PRINCIPALS_EVENTS.md

## event discovery prompt

dizzy is a methodology for writing software

Built out of composable pieces:
2 types of data: commands and events. 
2 types of functions: procedures and policies.

your goal is to create an Event definition based on our Command definition and Procedure description
explain your reasoning afterwards

@PRINCIPALS_EVENTS.md
@PRINCIPALS_COMMANDS.md
@app/dedupe/scan_and_upload/def/commands/start_scan.yaml
Procedure:
  PROCEDURE partition_scan(context, command):
  1. Get the scan path from the command
  2. Log that scan is starting
  3. FOR EACH item in the directory tree (recursively):
      IF item is a file (not a directory):
          TRY:
              - Hash the file using SHA256
              - Log the found file with its hash
          CATCH any errors:
              - Log the failure with error details
  4. Log that scan is complete

## response:

Looking at the command, procedure, and principles, I need to create Event definitions for the lifecycle of a partition scan. Let me create a comprehensive event schema:

  id: https://example.org/dedupe/events/scan_events
  name: dedupe-scan-events
  title: Partition Scan Events
  description: Events emitted during partition scanning operations
  prefixes:
    linkml: https://w3id.org/linkml/
    dedupe: https://example.org/dedupe/
  default_prefix: dedupe
  default_range: string
  imports:
  - linkml:types
  - ../../../../../dizzy/src/dizzy/def/events
  classes:

    scan_started:
      description: Emitted when partition scan begins
      is_a: Event
      attributes:
        session_id:
          description: Deterministic session identifier derived from command_id
          required: true
          range: string
        command_id:
          description: ID of the start_scan command that initiated this scan
          required: true
          range: string
        path:
          description: The filesystem path being scanned
          required: true
          range: string
        started_at:
          description: Timestamp when scan actually began
          required: true
          range: datetime

    file_discovered:
      description: Emitted when a file is found and successfully hashed
      is_a: Event
      attributes:
        session_id:
          description: Session identifier linking to scan_started
          required: true
          range: string
        command_id:
          description: ID of the originating start_scan command
          required: true
          range: string
        file_path:
          description: Full path to the discovered file
          required: true
          range: string
        content_hash:
          description: SHA256 hash of file content (content-based identity)
          required: true
          range: string
        file_size:
          description: File size in bytes
          required: true
          range: integer
        modified_at:
          description: File system modification timestamp (metadata enrichment)
          required: true
          range: datetime
        discovered_at:
          description: Timestamp when file was discovered during this scan
          required: true
          range: datetime

    file_scan_failed:
      description: Emitted when file hashing or processing fails
      is_a: Event
      attributes:
        session_id:
          description: Session identifier linking to scan_started
          required: true
          range: string
        command_id:
          description: ID of the originating start_scan command
          required: true
          range: string
        file_path:
          description: Path to the file that failed to process
          required: true
          range: string
        error_type:
          description: Classification of error (permission_denied, io_error, etc)
          required: true
          range: string
        error_message:
          description: Detailed error message
          required: true
          range: string
        failed_at:
          description: Timestamp when failure occurred
          required: true
          range: datetime

    scan_completed:
      description: Emitted when partition scan finishes
      is_a: Event
      attributes:
        session_id:
          description: Session identifier linking to scan_started
          required: true
          range: string
        command_id:
          description: ID of the originating start_scan command
          required: true
          range: string
        files_discovered:
          description: Count of successfully hashed files
          required: true
          range: integer
        files_failed:
          description: Count of files that failed to process
          required: true
          range: integer
        completed_at:
          description: Timestamp when scan completed
          required: true
          range: datetime

  Reasoning:

  Content-Based Identity (Principle 1): The file_discovered event includes content_hash as the SHA256 of file content. This is the immutable identity—even if files move or are renamed, the hash remains constant.

  Session Scoping (Principle 2): All events share a session_id that groups this particular execution of the scan. Multiple scans of the same path would produce different sessions.

  Deterministic Attributes (Principle 3):
  - session_id is deterministically derived from command_id (not a random UUID)
  - Timestamps like started_at, discovered_at, failed_at, completed_at reflect when things actually happened, not when events were created
  - No creation timestamps or submission times in the events

  Metadata Enrichment (Principle 4): The file_discovered event includes modified_at (filesystem timestamp), file_size, and file_path alongside the content hash. This allows policies to distinguish between "same content uploaded twice intentionally" vs "same file scanned twice accidentally."

  Honest Event Reporting (Principle 5): Every file discovered produces a file_discovered event, even if it's a duplicate hash. Policies downstream can decide whether to import, skip, or error on duplicates.

  Durable Execution (Principle 6):
  - session_id is derived from command_id, so if the procedure fails and restarts with the same command, it produces the same session_id
  - This enables deduplication: if we've already emitted file_discovered events for certain hashes in this session, we can skip or recognize partial work
  - Idempotent replay is possible because events are deterministic

  Command Linkage: Every event includes command_id to trace back to the originating start_scan command, enabling span tracking and observability.