# Play: Adding a Query to an Existing Procedure

## Problem Statement

An existing procedure needs to be enhanced with a new query capability to enrich the data it emits in domain events. The procedure already exists and works, but requires access to an additional external system or data source during its execution.

## Context

- **Architecture**: CQRS/Event Sourcing system with procedures that handle commands and emit events
- **Code Generation**: System uses schema definitions (YAML) to generate typed interfaces and contexts
- **Dependency Injection**: Procedures receive their dependencies through context objects (queries, emitters, mutators)

## The Play

### Step 1: Update Procedure Definition Schema

Add the new query to the procedure's dependency list in the schema definition file (e.g., `procedures.d.yaml`):

```yaml
procedures:
  my_procedure:
    command: MyCommand
    emitters:
      emit_something: SomethingHappened
    queries:
      existing_query: ExistingQuery
      new_query: NewQuery  # ← Add this
```

### Step 2: Update Event Schema (if needed)

If the new query provides data that should be included in emitted events, add fields to the event schema (e.g., `events.yaml`):

```yaml
classes:
  SomethingHappened:
    is_a: DomainEvent
    attributes:
      existing_field:
        description: Existing field
        required: true
        range: string
      new_field:  # ← Add this
        description: New field from query result
        required: true
        range: string
```

### Step 3: Regenerate Code

Run the code generation command to update all interfaces and contexts:

```bash
just gen  # or whatever your build command is
```

This will:
- Update the procedure context to include the new query
- Update event classes with new fields
- Regenerate all type definitions

### Step 4: Update Procedure Implementation

Modify the procedure implementation to use the new query:

```python
def __call__(self, context: MyProcedureContext, command: MyCommand) -> None:
    # Existing logic...

    # Call the new query
    result = context.query.new_query(
        NewQueryInput(param=value)
    )

    # Use the result in your event
    context.emit.something(SomethingHappened(
        existing_field=existing_value,
        new_field=result.new_data  # ← Use query result
    ))
```

### Step 5: Wire Up Service

Add the query implementation to the service initialization:

```python
# Initialize query implementation
new_query_impl = NewQueryImpl()

# Add to procedure context
self.procedure_map = {
    MyProcedure: MyProcedureContext(
        emit=MyProcedureEmitters(...),
        query=MyProcedureQueries(
            existing_query=existing_query.execute,
            new_query=new_query_impl.execute,  # ← Wire it up
        )
    ),
}
```

### Step 6: Update CLI/Entry Points (if needed)

If using a command registry, add any new commands:

```python
COMMAND_REGISTRY = {
    "ExistingCommand": ExistingCommand,
    "MyCommand": MyCommand,  # ← Ensure it's registered
}
```

## Specific Example: Adding CAS Storage to File Scanner

### Problem
We had a `ScanPartition` procedure that scanned files and emitted `FileItemScanned` events with just metadata (path, size, hash). We wanted to store the actual file content in a Content Addressable Storage (CAS) system and include the CAS ID in the event.

### Solution Applied

1. **Updated `procedures.d.yaml`**:
   ```yaml
   partition_scanner:
     command: ScanPartition
     queries:
       list_file_items: ListFileItems
       put_content: PutContent  # ← Added CAS query
   ```

2. **Updated `events.yaml`**:
   ```yaml
   FileItemScanned:
     attributes:
       content_hash: string
       cas_id: string  # ← Added CAS ID field
   ```

3. **Regenerated code**: `just gen`

4. **Updated `procedures/scan_partition.py`**:
   ```python
   # Read file content
   file_content = bytearray()
   with open(file_path, 'rb') as f:
       for chunk in iter(lambda: f.read(8192), b''):
           file_content.extend(chunk)

   # Store in CAS
   put_result = context.query.put_content(
       PutContentInput(content=bytes(file_content))
   )

   # Emit with CAS ID
   context.emit.scanned(FileItemScanned(
       path=str(file_path),
       cas_id=put_result.cas_id  # ← Use CAS ID
   ))
   ```

5. **Updated `st_service.py`**:
   ```python
   # Initialize CAS query
   put_content_query = PutContentQuery()

   # Wire to procedure
   ScanPartitionProcedure: ScanPartitionContext(
       query=ScanPartitionQueries(
           list_file_items=list_file_items_query.execute,
           put_content=put_content_query.execute,  # ← Added
       )
   )
   ```

6. **Updated `serve_cli.py`**:
   ```python
   COMMAND_REGISTRY = {
       "ScanPartition": ScanPartition,  # ← Registered
   }
   ```

### Special Considerations: Binary Data Handling

When working with binary data (like file contents), ensure the query implementation preserves bytes:

```python
# In the query implementation
def execute(self, query_input: PutContentInput) -> PutContent:
    content = query_input.content

    if isinstance(content, bytes):
        content_bytes = content  # Use as-is
    elif isinstance(content, str):
        content_bytes = content.encode('utf-8')  # Only for text

    # Store raw bytes - no encoding/decoding
    content_stream = BytesIO(content_bytes)
    self.client.put_object(bucket, path, content_stream, len(content_bytes))
```

## Key Principles

