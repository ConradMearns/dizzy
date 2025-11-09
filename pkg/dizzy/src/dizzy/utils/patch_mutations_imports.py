#!/usr/bin/env python3

"""
Post-process generated mutations.py to import DomainEvent from events module.

This utility patches the gen/mutations.py file after generation to ensure
that DomainEvent is imported from gen.events rather than being redefined.
This ensures type compatibility between events and mutations.
"""

import re
from pathlib import Path


def patch_mutations_file(mutations_py: Path):
    """
    Patch mutations.py to import DomainEvent from events module.

    Args:
        mutations_py: Path to the generated gen/mutations.py file
    """
    if not mutations_py.exists():
        print(f"Error: File not found: {mutations_py}")
        return False

    # Read the file
    content = mutations_py.read_text()

    # Check if already patched
    if 'from gen.events import DomainEvent' in content:
        print(f"File already patched: {mutations_py}")
        return True

    # Add the import after the pydantic imports
    import_line = '\n# Import DomainEvent from events module to ensure type compatibility\nfrom gen.events import DomainEvent\n'

    # Find the location to insert (after pydantic imports, before metamodel_version)
    pattern = r'(\)\n)(\n+metamodel_version = "None")'
    replacement = r'\1' + import_line + r'\2'

    new_content = re.sub(pattern, replacement, content)

    if new_content == content:
        print(f"Warning: Could not find insertion point in {mutations_py}")
        return False

    # Remove the DomainEvent class definition
    # Match the class definition and its docstring/pass statement
    domain_event_pattern = r'\n\nclass DomainEvent\(ConfiguredBaseModel\):.*?\n    pass\n'
    new_content = re.sub(domain_event_pattern, '', new_content, flags=re.DOTALL)

    # Write back
    mutations_py.write_text(new_content)
    print(f"✓ Patched mutations.py: Added DomainEvent import from events module")
    return True


def main():
    """CLI entry point when run as script."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m dizzy.utils.patch_mutations_imports <gen/mutations.py>")
        sys.exit(1)

    mutations_py = Path(sys.argv[1])
    success = patch_mutations_file(mutations_py)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
