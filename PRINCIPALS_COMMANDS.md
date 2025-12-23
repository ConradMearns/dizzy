Keep Command ID
This can be a timestamp, or a UUID, or something non-deterministic.
This allows for span tracking

  Commands MUST include a command_id attribute. Session IDs are either:
  - The command_id itself, or
  - Deterministically derived from command_id + stable command attributes (never timestamps)

  New Principal: Command Determinism

  Command Determinism
  Commands represent intent and must be deterministic. Never include creation
  timestamps, submission times, or other non-deterministic metadata in command
  attributes.

  Good: command_id, path, filter_criteria, target_date
  Bad: created_at, submitted_at, submitted_by_hostname

  Events record when things happened. Commands record what should happen. If you 
  need to know when a command 