"""
Event store query implementations.

Retrieves events from filesystem-based event storage.
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from gen.queries import (
    GetAllEventsInput,
    GetAllEvents,
    GetEventsByTypesInput,
    GetEventsByTypes,
    ChainEntry,
    DomainEvent,
    TestMessage,
    FileItemScanned,
)


# Mapping of event type names to classes
EVENT_TYPE_MAP = {
    "TestMessage": TestMessage,
    "FileItemScanned": FileItemScanned,
}


class GetAllEventsQuery:
    """Query to get all events from the chain."""

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize the query.

        Args:
            base_path: Root directory for event storage. Defaults to ./data
        """
        self.base_path = base_path or Path("data")
        self.events_dir = self.base_path / "events"
        self.chain_file = self.base_path / "chain.csv"

    def execute(self, query_input: GetAllEventsInput) -> GetAllEvents:
        """Get all events from the chain in order."""
        entries = self._read_chain()
        return GetAllEvents(events=entries)

    def _read_chain(self) -> list[ChainEntry]:
        """Read the entire chain and load events."""
        entries = []

        if not self.chain_file.exists():
            return entries

        with open(self.chain_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                event_hash = row['event_hash']
                event_type = row['event_type']
                timestamp = datetime.fromisoformat(row['timestamp'])

                # Load event from file
                event = self._load_event(event_hash, event_type)

                if event:
                    entries.append(ChainEntry(
                        event_hash=event_hash,
                        event_type=event_type,
                        timestamp=timestamp,
                        event=event
                    ))

        return entries

    def _load_event(self, event_hash: str, event_type: str) -> Optional[DomainEvent]:
        """Load an event from its JSON file."""
        event_file = self.events_dir / event_hash[:2] / f"{event_hash}.json"

        if not event_file.exists():
            return None

        with open(event_file, 'r') as f:
            event_dict = json.load(f)

        # Get the appropriate class for this event type
        event_class = EVENT_TYPE_MAP.get(event_type)
        if not event_class:
            return None

        # Reconstruct the event using Pydantic
        return event_class(**event_dict)


class GetEventsByTypesQuery:
    """Query to get events filtered by type."""

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize the query.

        Args:
            base_path: Root directory for event storage. Defaults to ./data
        """
        self.base_path = base_path or Path("data")
        self.events_dir = self.base_path / "events"
        self.chain_file = self.base_path / "chain.csv"

    def execute(self, query_input: GetEventsByTypesInput) -> GetEventsByTypes:
        """Get events filtered by type."""
        # Reuse the chain reading logic
        all_events_query = GetAllEventsQuery(base_path=self.base_path)
        all_entries = all_events_query._read_chain()

        # Filter by requested types
        requested_types = set(query_input.event_types)
        filtered_entries = [
            entry for entry in all_entries
            if entry.event_type in requested_types
        ]

        return GetEventsByTypes(events=filtered_entries)
