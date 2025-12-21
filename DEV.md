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

Display result as YAML

## response:

```markdown
Looking at the start_scan command and the principles, I'll create example events that would result from executing this command during a scan operation.

  # Event 1: Scan session started
  - event_type: scan_started
    session_id: 550e8400-e29b-41d4-a716-446655440000
    command_id: start_scan
    scan_path: /media/photos/2023
    started_at: "2023-06-15T14:30:00Z"
    device_id: laptop-01

  # Event 2: File discovered during scan
  - event_type: file_discovered
    session_id: 550e8400-e29b-41d4-a716-446655440000
    content_hash: sha256:a3b5c7d9e1f2a4b6c8d0e2f4a6b8c0d2e4f6a8b0c2d4e6f8a0b2c4d6e8f0a2b4
    file_path: /media/photos/2023/IMG_001.jpg
    file_size_bytes: 2458624
    file_mtime: "2023-06-10T08:15:23Z"
    file_ctime: "2023-06-10T08:15:23Z"
    discovered_at: "2023-06-15T14:30:01Z"
    metadata:
      mime_type: image/jpeg
      exif_date_taken: "2023-06-10T08:15:23Z"
      exif_camera: Canon EOS R5

  # Event 3: Another file discovered (duplicate content)
  - event_type: file_discovered
    session_id: 550e8400-e29b-41d4-a716-446655440000
    content_hash: sha256:a3b5c7d9e1f2a4b6c8d0e2f4a6b8c0d2e4f6a8b0c2d4e6f8a0b2c4d6e8f0a2b4
    file_path: /media/photos/2023/backup/IMG_001_copy.jpg
    file_size_bytes: 2458624
    file_mtime: "2023-06-12T19:45:00Z"
    file_ctime: "2023-06-12T19:45:00Z"
    discovered_at: "2023-06-15T14:30:02Z"
    metadata:
      mime_type: image/jpeg
      exif_date_taken: "2023-06-10T08:15:23Z"
      exif_camera: Canon EOS R5

  # Event 4: Scan completed
  - event_type: scan_completed
    session_id: 550e8400-e29b-41d4-a716-446655440000
    scan_path: /media/photos/2023
    completed_at: "2023-06-15T14:32:15Z"
    files_discovered: 142
    total_bytes: 1847293824
    unique_content_hashes: 138

  Reasoning

  Content-Based Identity: Each file_discovered event includes a content_hash (SHA256) as the primary identifier. Notice events 2 and 3 have the same hash despite different paths—the content defines identity.

  Session Scoping: All events share session_id: 550e8400-e29b-41d4-a716-446655440000. If the same start_scan command runs again on the same path, it gets a new session_id, making operations distinguishable.

  Deterministic Attributes:
  - file_mtime and file_ctime reflect when the file was modified/created, not when we scanned it
  - exif_date_taken is from the file itself
  - Non-deterministic attributes like discovered_at are clearly labeled as observation timestamps

  Metadata Enrichment: Beyond just the hash, we capture file timestamps, EXIF data, MIME type, and device context. This lets policies distinguish between "same photo taken once" vs "same photo copied multiple times."

  Let Policies Handle Duplication: Events 2 and 3 honestly report both files were discovered, even though they're duplicates (same hash). A policy can then decide: import both? Skip the second? Flag for user review? The events don't presume the answer.
```