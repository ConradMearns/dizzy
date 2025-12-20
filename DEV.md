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

# 8. generate events for event-less procedure

after building / manipulating the start of the procedure, we can make event definitions
then we can go back and finish the procedure

## event definitions

dizzy is a methodology for writing software

Built out of composable pieces:
2 types of data: commands and events. 
2 types of functions: procedures and policies.

You're goal is to read a fresh procedure and write the LinkML definitions for the relevant Events.
Base the Event information on what is in the debug logs - don't add other unneeded information

Events:
```yaml
events:
  scan_item_found: Found a file (not folder) while scanning
  scan_complete: Finished scanning
  scan_item_failed: Something went reading a single item
```

@app/dedupe/scan_and_upload/src/procedure/lcpc_a_py/start_scan.py
->
@app/dedupe/scan_and_upload/gen/events/pyd/scan_complete.py
@app/dedupe/scan_and_upload/gen/events/pyd/scan_item_found.py
@app/dedupe/scan_and_upload/gen/events/pyd/scan_item_failed.py