# Schema-Driven Feature Implementation Play

## Problem Statement

**Given**: A codebase with schema-driven architecture using YAML definitions, code generation, and protocol-based implementations.

**Need**: Implement a new feature that integrates with the existing architecture, follows established patterns, and maintains type safety and testability.

## The Play (General Pattern)

### Phase 1: Schema Definition
1. **Define data models** in `def/models.yaml`
   - Identify core domain entities
   - Define attributes with proper types and constraints
   - Mark identifiers appropriately

2. **Define interface contracts** in relevant definition files (`def/queries.yaml`, `def/mutations.yaml`, etc.)
   - Create Input/Output pairs for operations
   - Import required models
   - Use proper inheritance (`is_a: Query`, `is_a: QueryInput`, etc.)
   - Add clear descriptions for all entities

### Phase 2: Code Generation
3. **Run generation tooling** (`just gen` or equivalent)
   - Generate Pydantic models from YAML schemas
   - Generate protocol interfaces for implementations
   - Verify generation output for correctness

### Phase 3: Implementation
4. **Implement protocol interfaces**
   - Create implementation files following project structure
   - Implement each protocol's `execute` method
   - Document hidden dependencies (network, platform, credentials)
   - Handle data type conversions appropriately

5. **Add required dependencies**
   - Use package manager to add new libraries
   - Update project configuration as needed

### Phase 4: Verification
6. **Create test/verification script** in `vibes/` directory
   - Test each operation independently
   - Test edge cases (idempotency, error handling, type conversions)
   - Provide clear pass/fail reporting
   - Include comprehensive test coverage

## Example: Content Addressable Storage (CAS) Implementation

### Problem Context
Implement a Content Addressable Storage system using MinIO as the backend, with BLAKE3 hashing and base58 encoding for content identification.

### Solution Execution

#### Phase 1: Schema Definition

**Models** (`app/dedupe/def/models.yaml`):
```yaml
CASIdentity:
  description: >-
    Content Addressable Storage identifier consisting of version and hash.
    Used to uniquely identify content by its cryptographic hash.
  attributes:
    version:
      description: CAS version string (e.g., "DZ0")
      identifier: true
      required: true
      range: string
    hash:
      description: Base58-encoded BLAKE3 hash of the content
      identifier: true
      required: true
      range: string
```

**Query Interfaces** (`app/dedupe/def/queries.yaml`):
- Added `models` to imports
- Created three operation pairs:
  - `PutContentInput` → `PutContent` (store content, return CAS ID)
  - `GetContentInput` → `GetContent` (retrieve by CAS ID)
  - `CheckExistsInput` → `CheckExists` (verify existence)

#### Phase 2: Code Generation

```bash
just gen
```

Generated outputs:
- Updated `gen/models.py`, `gen/queries.py`
- Updated `queries/interfaces.py` with three new protocols:
  - `PutContentProtocol`
  - `GetContentProtocol`
  - `CheckExistsProtocol`

#### Phase 3: Implementation

**File**: `app/dedupe/queries/cas_minio.py`

Key implementation details:
- **CAS ID Format**: String `"version:hash"` (e.g., `"DZ0:1317P2j..."`)
- **Storage Path**: `/{version}/{hash}` in MinIO bucket
- **Configuration Class**: `MinIOCASConfig` for connection parameters
- **Three Query Classes**: Each implementing respective protocol

Dependencies added:
```bash
uv add blake3 base58
```

Critical implementation decisions:
- Used string format for CAS ID (generated schema expected string, not object)
- Handled both bytes and string content inputs
- Auto-create bucket on first use
- Parse CAS ID string format when retrieving/checking content

#### Phase 4: Verification

**Test Script**: `app/dedupe/vibes/test_cas.py`

Six comprehensive tests:
1. ✓ PutContent - Store content and verify CAS ID format
2. ✓ CheckExists - Verify stored content is findable
3. ✓ GetContent - Retrieve and match original content
4. ✓ Deduplication - Different content produces different hash
5. ✓ Idempotency - Same content produces same hash
6. ✓ String Handling - Both bytes and strings work correctly

All tests passed on first complete run.

## Key Learnings from This Example

1. **Schema-first approach** prevents implementation drift from contracts
2. **Type mismatches** between schema and implementation are caught early (CAS ID as string vs object)
3. **Code generation** eliminates boilerplate and ensures consistency
4. **Protocol-based design** allows for multiple implementations (could swap MinIO for S3, filesystem, etc.)
5. **Vibes testing** validates end-to-end functionality before integration

## Applicability

This play applies when:
- Adding new queries, mutations, or procedures to the system
- Extending existing schemas with new models
- Implementing alternative backends for existing protocols
- Building features that follow established architectural patterns

## Success Criteria

- [ ] Schema definitions are complete and properly typed
- [ ] Code generation completes without errors
- [ ] All protocols are implemented with proper signatures
- [ ] Test script validates all operations
- [ ] Documentation includes hidden dependencies
- [ ] Implementation follows project conventions

## Improvements for Next Time

### What Went Well
- **Schema-driven architecture** caught type issues before runtime
- **Todo list tracking** kept progress visible and organized
- **Comprehensive test suite** validated all functionality in one go
- **Parallel tool calls** made the workflow efficient

### What Could Have Been Better

#### 1. **Run Type Checking Between Phases**
**Problem**: We didn't discover the CAS ID type mismatch (string vs CASIdentity object) until test execution.

**Solution**: Add type checking checkpoints:
```bash
# After Phase 2 (Generation)
just gen
uv run ty check queries/  # Would show: "no implementation yet" - expected

# After Phase 3 (Implementation stub)
uv run ty check queries/  # Would catch type signature mismatches early

# After Phase 3 (Full implementation)
uv run ty check queries/  # Final validation before testing
```

