# DIZZY Testing Guide

Testing event-driven systems requires different strategies than traditional applications. DIZZY's architecture enables comprehensive testing at multiple levels.

## Testing Philosophy

**Key Principles**:
1. **Test behavior, not implementation** - Focus on what events are emitted, not how
2. **Isolation through mocks** - Use mock emitters and queries for unit tests
3. **Determinism** - Same events through same projection should always produce same model
4. **Idempotency** - Projections should handle duplicate events safely

## Unit Testing

Unit tests validate individual procedures and policies in isolation.

### Testing Procedures

Procedures take commands and emit events. Test by mocking the context:

```python
# src/procedure/cc_py/test_partition_scan.py
from unittest.mock import Mock, call
import pytest
from src.procedure.cc_py.partition_scan import partition_scan
from gen.pyd.commands.start_scan import StartScan
from gen.pyd.procedure.partition_scan_context import (
    start_scan_context,
    start_scan_emitters,
    start_scan_queries
)
from gen.pyd.events.scan_item_found import ScanItemFound
from gen.pyd.events.scan_complete import ScanComplete

def test_partition_scan_emits_found_events():
    """Procedure should emit ScanItemFound for each file."""
    # Arrange
    mock_found = Mock()
    mock_complete = Mock()

    context = start_scan_context(
        emit=start_scan_emitters(
            scan_item_found=mock_found,
            scan_complete=mock_complete
        ),
        query=start_scan_queries()
    )

    command = StartScan(
        command_id="test-123",
        scan_path="/tmp/test_dir",
        recursive=True
    )

    # Act
    partition_scan(context, command)

    # Assert
    assert mock_found.called
    assert mock_complete.call_count == 1

    # Verify event structure
    found_event = mock_found.call_args[0][0]
    assert isinstance(found_event, ScanItemFound)
    assert found_event.file_path.startswith("/tmp/test_dir")

def test_partition_scan_counts_items_correctly():
    """Procedure should report accurate count in completion event."""
    found_events = []
    complete_events = []

    context = start_scan_context(
        emit=start_scan_emitters(
            scan_item_found=lambda e: found_events.append(e),
            scan_complete=lambda e: complete_events.append(e)
        ),
        query=start_scan_queries()
    )

    command = StartScan(command_id="test", scan_path="/tmp/test_dir")
    partition_scan(context, command)

    assert len(complete_events) == 1
    assert complete_events[0].total_items == len(found_events)

def test_partition_scan_handles_empty_directory():
    """Procedure should handle empty directories gracefully."""
    mock_found = Mock()
    mock_complete = Mock()

    context = start_scan_context(
        emit=start_scan_emitters(
            scan_item_found=mock_found,
            scan_complete=mock_complete
        ),
        query=start_scan_queries()
    )

    command = StartScan(command_id="test", scan_path="/tmp/empty_dir")
    partition_scan(context, command)

    assert not mock_found.called
    assert mock_complete.called
    assert mock_complete.call_args[0][0].total_items == 0
```

### Testing Policies

Policies take events and emit commands. Test by mocking the policy context:

```python
# src/policy/cc_py/test_hash_priority_files.py
from unittest.mock import Mock
import pytest
from src.policy.cc_py.hash_priority_files import hash_priority_files
from gen.pyd.events.scan_item_found import ScanItemFound
from gen.pyd.policy.hash_priority_files_context import (
    hash_priority_context,
    hash_priority_emitters
)
from gen.pyd.commands.calculate_hash import CalculateHash

def test_policy_emits_hash_for_priority_files():
    """Policy should emit hash command for priority file types."""
    mock_emit_hash = Mock()

    context = hash_priority_context(
        emit=hash_priority_emitters(
            calculate_hash=mock_emit_hash
        )
    )

    event = ScanItemFound(
        event_id="evt-1",
        file_path="/data/important.pdf",
        size_bytes=1024
    )

    hash_priority_files(context, event)

    assert mock_emit_hash.called
    emitted_command = mock_emit_hash.call_args[0][0]
    assert isinstance(emitted_command, CalculateHash)
    assert emitted_command.file_path == "/data/important.pdf"

def test_policy_ignores_non_priority_files():
    """Policy should not emit hash command for non-priority files."""
    mock_emit_hash = Mock()

    context = hash_priority_context(
        emit=hash_priority_emitters(calculate_hash=mock_emit_hash)
    )

    event = ScanItemFound(
        event_id="evt-2",
        file_path="/data/random.txt",
        size_bytes=512
    )

    hash_priority_files(context, event)

    assert not mock_emit_hash.called

@pytest.mark.parametrize("file_path,should_hash", [
    ("/data/doc.pdf", True),
    ("/data/doc.docx", True),
    ("/data/sheet.xlsx", True),
    ("/data/archive.zip", True),
    ("/data/text.txt", False),
    ("/data/image.jpg", False),
    ("/data/no_extension", False),
])
def test_policy_file_type_detection(file_path, should_hash):
    """Policy should correctly identify priority file types."""
    mock_emit_hash = Mock()

    context = hash_priority_context(
        emit=hash_priority_emitters(calculate_hash=mock_emit_hash)
    )

    event = ScanItemFound(
        event_id="evt",
        file_path=file_path,
        size_bytes=1024
    )

    hash_priority_files(context, event)

    assert mock_emit_hash.called == should_hash
```

