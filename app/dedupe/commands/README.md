# DIZZY Commands

This directory contains pre-made command files for the DIZZY service.

## Command Format

Commands are JSON objects with a `type` field that specifies the command class, followed by any required fields for that command.

### InspectStorage

Inspects storage devices and emits events for detected drives and partitions.

```json
{
  "type": "InspectStorage"
}
```

### AssignPartitionMount

Assigns a partition to a desired mount point.

```json
{
  "type": "AssignPartitionMount",
  "partition": {
    "uuid": "PARTITION_UUID",
    "drive_uuid": "DRIVE_UUID"
  },
  "mount_point": "/path/to/mount"
}
```

## File Formats

### Single Command (.json)

A single JSON object:

```json
{
  "type": "InspectStorage"
}
```

### Batch Commands (.jsonl)

Multiple commands, one per line (newline-delimited JSON):

```jsonl
{"type": "InspectStorage"}
{"type": "AssignPartitionMount", "partition": {"uuid": "ABC123", "drive_uuid": "XYZ"}, "mount_point": "/mnt/data"}
```

## Usage Examples

### Run a single command file

```bash
python serve_cli.py commands/inspect_storage.json
```

### Run multiple command files in sequence

```bash
python serve_cli.py commands/inspect_storage.json commands/assign_mount_example.json
```

### Run a batch file

```bash
python serve_cli.py commands/batch_example.jsonl
```

### Pipe from stdin

```bash
cat commands/inspect_storage.json | python serve_cli.py --stdin
```

### Verbose output

```bash
python serve_cli.py -v commands/batch_example.jsonl
```

## Example Files

- `inspect_storage.json` - Single InspectStorage command
- `assign_mount_example.json` - Single AssignPartitionMount command
- `batch_example.jsonl` - Complete workflow: inspect storage then assign 4 partitions

## Creating Your Own Commands

1. Create a JSON file with the command structure
2. Ensure the `type` field matches a registered command class
3. Pydantic will validate all fields automatically
4. If validation fails, you'll get a clear error message with stack trace
