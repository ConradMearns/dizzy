"""
Generic filesystem-based event storage mutation.

Implements content-addressable storage with ordered chain:
- Events stored in: events/{hash[:2]}/{hash}.json
- Chain stored in: chain.csv (timestamp, hash, event_type)
- Sequence is implicit from CSV row order
"""

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol


class DomainEvent(Protocol):
    """Protocol for domain events that can be stored."""

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Serialize event to dictionary."""
        ...

    @property
    def __class__(self) -> type:
        """Get the event class."""
        ...


class EventRecordInput(Protocol):
    """Protocol for event record input."""
    event: DomainEvent


class EventRecord(Protocol):
    """Protocol for event record result."""
    event_hash: str
    event_type: str
    event: DomainEvent
    is_duplicate: bool


class EventRecordMutation:
    """Store events using content-addressable filesystem storage."""

    def __init__(self, base_path: Path | None = None):
        """
        Initialize the event store.

        Args:
            base_path: Root directory for event storage. Defaults to ./data
        """
        self.base_path = base_path or Path("data")
        self.events_dir = self.base_path / "events"
        self.chain_file = self.base_path / "chain.csv"

        # Ensure directories exist
        self.events_dir.mkdir(parents=True, exist_ok=True)

        # Initialize chain.csv if it doesn't exist
        if not self.chain_file.exists():
            with open(self.chain_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'event_hash', 'event_type'])

        # Create .gitignore in data folder
        gitignore_file = self.base_path / ".gitignore"
        if not gitignore_file.exists():
            with open(gitignore_file, 'w') as f:
                f.write('*\n')

    def execute(self, mutation_input: EventRecordInput, event_record_class: type) -> EventRecord:
        """
        Store an event and return the record.

        Args:
            mutation_input: The input containing the event to store
            event_record_class: The EventRecord class to instantiate

        Returns:
            EventRecord instance with hash, type, and original event
        """
        event = mutation_input.event
        event_type = event.__class__.__name__

        # Serialize event to JSON for hashing
        event_dict = event.model_dump(exclude_none=True)
        event_json = json.dumps(event_dict, sort_keys=True)

        # Compute hash
        event_hash = hashlib.sha256(event_json.encode()).hexdigest()

        # Store event in content-addressable location
        shard_dir = self.events_dir / event_hash[:2]
        shard_dir.mkdir(exist_ok=True)

        event_file = shard_dir / f"{event_hash}.json"

        # Check if this is a duplicate (event file already exists)
        is_duplicate = event_file.exists()

        # Write event file and chain entry (idempotent - only if not exists)
        if not is_duplicate:
            with open(event_file, 'w') as f:
                json.dump(event_dict, f, indent=2)

            # Append to chain (only for new events, not duplicates)
            timestamp = datetime.now(timezone.utc).isoformat()

            with open(self.chain_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, event_hash, event_type])

        # Return the event record with duplicate flag
        return event_record_class(
            event_hash=event_hash,
            event_type=event_type,
            event=event,
            is_duplicate=is_duplicate
        )
