# Known Issues

## Duplicated type maps across generator modules

`_LINKML_TYPE_MAP` and `_PYTHON_TYPE_MAP` are copy-pasted into every generator module
(`commands.py`, `events.py`, and future `queries.py`, `models.py`, etc.).

A change to a type mapping (e.g. adding `date` → `date`) must be applied in every file.
This is a maintenance hazard that will grow as more generators are added.