### Testing Projections

Projections transform events into model updates. Test by applying events and verifying model state:

```python
# src/projection/test_scan_results_projection.py
import pytest
from src.projection.scan_results_projection import apply_scan_item_found, apply_scan_complete
from gen.pyd.events.scan_item_found import ScanItemFound
from gen.pyd.events.scan_complete import ScanComplete
from models.scan_result import ScanResult

def test_projection_creates_new_scan_result():
    """Projection should create new scan result on first event."""
    event = ScanItemFound(
        event_id="evt-1",
        scan_id="scan-123",
        file_path="/data/file1.txt",
        size_bytes=1024
    )

    # Simulate projection logic
    result = apply_scan_item_found(event, existing_results={})

    assert result.scan_id == "scan-123"
    assert result.total_items == 1
    assert result.total_bytes == 1024

def test_projection_accumulates_items():
    """Projection should accumulate items from multiple events."""
    existing = ScanResult(scan_id="scan-123", total_items=5, total_bytes=5120)

    event = ScanItemFound(
        event_id="evt-6",
        scan_id="scan-123",
        file_path="/data/file6.txt",
        size_bytes=2048
    )

    result = apply_scan_item_found(event, existing_result=existing)

    assert result.total_items == 6
    assert result.total_bytes == 7168

def test_projection_idempotency():
    """Projection should handle duplicate events idempotently."""
    existing = ScanResult(scan_id="scan-123", total_items=1, total_bytes=1024)

    # Same event applied twice
    event = ScanItemFound(
        event_id="evt-1",  # Same event ID
        scan_id="scan-123",
        file_path="/data/file1.txt",
        size_bytes=1024
    )

    result1 = apply_scan_item_found(event, existing_result=existing)
    result2 = apply_scan_item_found(event, existing_result=result1)

    # Should not double-count
    assert result1 == result2
```

## Integration Testing

Integration tests validate workflows across multiple components.

### Testing Event Flows

Test complete workflows from command through events to subsequent commands:

```python
# tests/integration/test_scan_and_hash_workflow.py
import pytest
from collections import defaultdict
from src.procedure.cc_py.partition_scan import partition_scan
from src.policy.cc_py.hash_priority_files import hash_priority_files
from gen.pyd.commands.start_scan import StartScan

def test_scan_to_hash_workflow():
    """Integration test: scan triggers hash commands for priority files."""
    # Event store
    events_emitted = []
    commands_emitted = []

    # Wire procedure
    procedure_context = start_scan_context(
        emit=start_scan_emitters(
            scan_item_found=lambda e: events_emitted.append(e),
            scan_complete=lambda e: events_emitted.append(e)
        ),
        query=start_scan_queries()
    )

    # Execute procedure
    command = StartScan(
        command_id="cmd-1",
        scan_path="/tmp/test_files",
        recursive=True
    )
    partition_scan(procedure_context, command)

    # Wire policy
    policy_context = hash_priority_context(
        emit=hash_priority_emitters(
            calculate_hash=lambda c: commands_emitted.append(c)
        )
    )

    # Execute policy on emitted events
    for event in events_emitted:
        if isinstance(event, ScanItemFound):
            hash_priority_files(policy_context, event)

    # Assertions
    assert len(events_emitted) > 0, "Should have emitted scan events"

    scan_complete_events = [e for e in events_emitted if isinstance(e, ScanComplete)]
    assert len(scan_complete_events) == 1, "Should complete once"

    # Verify workflow: some files should trigger hash commands
    priority_files = [e for e in events_emitted
                     if isinstance(e, ScanItemFound)
                     and e.file_path.endswith(('.pdf', '.docx'))]

    assert len(commands_emitted) == len(priority_files), \
        "Should emit hash command for each priority file"
```

