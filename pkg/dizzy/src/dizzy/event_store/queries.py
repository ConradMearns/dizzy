"""
Generic event store query implementations.

Retrieves events from filesystem-based event storage.
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol


class DomainEvent(Protocol):
    """Protocol for domain events that can be loaded."""
    ...


class ChainEntry(Protocol):
    """Protocol for chain entry result."""
    event_hash: str
    event_type: str
    timestamp: datetime
    event: DomainEvent


class GetAllEventsInput(Protocol):
    """Protocol for get all events input."""
    ...


class GetAllEvents(Protocol):
    """Protocol for get all events result."""
    events: list[ChainEntry]


class GetEventsByTypesInput(Protocol):
    """Protocol for get events by types input."""
    event_types: list[str]


class GetEventsByTypes(Protocol):
    """Protocol for get events by types result."""
    events: list[ChainEntry]


class GetAllEventsQuery:
    """Query to get all events from the chain."""

    def __init__(
        self,
        base_path: Path | None = None,
        event_type_map: dict[str, type] | None = None
    ):
        """
        Initialize the query.

        Args:
            base_path: Root directory for event storage. Defaults to ./data
            event_type_map: Mapping of event type names to classes for deserialization
        """
        self.base_path = base_path or Path("data")
        self.events_dir = self.base_path / "events"
        self.chain_file = self.base_path / "chain.csv"
        self.event_type_map = event_type_map or {}

    def execute(
        self,
        query_input: GetAllEventsInput,
        chain_entry_class: type,
        get_all_events_class: type
    ) -> GetAllEvents:
        """
        Get all events from the chain in order.

        Args:
            query_input: The query input
            chain_entry_class: Class to instantiate for each chain entry
            get_all_events_class: Class to instantiate for the result

        Returns:
            GetAllEvents instance with list of chain entries
        """
        entries = self._read_chain(chain_entry_class)
        return get_all_events_class(events=entries)

    def _read_chain(self, chain_entry_class: type) -> list[ChainEntry]:
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
                    # Use model_construct to bypass validation for subclass instances
                    entry = chain_entry_class.model_construct(
                        event_hash=event_hash,
                        event_type=event_type,
                        timestamp=timestamp,
                        event=event
                    )
                    entries.append(entry)

        return entries

    def _load_event(self, event_hash: str, event_type: str) -> DomainEvent | None:
        """Load an event from its JSON file."""
        event_file = self.events_dir / event_hash[:2] / f"{event_hash}.json"

        if not event_file.exists():
            return None

        with open(event_file, 'r') as f:
            event_dict = json.load(f)

        # Get the appropriate class for this event type
        event_class = self.event_type_map.get(event_type)
        if not event_class:
            return None

        # Reconstruct the event using Pydantic
        return event_class(**event_dict)


class GetEventsByTypesQuery:
    """Query to get events filtered by type."""

    def __init__(
        self,
        base_path: Path | None = None,
        event_type_map: dict[str, type] | None = None
    ):
        """
        Initialize the query.

        Args:
            base_path: Root directory for event storage. Defaults to ./data
            event_type_map: Mapping of event type names to classes for deserialization
        """
        self.base_path = base_path or Path("data")
        self.events_dir = self.base_path / "events"
        self.chain_file = self.base_path / "chain.csv"
        self.event_type_map = event_type_map or {}

    def execute(
        self,
        query_input: GetEventsByTypesInput,
        chain_entry_class: type,
        get_events_by_types_class: type
    ) -> GetEventsByTypes:
        """
        Get events filtered by type.

        Args:
            query_input: The query input with event_types list
            chain_entry_class: Class to instantiate for each chain entry
            get_events_by_types_class: Class to instantiate for the result

        Returns:
            GetEventsByTypes instance with filtered list of chain entries
        """
        # Reuse the chain reading logic
        all_events_query = GetAllEventsQuery(
            base_path=self.base_path,
            event_type_map=self.event_type_map
        )
        all_entries = all_events_query._read_chain(chain_entry_class)

        # Filter by requested types
        requested_types = set(query_input.event_types)
        filtered_entries = [
            entry for entry in all_entries
            if entry.event_type in requested_types
        ]

        return get_events_by_types_class(events=filtered_entries)