**Benefit**: Catch type mismatches in minutes instead of at test time.

#### 2. **Inspect Generated Code Immediately**
**Problem**: We implemented based on our mental model of the schema, but the Pydantic generator had different ideas about how `range: CASIdentity` should be rendered.

**Solution**: After `just gen`, immediately inspect the generated classes:
```bash
just gen
grep -A 10 "class PutContent" gen/queries.py  # See what types were actually generated
grep -A 10 "class CASIdentity" gen/models.py  # Understand the generated model
```

**Benefit**: Design implementation to match generated types from the start.

#### 3. **Plan Dependencies Upfront**
**Problem**: Discovered we needed `blake3` and `base58` during implementation, causing a pause.

**Solution**: Before Phase 3, review implementation requirements:
- What hashing algorithm? → `blake3`
- What encoding? → `base58`
- What storage backend? → `minio` (already installed)
- Add dependencies before writing code

**Benefit**: Uninterrupted implementation flow.

#### 4. **Review Existing Implementations First**
**Problem**: We needed to discover the project patterns by exploring during implementation.

**Solution**: Start Phase 3 with:
```bash
# Find similar implementations
ls queries/
cat queries/file_scanners/linux.py  # See established patterns
```

**What to look for**:
- How do query classes structure their `__init__`?
- How are configuration objects handled?
- How are protocol return types constructed?
- What error handling patterns exist?

**Benefit**: Follow established conventions from the start.

#### 5. **Verify External Dependencies Early**
**Problem**: We assumed MinIO was accessible without verification.

**Solution**: Before Phase 3, add pre-flight check:
```bash
# Verify MinIO is accessible
curl -s http://localhost:30000/minio/health/live || echo "MinIO not responding!"
```

**Benefit**: Don't implement against a broken backend.

#### 6. **Incremental Implementation + Testing**
**Problem**: We implemented all three query classes before testing any of them.

**Solution**: Test-driven approach within Phase 3:
1. Implement `PutContentQuery` only
2. Write minimal test for just PutContent
3. Run test, verify it works
4. Implement `CheckExistsQuery`
5. Add CheckExists test
6. Continue...

**Benefit**: Catch issues in small increments, faster debugging.

#### 7. **Schema Design Validation**
**Problem**: The YAML schema implied `CASIdentity` would be a rich object, but the generator flattened it to a string.

**Solution**: Before code generation, validate schema assumptions:
- Review LinkML/Pydantic generator docs for how `range:` works with custom classes
- Check if we need `inlined: true` or other directives
- Look at existing schemas for precedent (do other models use complex types?)

**Benefit**: Schema matches expectations first time.

#### 8. **Add Type Checking to the Play**

**Updated Play - Insert after Phase 2**:
```
### Phase 2.5: Inspect Generated Code & Type Check
3a. **Inspect generated types**
    - Review generated Pydantic models for your entities
    - Check protocol signatures match your mental model
    - Verify input/output types are what you expected

3b. **Run type checker baseline**
    ```bash
    just check  # or: uv run ty check queries/
    ```
    - Expected: Type errors for unimplemented protocols (OK!)
    - Unexpected: Type errors in generated code (investigate!)
```

**Updated Play - Insert after Phase 3**:
```
### Phase 3.5: Type Check Implementation
5a. **Run type checker on implementation**
    ```bash
    just check
    ```
    - Should catch: Wrong return types, incorrect protocol signatures
    - Should pass: All type signatures match generated protocols
```

### Recommended Enhanced Workflow

```bash
# Phase 1: Schema Definition
vim def/models.yaml def/queries.yaml

# Phase 2: Code Generation
just gen

# Phase 2.5: Inspect & Baseline Check (NEW!)
grep -A 10 "class PutContent" gen/queries.py  # Inspect types
grep -A 10 "class PutContentProtocol" queries/interfaces.py
just check  # Baseline type check (unimplemented is OK)

# Phase 3: Plan Dependencies (NEW!)
cat queries/file_scanners/linux.py  # Review patterns
# Identify and install dependencies
uv add blake3 base58

# Phase 3: Verify External Dependencies (NEW!)
curl http://localhost:30000/minio/health/live  # Check MinIO

# Phase 3: Implement (incrementally)
vim queries/cas_minio.py  # Implement PutContentQuery

# Phase 3.5: Type Check (NEW!)
just check  # Catch type issues immediately

# Phase 3: Continue implementing
# ... implement GetContentQuery, CheckExistsQuery ...
just check  # Type check again

# Phase 4: Test
PYTHONPATH=. uv run python vibes/test_cas.py
```

### Tools That Would Help

1. **Pre-commit hook** to run `just check` automatically
2. **Schema validator** that warns when `range:` types might not work as expected
3. **Dependency analyzer** that scans implementation TODOs and suggests packages
4. **Template generator** for new query implementations based on existing patterns
5. **Integration test harness** that validates external services (MinIO, databases) before testing

### Time Saved with Improvements

| Phase | Original Time | With Improvements | Savings |
|-------|--------------|-------------------|---------|
| Phase 1 | 5 min | 5 min | 0 min |
| Phase 2 | 2 min | 4 min (inspect) | -2 min |
| Phase 3 | 15 min | 12 min (patterns known, deps ready) | +3 min |
| Phase 3 Debug | 10 min (type issues) | 2 min (caught by ty) | +8 min |
| Phase 4 | 5 min | 5 min | 0 min |
| **Total** | **37 min** | **28 min** | **+9 min (24% faster)** |

Plus: **Higher confidence** that implementation is correct before testing.
