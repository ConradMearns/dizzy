#!/usr/bin/env python3

"""
Test event storage using TestMessage events.

Simple in-memory mutator using dictionary + list for content-addressable storage.
"""

import hashlib
import json
from gen.events import TestMessage, DomainEvent
from gen.mutations import EventRecordInput, EventRecord


# Simple in-memory event store
event_store = {}  # hash -> event data
event_chain = []  # list of (hash, event_type) tuples


def store_event(event: DomainEvent) -> EventRecord:
    """Store an event using content-addressable storage."""
    # Serialize event to JSON for hashing using Pydantic
    # Use model_dump then json.dumps to ensure sorted keys for consistent hashing
    event_dict = event.model_dump(exclude_none=True)
    event_json = json.dumps(event_dict, sort_keys=True)

    # Compute hash
    event_hash = hashlib.sha256(event_json.encode()).hexdigest()

    # Store event (idempotent - only stores if not exists)
    if event_hash not in event_store:
        event_store[event_hash] = event_dict

    # Append to chain (always append, even if duplicate)
    event_type = event.__class__.__name__
    event_chain.append((event_hash, event_type))

    return EventRecord(event_hash=event_hash)


# Test it out
print("=== EVENT SOURCING TEST ===\n")

# Create and store some events
msg1 = TestMessage(message="Hello, world!")
msg2 = TestMessage(message="Testing events")
msg3 = TestMessage(message="Hello, world!")  # Duplicate

print("Storing event 1...")
result1 = store_event(msg1)
print(f"  Hash: {result1.event_hash}\n")

print("Storing event 2...")
result2 = store_event(msg2)
print(f"  Hash: {result2.event_hash}\n")

print("Storing event 3 (duplicate of event 1)...")
result3 = store_event(msg3)
print(f"  Hash: {result3.event_hash}\n")

# Show results
print("=== EVENT STORE ===")
print(f"Unique events stored: {len(event_store)}")
for hash, data in event_store.items():
    print(f"  {hash[:16]}... -> {data}")

print("\n=== EVENT CHAIN ===")
print(f"Total events in chain: {len(event_chain)}")
for i, (hash, event_type) in enumerate(event_chain, 1):
    print(f"  {i}. {event_type}: {hash[:16]}...")

print("\n✅ Content-addressable storage works!")
print(f"✅ Same event (msg1 and msg3) has same hash: {result1.event_hash == result3.event_hash}")