### Testing Query Integration

Test procedures using queries from projections:

```python
def test_procedure_with_query_integration():
    """Test procedure that queries model before emitting events."""
    # Set up mock query that returns data
    mock_query = Mock(return_value=ScanResult(total_items=100))

    procedure_context = some_procedure_context(
        emit=some_emitters(...),
        query=some_queries(get_scan_results=mock_query)
    )

    command = SomeCommand(...)
    some_procedure(procedure_context, command)

    # Verify query was called
    assert mock_query.called

    # Verify procedure used query result in logic
    # (check emitted events reflect query data)
```

## Property-Based Testing

Use Hypothesis to generate test cases and verify properties:

```python
# tests/property/test_scan_properties.py
from hypothesis import given, strategies as st
from src.procedure.cc_py.partition_scan import partition_scan

@given(
    scan_path=st.text(min_size=1, max_size=100),
    recursive=st.booleans()
)
def test_scan_always_completes(scan_path, recursive):
    """Property: Every scan should emit exactly one complete event."""
    events = []

    context = start_scan_context(
        emit=start_scan_emitters(
            scan_item_found=lambda e: events.append(e),
            scan_complete=lambda e: events.append(e)
        ),
        query=start_scan_queries()
    )

    command = StartScan(
        command_id="test",
        scan_path=scan_path,
        recursive=recursive
    )

    # Should not raise
    partition_scan(context, command)

    # Should always emit exactly one complete
    complete_events = [e for e in events if isinstance(e, ScanComplete)]
    assert len(complete_events) == 1

@given(
    file_path=st.text(),
    size_bytes=st.integers(min_value=0)
)
def test_policy_is_deterministic(file_path, size_bytes):
    """Property: Policy should produce same output for same input."""
    event = ScanItemFound(
        event_id="evt",
        file_path=file_path,
        size_bytes=size_bytes
    )

    # Run policy twice
    commands1 = []
    commands2 = []

    for commands_list in [commands1, commands2]:
        context = hash_priority_context(
            emit=hash_priority_emitters(
                calculate_hash=lambda c: commands_list.append(c)
            )
        )
        hash_priority_files(context, event)

    # Should emit same commands both times
    assert len(commands1) == len(commands2)
    if commands1:
        assert commands1[0].file_path == commands2[0].file_path
```

## Chaos Testing

Test system behavior under adverse conditions.

### Event Replay Testing

Verify projections can rebuild state from events:

```python
def test_projection_rebuild_from_events():
    """Chaos test: Rebuild entire model from event log."""
    # Generate random events
    events = generate_random_scan_events(count=1000)

    # Build model incrementally
    result1 = ScanResult.empty()
    for event in events:
        result1 = apply_event(event, result1)

    # Rebuild from scratch
    result2 = ScanResult.empty()
    for event in events:
        result2 = apply_event(event, result2)

    # Should be identical
    assert result1 == result2

def test_projection_handles_out_of_order_events():
    """Chaos test: Projections should handle out-of-order events."""
    events = generate_events_with_timestamps()

    # Apply in order
    result1 = rebuild_model(sorted(events, key=lambda e: e.timestamp))

    # Apply out of order
    result2 = rebuild_model(random.shuffle(events))

    # Should produce same result if idempotent
    assert result1 == result2
```

### Fault Injection

Test error handling and recovery:

```python
def test_procedure_handles_filesystem_errors():
    """Chaos test: Procedure should handle I/O errors gracefully."""
    error_events = []

    context = start_scan_context(
        emit=start_scan_emitters(
            scan_item_found=Mock(),
            scan_complete=Mock(),
            scan_item_failed=lambda e: error_events.append(e)  # Error handler
        ),
        query=start_scan_queries()
    )

    command = StartScan(
        command_id="test",
        scan_path="/nonexistent/path"
    )

    # Should not raise
    partition_scan(context, command)

    # Should emit error event
    assert len(error_events) > 0

def test_policy_handles_invalid_events():
    """Chaos test: Policy should handle malformed events."""
    mock_emit = Mock()

    context = hash_priority_context(
        emit=hash_priority_emitters(calculate_hash=mock_emit)
    )

    # Malformed event (missing required fields)
    event = ScanItemFound(event_id="evt")  # Missing file_path

    # Should not raise
    try:
        hash_priority_files(context, event)
    except Exception as e:
        pytest.fail(f"Policy should handle malformed events: {e}")
```

