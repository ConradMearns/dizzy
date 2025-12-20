#!/usr/bin/env python3
"""
Generic test script for running dizzy procedures.

Usage:
    python run_procedure.py --feature <feature.yaml> --procedure <path/to/procedure.py> --procedure-name <name> --command <json_command>

Example:
    python run_procedure.py \\
        --feature app/dedupe/scan_and_upload.feat.yaml \\
        --procedure app/dedupe/scan_and_upload/src/procedure/lcpc_a_py/start_scan.py \\
        --procedure-name partition_scan \\
        --command '{"path": "/tmp/test"}'
"""

import argparse
import importlib.util
import json
import logging
import sys
from pathlib import Path
from typing import Any, Callable

import yaml


# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_procedure_module(procedure_path: str):
    """Dynamically load a procedure module from a file path."""
    procedure_file = Path(procedure_path)

    if not procedure_file.exists():
        raise FileNotFoundError(f"Procedure file not found: {procedure_path}")

    # Create a module spec from the file
    module_name = procedure_file.stem
    spec = importlib.util.spec_from_file_location(module_name, procedure_file)

    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {procedure_path}")

    # Load the module
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module


def find_procedure_function(module):
    """Find the procedure function in the module (ends with _procedure)."""
    for attr_name in dir(module):
        if attr_name.endswith('_procedure') and callable(getattr(module, attr_name)):
            return getattr(module, attr_name)

    raise ValueError(f"No procedure function found in module {module.__name__}")


def create_mock_emitter(event_name: str) -> Callable:
    """Create a mock emitter function that logs events."""
    def mock_emit(event: Any) -> None:
        logger.info(f"[EVENT EMIT] {event_name}: {event}")
    return mock_emit


def load_feature_yaml(feature_path: str) -> dict:
    """Load and parse the feature YAML file."""
    feature_file = Path(feature_path)

    if not feature_file.exists():
        raise FileNotFoundError(f"Feature file not found: {feature_path}")

    with open(feature_file, 'r') as f:
        return yaml.safe_load(f)


def get_procedure_events(feature_data: dict, procedure_name: str) -> list[str]:
    """Extract the list of events emitted by a procedure from feature YAML."""
    procedures = feature_data.get('procedures', {})

    for proc_name, proc_def in procedures.items():
        if proc_name == procedure_name:
            return proc_def.get('emits', [])

    raise ValueError(f"Procedure '{procedure_name}' not found in feature YAML")


def create_mock_context(context_class, event_names: list[str]):
    """Create a mock context with logging emitters based on feature YAML event list."""
    # Get the emitters and queries classes from the context
    emitters_class = None
    queries_class = None

    for field in context_class.__dataclass_fields__.values():
        if 'emitters' in field.type.__name__:
            emitters_class = field.type
        elif 'queries' in field.type.__name__:
            queries_class = field.type

    if emitters_class is None:
        raise ValueError("Could not find emitters class in context")

    # Create mock emitters for each event
    emitter_fields = {}
    for event_name in event_names:
        emitter_fields[event_name] = create_mock_emitter(event_name)

    emitters = emitters_class(**emitter_fields)

    # Create empty queries object
    queries = queries_class() if queries_class else None

    # Create the context
    context = context_class(emit=emitters, query=queries)

    return context


def parse_command_json(command_json: str, command_class) -> Any:
    """Parse JSON command and create command object."""
    command_data = json.loads(command_json)
    return command_class(**command_data)


def main():
    parser = argparse.ArgumentParser(
        description='Run a dizzy procedure with a JSON command',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--feature',
        required=True,
        help='Path to the feature YAML file (e.g., app/dedupe/scan_and_upload.feat.yaml)'
    )
    parser.add_argument(
        '--procedure',
        required=True,
        help='Path to the procedure Python file'
    )
    parser.add_argument(
        '--procedure-name',
        required=True,
        help='Name of the procedure from the feature YAML (e.g., partition_scan)'
    )
    parser.add_argument(
        '--command',
        required=True,
        help='JSON command to execute'
    )

    args = parser.parse_args()

    try:
        # Load feature YAML to understand procedure configuration
        logger.info(f"Loading feature YAML from: {args.feature}")
        feature_data = load_feature_yaml(args.feature)

        logger.info(f"Loading procedure from: {args.procedure}")

        # Add the dizzy root to sys.path so imports work
        dizzy_root = Path(__file__).parent
        if str(dizzy_root) not in sys.path:
            sys.path.insert(0, str(dizzy_root))

        # Also add the app directory
        app_root = dizzy_root / "app" / "dedupe" / "scan_and_upload"
        if str(app_root) not in sys.path:
            sys.path.insert(0, str(app_root))

        # Load the procedure module
        procedure_module = load_procedure_module(args.procedure)
        procedure_function = find_procedure_function(procedure_module)

        logger.info(f"Found procedure function: {procedure_function.__name__}")

        # Get the function signature to determine context type
        import inspect
        sig = inspect.signature(procedure_function)
        params = list(sig.parameters.values())

        if len(params) < 2:
            raise ValueError("Procedure must accept at least 2 parameters (context, command)")

        context_class = params[0].annotation
        logger.info(f"Context type: {context_class.__name__}")

        # Get procedure name from CLI argument
        procedure_name = args.procedure_name
        logger.info(f"Procedure name: {procedure_name}")

        # Look up the procedure in the feature YAML
        procedures = feature_data.get('procedures', {})
        if procedure_name not in procedures:
            raise ValueError(f"Procedure '{procedure_name}' not found in feature YAML")

        procedure_def = procedures[procedure_name]
        command_type_name = procedure_def.get('command')

        if not command_type_name:
            raise ValueError(f"Procedure '{procedure_name}' does not specify a command in feature YAML")

        logger.info(f"Command type from feature YAML: {command_type_name}")

        # Dynamically import the command class based on the YAML
        # Import the module and find the class with matching class_name
        import importlib
        command_module = importlib.import_module(f"gen.commands.pyd.{command_type_name}")

        # Find the class in the module that has class_name matching our command type
        command_class = None
        for attr_name in dir(command_module):
            attr = getattr(command_module, attr_name)
            if (isinstance(attr, type) and
                hasattr(attr, 'class_name') and
                attr.class_name == command_type_name):
                command_class = attr
                break

        if command_class is None:
            raise ValueError(f"Could not find command class for '{command_type_name}' in module")

        logger.info(f"Command class: {command_class.__name__}")

        # Get the events this procedure emits
        event_names = get_procedure_events(feature_data, procedure_name)
        logger.info(f"Events emitted by procedure: {event_names}")

        # Parse the command JSON
        logger.info(f"Parsing command: {args.command}")
        command = parse_command_json(args.command, command_class)

        # Create mock context with events from feature YAML
        logger.info("Creating mock context")
        context = create_mock_context(context_class, event_names)

        # Execute the procedure
        logger.info("=" * 60)
        logger.info("EXECUTING PROCEDURE")
        logger.info("=" * 60)
        procedure_function(context, command)
        logger.info("=" * 60)
        logger.info("PROCEDURE COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Procedure execution failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
