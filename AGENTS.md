<general_rules>
When creating new Event classes, always search in `dizzy/domain/` first to see if a similar event already exists before creating a new one. All Event classes must use the `@dataclass` decorator and inherit from the base `Event` class, following the pattern established in `dizzy/event_loop.py` lines 48-50.

When creating new Listeners, first check existing handlers in `dizzy/domain/command_handler.py` to see if similar functionality exists. All Listeners must inherit from the abstract `Listener` class and implement the `run(self, queue: EventQueue, event: Event)` method.

For provenance tracking, always use DuckDB following the patterns established in `dizzy/domain/event_system.py` lines 115-192. The framework provides `ProvenanceDuckDBListener` as a base class for provenance-related event handlers.

Use Poetry for all dependency management. Install dependencies with `poetry install` and add new dependencies with `poetry add <package>`. Never use pip directly in this project.

The framework follows an event-driven architecture where Events are emitted to EventQueues and processed by registered Listeners. Always emit events through the EventSystem rather than directly manipulating queues.

When working with the command queue system, use the `CommandQueueSystem` class which provides instrumentation and meta-event capabilities for tracking system behavior.
</general_rules>

<repository_structure>
The repository is organized around the main `dizzy/` package which implements an event-driven processing framework:

- `dizzy/domain/`: Core domain logic including the EventSystem, CommandQueue, and provenance tracking handlers. This is the heart of the framework containing event system primitives and command handling patterns.

- `dizzy/dedupe/`: Deduplication logic and event system extensions for handling duplicate data processing scenarios.

- `dizzy/fuse/`: Filesystem operations and FUSE-based virtual filesystem implementations for tag-based file organization.

- `docs/`: Documentation source files using MkDocs with Material theme. Contains comprehensive framework documentation and examples.

- `prov_command.py`: Root-level script demonstrating DuckDB-based event storage and provenance tracking patterns.

The framework's core files `event_loop.py` and `event_loop_emitting.py` in the root `dizzy/` directory contain the fundamental EventSystem, EventQueue, and Listener abstractions that all other components build upon.

Configuration files include `pyproject.toml` for Poetry dependency management, `mkdocs.yml` for documentation generation, and `.github/workflows/ci.yml` for automated documentation deployment.
</repository_structure>

<dependencies_and_installation>
This project uses Poetry for dependency management and requires Python 3.11 or higher.

Install all dependencies with: `poetry install`

Core runtime dependencies include:
- `duckdb`: In-process database for provenance tracking and event storage
- `typer`: CLI framework with rich terminal features
- `rich`: Rich text and beautiful formatting for console output

For documentation development, install docs dependencies with: `poetry install --with docs`

Documentation dependencies include MkDocs with Material theme, mkdocstrings for API documentation generation, and various MkDocs plugins for enhanced documentation features.

The project includes a `shell.nix` file for Nix users, though Poetry remains the primary dependency management approach.

Always use `poetry run <command>` to execute scripts within the virtual environment, or activate the environment first with `poetry shell`.
</dependencies_and_installation>

<testing_instructions>
While pytest is available in the poetry.lock file, no formal testing framework is currently configured in this repository. Developers should add comprehensive tests when implementing new features.

When adding tests, create them in a `tests/` directory following standard pytest conventions. Focus testing efforts on:
- Event/Listener interactions and the EventSystem behavior
- Command queue processing and instrumentation
- Provenance tracking and DuckDB integration
- Deduplication logic and filesystem operations

Run tests with `poetry run pytest` once test files are created. Consider adding test configuration to `pyproject.toml` for consistent test execution across the project.

The framework's event-driven nature makes it well-suited for integration testing where you can emit events and verify the expected listeners are triggered with correct behavior.

Given the framework's focus on provenance and data processing pipelines, tests should verify both functional correctness and proper event tracking/storage in DuckDB.
</testing_instructions>

<pull_request_formatting>
</pull_request_formatting>
