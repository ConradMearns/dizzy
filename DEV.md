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

your goal is to create an example Events based on our Command definition and Procedure description
explain your reasoning afterwards

@PRINCIPALS_EVENTS.md
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

```markdown
Based on the start_scan command, the procedure description, and the event principles, here are the example events that should be generated:

  # Event 1: Scan Session Started
  ---
  type: scan_started
  session_id: "550e8400-e29b-41d4-a716-446655440000"  # Groups all events from this scan
  path: "/media/photos/vacation2024"
  started_at: "2024-11-20T14:32:15Z"  # When scan actually started
  source_device: "workstation-01"

  # Event 2: File Discovered (successful)
  ---
  type: file_discovered
  session_id: "550e8400-e29b-41d4-a716-446655440000"
  file_path: "/media/photos/vacation2024/IMG_0001.jpg"
  content_hash: "sha256:a3b2c1d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
  discovered_at: "2024-11-20T14:32:16Z"
  metadata:
    size_bytes: 2547891
    modified_time: "2024-07-15T10:23:45Z"  # Original file timestamp
    created_time: "2024-07-15T10:23:45Z"
    exif_date: "2024-07-15T10:23:45Z"

  # Event 3: File Discovered (another file)
  ---
  type: file_discovered
  session_id: "550e8400-e29b-41d4-a716-446655440000"
  file_path: "/media/photos/vacation2024/IMG_0002.jpg"
  content_hash: "sha256:b4c3d2e1f5a6789012345678901234567890bcdef1234567890bcdef234567"
  discovered_at: "2024-11-20T14:32:17Z"
  metadata:
    size_bytes: 3124567
    modified_time: "2024-07-15T11:45:12Z"
    created_time: "2024-07-15T11:45:12Z"
    exif_date: "2024-07-15T11:45:12Z"

  # Event 4: File Scan Failed
  ---
  type: file_scan_failed
  session_id: "550e8400-e29b-41d4-a716-446655440000"
  file_path: "/media/photos/vacation2024/corrupt.jpg"
  failed_at: "2024-11-20T14:32:18Z"
  error_type: "PermissionError"
  error_message: "Permission denied: unable to read file"
  metadata:
    size_bytes: 0  # What we could determine without reading

  # Event 5: Duplicate Content (same hash, different path)
  ---
  type: file_discovered
  session_id: "550e8400-e29b-41d4-a716-446655440000"
  file_path: "/media/photos/vacation2024/copies/IMG_0001_copy.jpg"
  content_hash: "sha256:a3b2c1d4e5f6789012345678901234567890abcdef1234567890abcdef123456"  # Same as IMG_0001.jpg
  discovered_at: "2024-11-20T14:32:19Z"
  metadata:
    size_bytes: 2547891
    modified_time: "2024-08-01T09:12:33Z"  # Different timestamp than original
    created_time: "2024-08-01T09:12:33Z"

  # Event 6: Scan Completed
  ---
  type: scan_completed
  session_id: "550e8400-e29b-41d4-a716-446655440000"
  path: "/media/photos/vacation2024"
  completed_at: "2024-11-20T14:35:42Z"
  summary:
    files_discovered: 247
    files_failed: 1
    unique_content_hashes: 246  # One duplicate detected
    total_bytes: 1547892345

  Reasoning

  Content-Based Identity: Each file_discovered event includes a SHA256 content_hash as the primary identifier. Notice that IMG_0001.jpg and IMG_0001_copy.jpg share the same hash—the content defines their identity, not their paths.

  Session Scoping: All events share the same session_id to group them as one logical scan operation. If we ran the same scan again tomorrow, it would get a different session_id even if the content was identical.

  Deterministic Attributes Only:
  - Timestamps (discovered_at, started_at, etc.) reflect when things actually happened, not when events were created
  - The session_id is a UUID for this specific execution instance
  - Content hashes are deterministic—same content always produces the same hash

  Metadata Enrichment: Events include file timestamps, sizes, and EXIF data alongside hashes. This allows policies to distinguish between "same content uploaded at different times" vs "same content that was always there."

  Let Policies Handle Duplication: The procedure honestly reports both files with their hashes, even though they're duplicates. A policy can then decide whether to:
  - Skip the duplicate import
  - Flag it for user review
  - Import both with different metadata
  - Trigger an error

  The events are immutable facts about what was found—policies make the decisions about what to do with those facts.
```