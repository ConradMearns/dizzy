#!/usr/bin/env python3
"""
Flow Report Generator

Reads definition files from def/ folder and produces a colored flow report showing:
- Command -> Procedure
- Procedure -> Event(s)
- Event -> Policy
- Policy -> Command(s)
"""

import yaml
from pathlib import Path
from typing import Dict, List, Tuple


# ANSI color codes
class Colors:
    COMMAND = '\033[94m'      # Blue
    PROCEDURE = '\033[38;5;208m'  # Orange
    EVENT = '\033[92m'        # Green
    POLICY = '\033[95m'       # Magenta
    ARROW = '\033[90m'        # Dark gray
    RESET = '\033[0m'


def load_procedures(def_path: Path) -> Dict:
    """Load procedures from procedures.d.yaml"""
    procedures_file = def_path / 'procedures.d.yaml'
    if not procedures_file.exists():
        return {}

    with open(procedures_file, 'r') as f:
        data = yaml.safe_load(f)
        return data.get('procedures', {})


def load_policies(def_path: Path) -> Dict:
    """Load policies from policies.d.yaml"""
    policies_file = def_path / 'policies.d.yaml'
    if not policies_file.exists():
        return {}

    with open(policies_file, 'r') as f:
        data = yaml.safe_load(f)
        return data.get('policies', {})


def print_flow_report(procedures: Dict, policies: Dict):
    """Print the flow report with colors"""

    print("\n" + "="*80)
    print("FLOW REPORT: Commands → Procedures → Events → Policies → Commands")
    print("="*80 + "\n")

    # Track which events are emitted (for finding orphaned policies)
    emitted_events = set()

    # 1. Command -> Procedure -> Event(s)
    print(f"{Colors.COMMAND}Commands → Procedures → Events:{Colors.RESET}")
    print("-" * 80)

    for procedure_name, procedure_config in procedures.items():
        command = procedure_config.get('command', 'Unknown')
        emitters = procedure_config.get('emitters', {})

        # Print Command -> Procedure
        print(f"{Colors.COMMAND}{command}{Colors.RESET} "
              f"{Colors.ARROW}→{Colors.RESET} "
              f"{Colors.PROCEDURE}{procedure_name}{Colors.RESET}")

        # Print Procedure -> Event(s)
        if emitters:
            for emitter_key, event_name in emitters.items():
                emitted_events.add(event_name)
                print(f"  {Colors.PROCEDURE}{procedure_name}{Colors.RESET} "
                      f"{Colors.ARROW}→{Colors.RESET} "
                      f"{Colors.EVENT}{event_name}{Colors.RESET}")
        else:
            print(f"  {Colors.PROCEDURE}{procedure_name}{Colors.RESET} "
                  f"{Colors.ARROW}→{Colors.RESET} (no events)")

        print()

    # 2. Event -> Policy -> Command(s)
    print(f"\n{Colors.EVENT}Events → Policies → Commands:{Colors.RESET}")
    print("-" * 80)

    for policy_name, policy_config in policies.items():
        event = policy_config.get('event', 'Unknown')
        emitters = policy_config.get('emitters', {})

        # Print Event -> Policy
        print(f"{Colors.EVENT}{event}{Colors.RESET} "
              f"{Colors.ARROW}→{Colors.RESET} "
              f"{Colors.POLICY}{policy_name}{Colors.RESET}")

        # Print Policy -> Command(s)
        if emitters:
            for emitter_key, command_name in emitters.items():
                print(f"  {Colors.POLICY}{policy_name}{Colors.RESET} "
                      f"{Colors.ARROW}→{Colors.RESET} "
                      f"{Colors.COMMAND}{command_name}{Colors.RESET}")
        else:
            print(f"  {Colors.POLICY}{policy_name}{Colors.RESET} "
                  f"{Colors.ARROW}→{Colors.RESET} (no commands)")

        print()

    # 3. Show potential loops
    print(f"\n{Colors.ARROW}Loop Detection:{Colors.RESET}")
    print("-" * 80)

    # Find commands that are both triggered and emitted
    triggered_commands = {p.get('command') for p in procedures.values()}
    emitted_commands = set()
    for policy_config in policies.values():
        emitted_commands.update(policy_config.get('emitters', {}).values())

    loop_commands = triggered_commands & emitted_commands
    if loop_commands:
        print(f"Commands that can create loops (both triggered and emitted):")
        for cmd in sorted(loop_commands):
            print(f"  {Colors.COMMAND}{cmd}{Colors.RESET}")
    else:
        print("No potential loops detected.")

    print("\n" + "="*80 + "\n")


def main():
    """Main entry point"""
    # Determine def/ path relative to this script
    script_dir = Path(__file__).parent
    def_path = script_dir.parent / 'def'

    if not def_path.exists():
        print(f"Error: def/ directory not found at {def_path}")
        return 1

    # Load data
    procedures = load_procedures(def_path)
    policies = load_policies(def_path)

    # Print report
    print_flow_report(procedures, policies)

    return 0


if __name__ == '__main__':
    exit(main())