## Performance Testing

Test system performance characteristics:

```python
import time
import pytest

def test_scan_performance_large_directory():
    """Performance test: Scan should handle large directories efficiently."""
    events = []

    context = start_scan_context(
        emit=start_scan_emitters(
            scan_item_found=lambda e: events.append(e),
            scan_complete=lambda e: events.append(e)
        ),
        query=start_scan_queries()
    )

    command = StartScan(
        command_id="perf-test",
        scan_path="/large/directory/with/10000/files"
    )

    start = time.time()
    partition_scan(context, command)
    duration = time.time() - start

    assert duration < 60.0, f"Scan took {duration}s, should be < 60s"
    assert len(events) > 10000, "Should have found all files"

@pytest.mark.benchmark
def test_projection_throughput(benchmark):
    """Benchmark: Projection should process events at high throughput."""
    events = generate_random_scan_events(count=1000)

    def rebuild():
        result = ScanResult.empty()
        for event in events:
            result = apply_event(event, result)
        return result

    result = benchmark(rebuild)
    assert result.total_items == 1000
```

## Contract Testing

Verify components adhere to their protocols:

```python
def test_procedure_implements_protocol():
    """Contract test: Implementation should match protocol signature."""
    from inspect import signature
    from src.procedure.cc_py.partition_scan import partition_scan
    from gen.pyd.procedure.partition_scan_protocol import start_scan_procedure_protocol

    # Get signatures
    impl_sig = signature(partition_scan)
    protocol_sig = signature(start_scan_procedure_protocol.__call__)

    # Should match (ignoring self parameter)
    assert list(impl_sig.parameters.keys()) == list(protocol_sig.parameters.keys())[1:]

def test_procedure_emits_declared_events():
    """Contract test: Procedure should only emit events declared in feat.yaml."""
    from gen.pyd.events.scan_item_found import ScanItemFound
    from gen.pyd.events.scan_complete import ScanComplete

    ALLOWED_EVENTS = {ScanItemFound, ScanComplete}

    events = []
    context = start_scan_context(
        emit=start_scan_emitters(
            scan_item_found=lambda e: events.append(e),
            scan_complete=lambda e: events.append(e)
        ),
        query=start_scan_queries()
    )

    partition_scan(context, StartScan(...))

    # All emitted events should be declared types
    for event in events:
        assert type(event) in ALLOWED_EVENTS, \
            f"Unexpected event type: {type(event)}"
```

## Testing Best Practices

### 1. Test Isolation

Each test should be independent:
- Don't share state between tests
- Use fresh mocks for each test
- Clean up resources (files, connections) after tests

### 2. Descriptive Names

Test names should describe expected behavior:
- ✓ `test_procedure_emits_complete_event_after_scan`
- ✗ `test_procedure_1`

### 3. Arrange-Act-Assert

Structure tests clearly:
```python
def test_something():
    # Arrange - set up test data
    context = ...
    command = ...

    # Act - execute behavior
    procedure(context, command)

    # Assert - verify results
    assert ...
```

### 4. Test Coverage

Aim for coverage of:
- **Happy paths**: Normal operation
- **Edge cases**: Empty inputs, boundary values
- **Error paths**: Invalid inputs, system failures
- **Integration**: Component interactions

### 5. Fast Feedback

- Unit tests should run in milliseconds
- Use `pytest -x` to stop on first failure
- Use `pytest -k test_name` to run specific tests
- Mock external dependencies (databases, APIs, filesystem)

## Continuous Integration

### pytest Configuration

```ini
# pytest.ini
[pytest]
testpaths = src tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --verbose
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=html
    --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    chaos: Chaos/fuzz tests
    benchmark: Performance benchmarks
```

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest -m unit

# Integration tests
pytest -m integration

# With coverage
pytest --cov=src --cov-report=html

# Fast fail
pytest -x

# Verbose output
pytest -vv

# Specific test
pytest src/procedure/cc_py/test_partition_scan.py::test_partition_scan_emits_found_events
```

## Summary

DIZZY's architecture makes testing straightforward:

1. **Unit tests**: Mock emitters/queries to test procedures and policies in isolation
2. **Integration tests**: Wire components together to test event flows
3. **Property tests**: Use Hypothesis to verify invariants hold for all inputs
4. **Chaos tests**: Verify system handles failures, out-of-order events, replays
5. **Contract tests**: Ensure implementations match protocols

**Key insight**: Event-driven architecture enables deterministic testing. Same events in, same state out.
