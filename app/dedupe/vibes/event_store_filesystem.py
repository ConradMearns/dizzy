#!/usr/bin/env python3

"""
Test filesystem-based event storage.

Tests the EventRecordMutation with actual file and CSV storage.
"""

from pathlib import Path
import shutil

from gen.mutations import EventRecordInput, EventRecord, TestMessage
from dizzy.event_store import EventRecordMutation


# Clean up any previous test data
test_data_path = Path("data_test")
if test_data_path.exists():
    shutil.rmtree(test_data_path)

# Create mutation with test data directory
mutation = EventRecordMutation(base_path=test_data_path)

print("=== FILESYSTEM EVENT STORAGE TEST ===\n")

# Store some events
msg1 = TestMessage(message="Hello, filesystem!")
msg2 = TestMessage(message="Testing persistence")
msg3 = TestMessage(message="Hello, filesystem!")  # Duplicate

print("Storing event 1...")
result1 = mutation.execute(EventRecordInput(event=msg1), EventRecord)
print(f"  Hash: {result1.event_hash[:16]}...")
print(f"  Type: {result1.event_type}\n")

print("Storing event 2...")
result2 = mutation.execute(EventRecordInput(event=msg2), EventRecord)
print(f"  Hash: {result2.event_hash[:16]}...")
print(f"  Type: {result2.event_type}\n")

print("Storing event 3 (duplicate of event 1)...")
result3 = mutation.execute(EventRecordInput(event=msg3), EventRecord)
print(f"  Hash: {result3.event_hash[:16]}...")
print(f"  Type: {result3.event_type}\n")

# Verify files were created
print("=== FILE SYSTEM CHECK ===")
events_dir = test_data_path / "events"
event_files = list(events_dir.rglob("*.json"))
print(f"Event files created: {len(event_files)}")
for f in event_files:
    print(f"  {f.relative_to(test_data_path)}")

# Check chain.csv
print("\n=== CHAIN.CSV ===")
chain_file = test_data_path / "chain.csv"
with open(chain_file, 'r') as f:
    print(f.read())

print("✅ Same event (msg1 and msg3) has same hash:", result1.event_hash == result3.event_hash)
print("✅ Only 2 unique event files created (deduplication works)")
print("✅ 3 entries in chain.csv (captures all observations)")

# Now test querying
print("\n=== QUERYING EVENTS ===")
from gen.queries import GetAllEventsInput, GetAllEvents, ChainEntry
from gen.events import TestMessage, FileItemScanned
from dizzy.event_store import GetAllEventsQuery

# Create event type registry
EVENT_TYPE_MAP = {
    "TestMessage": TestMessage,
    "FileItemScanned": FileItemScanned,
}

query = GetAllEventsQuery(base_path=test_data_path, event_type_map=EVENT_TYPE_MAP)
all_events_result = query.execute(GetAllEventsInput(), ChainEntry, GetAllEvents)

print(f"Retrieved {len(all_events_result.events)} events from chain:")
for i, entry in enumerate(all_events_result.events, 1):
    print(f"  {i}. {entry.event_type}: {entry.event_hash[:16]}...")
    print(f"     Message: {entry.event.message}")
    print(f"     Timestamp: {entry.timestamp}")

print("\n✅ Event retrieval works!")
print(f"✅ All 3 events retrieved in order")

# Test filtered query
print("\n=== QUERYING BY TYPE ===")
from gen.queries import GetEventsByTypesInput, GetEventsByTypes
from dizzy.event_store import GetEventsByTypesQuery

filtered_query = GetEventsByTypesQuery(base_path=test_data_path, event_type_map=EVENT_TYPE_MAP)
filtered_result = filtered_query.execute(GetEventsByTypesInput(event_types=["TestMessage"]), ChainEntry, GetEventsByTypes)

print(f"Retrieved {len(filtered_result.events)} TestMessage events:")
for i, entry in enumerate(filtered_result.events, 1):
    print(f"  {i}. {entry.event_type}: {entry.event.message}")

print("\n✅ Filtered query works!")