1. **Schema-Driven**: Changes start in schema definitions, not code
2. **Regenerate**: Always regenerate code after schema changes
3. **Type Safety**: Generated contexts enforce correct dependencies at compile time
4. **Dependency Injection**: Queries are injected via context, not imported directly
5. **Binary Preservation**: When handling file content, work with raw bytes to preserve binary files exactly

## Anti-Patterns to Avoid

- ❌ Importing query implementations directly in procedures
- ❌ Bypassing schema definitions and hand-editing generated code
- ❌ Forgetting to wire up queries in the service initialization
- ❌ Converting binary data to strings (causes corruption)

## Verification

After implementation:
1. Run the procedure with verbose output
2. Verify the new query is called
3. Check that events contain the new fields
4. For storage systems, verify data is persisted correctly
5. For binary data, verify byte-for-byte preservation

## Related Plays

- Adding a mutation to a policy
- Creating a new procedure from scratch
- Adding event sourcing to a new domain

---

## What Went Poorly / Lessons Learned

### 1. Type System Mismatch Not Caught Early

**Issue**: The LinkML schema defined `content: range: string` with a comment "Will be bytes in Python", but Pydantic generated `content: str`. This creates a type mismatch where we're passing `bytes` to a field typed as `str`.

**Impact**: Requires runtime type checking and defensive programming in the query implementation. Pydantic may attempt UTF-8 decoding which could corrupt binary files or crash on non-UTF-8 data.

**Better Next Time**:
- Proactively ask about data types when dealing with file content or binary data
- Check generated types immediately after regeneration
- Consider whether the schema system supports the actual data types needed
- Document type system limitations in the schema file itself
- Consider using base64 encoding at the schema boundary if binary types aren't supported

### 2. Binary Data Corruption Risk Not Identified Immediately

**Issue**: Didn't immediately recognize that string encoding could corrupt binary files. User had to point out the "octet-stream" MIME type question before we addressed byte preservation.

**Impact**: Could have shipped code that corrupted binary files (images, executables, etc.) through UTF-8 encoding attempts.

**Better Next Time**:
- When seeing file I/O, immediately ask: "Is this text or binary?"
- Add verification step: download and compare checksums
- Test with actual binary files (images, PDFs) not just text
- Document binary handling requirements upfront in the play

### 3. No End-to-End Verification Test

**Issue**: We ran the scan successfully but didn't verify that:
- Files can be retrieved from CAS
- Retrieved bytes match original bytes exactly
- Binary files aren't corrupted

**Impact**: We're trusting the implementation without proof of correctness.

**Better Next Time**:
- Always include a round-trip test for storage systems
- Write a verification script that: stores file → retrieves file → compares hashes
- Add to verification checklist: "Prove bytes are preserved with SHA256 comparison"
- Run existing test suite (like `test_cas.py`) after integration

### 4. Debug Code Left in Production Path

**Issue**: The scan procedure has `print("Wrapping up")` and `exit()` calls that appear to be debug code, limiting the scan to one file.

**What Should Have Happened**:
- Remove debug statements and exit calls
- Scan should process all files in partition
- Add proper logging instead of print statements

**Better Next Time**:
- Review existing code for debug artifacts before modification
- Ask: "Should this scan multiple files or just one?"
- Clean up debug code as part of the enhancement

### 5. Schema Limitations Created Technical Debt

**Issue**: LinkML doesn't support bytes type, forcing us to use `string` in schema but `bytes` at runtime. This creates a permanent type mismatch.

**Impact**: Every future developer must understand this quirk and handle it correctly. Documentation burden increases. Type safety is weakened.

**Better Next Time**:
- Document schema limitations prominently in schema files
- Consider whether schema system is the right choice for binary data
- Evaluate alternatives: separate binary storage abstraction, base64 encoding, or different schema system
- Add runtime validation that logs warnings on type mismatches

### 6. Missing Integration Test in Play Execution

**Issue**: Didn't write or run a test showing the complete flow works correctly with binary preservation.

**What Would Have Been Better**:
```python
# Should have created: tests/test_scan_with_cas.py
def test_scan_preserves_binary_files():
    # Create test binary file
    test_content = bytes([0xFF, 0xD8, 0xFF, 0xE0])  # JPEG header

    # Run scan procedure
    scan(partition_uuid)

    # Retrieve from CAS using emitted cas_id
    retrieved = cas.get_content(cas_id)

    # Verify exact byte match
    assert retrieved == test_content
```

**Better Next Time**:
- Write integration test as final step of play
- Test with non-UTF-8 binary data specifically
- Include in verification checklist: "Integration test passes"

### 7. Missed Opportunity for Proactive Questions

**Issue**: Could have asked earlier:
- "What type of files are we scanning?" (text vs binary)
- "Should we scan all files or stop after one?"
- "How do we verify the stored content is correct?"

**Better Next Time**:
- Front-load questions about data characteristics
- Ask about expected behavior (single vs multiple items)
- Propose verification approach before starting implementation

---

## Future Improvements to This Play

1. Add "Data Type Analysis" as Step 0: Identify if working with text, binary, or structured data
2. Expand verification section to include round-trip testing
3. Add schema limitation documentation requirements
4. Include cleanup checklist (remove debug code, add proper logging)
5. Require integration test as part of completion criteria
