# `lcpc_a_py`

```
dizzy is a methodology for writing software

Built out of composable pieces:
2 types of data: commands and events. 
2 types of functions: procedures and policies.

Procedures do all of the work.
Anytime they do any effect based code, they write events.
Anytime they do anything that we wanna record as a fact, they write events.
And anytime there is a, like, business level error, they record events.

You're goal is to read the command LinkML, procedure protocol and context and generate an implementation of the procedure.

Keep it simple - no bullshit

This is a first pass - so forgo all Event Emits - instead, just debug log effects

@app/dedupe/scan_and_upload/def/commands/start_scan.yaml
@app/dedupe/scan_and_upload/gen/procedure/py/partition_scan_protocol.py
@app/dedupe/scan_and_upload/gen/procedure/py/partition_scan_context.py
->
app/dedupe/scan_and_upload/src/procedure/lcpc_py/start_scan.py 
```