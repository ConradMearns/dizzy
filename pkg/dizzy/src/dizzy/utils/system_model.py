"""System model for representing the parsed LinkML schema structure."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class Command:
    """Represents a command in the system."""
    name: str
    description: Optional[str] = None


@dataclass
class Event:
    """Represents an event in the system."""
    name: str
    description: Optional[str] = None


@dataclass
class Query:
    """Represents a query in the system."""
    name: str
    description: Optional[str] = None


@dataclass
class Mutator:
    """Represents a mutator in the system."""
    name: str
    description: Optional[str] = None


@dataclass
class Procedure:
    """Represents a procedure that handles a command."""
    name: str
    command: str
    emitters: Dict[str, str] = field(default_factory=dict)  # emitter_name -> event_type
    queries: Dict[str, str] = field(default_factory=dict)  # query_name -> query_type


@dataclass
class Policy:
    """Represents a policy that handles an event."""
    name: str
    event: str
    emitters: Dict[str, str] = field(default_factory=dict)  # emitter_name -> command_type
    queries: Dict[str, str] = field(default_factory=dict)  # query_name -> query_type
    mutators: Dict[str, str] = field(default_factory=dict)  # mutator_name -> mutator_type


@dataclass
class System:
    """Represents the entire system architecture."""

    # Core entities
    commands: Dict[str, Command] = field(default_factory=dict)
    events: Dict[str, Event] = field(default_factory=dict)
    queries: Dict[str, Query] = field(default_factory=dict)
    mutators: Dict[str, Mutator] = field(default_factory=dict)

    # Relationships
    procedures: Dict[str, Procedure] = field(default_factory=dict)
    policies: Dict[str, Policy] = field(default_factory=dict)

    def get_command_to_procedure_map(self) -> Dict[str, str]:
        """Map command names to procedure names."""
        return {proc.command: proc_name for proc_name, proc in self.procedures.items()}

    def get_event_to_policy_map(self) -> Dict[str, List[str]]:
        """Map event names to list of policy names that handle them."""
        result: Dict[str, List[str]] = {}
        for policy_name, policy in self.policies.items():
            if policy.event not in result:
                result[policy.event] = []
            result[policy.event].append(policy_name)
        return result

    def get_procedure_emitted_events(self) -> Dict[str, Set[str]]:
        """Map procedure names to the events they emit."""
        result: Dict[str, Set[str]] = {}
        for proc_name, proc in self.procedures.items():
            result[proc_name] = set(proc.emitters.values())
        return result

    def get_policy_emitted_commands(self) -> Dict[str, Set[str]]:
        """Map policy names to the commands they emit."""
        result: Dict[str, Set[str]] = {}
        for policy_name, policy in self.policies.items():
            result[policy_name] = set(policy.emitters.values())
        return result

    def get_procedure_queries(self) -> Dict[str, Set[str]]:
        """Map procedure names to the queries they use."""
        result: Dict[str, Set[str]] = {}
        for proc_name, proc in self.procedures.items():
            result[proc_name] = set(proc.queries.values())
        return result

    def get_policy_queries(self) -> Dict[str, Set[str]]:
        """Map policy names to the queries they use."""
        result: Dict[str, Set[str]] = {}
        for policy_name, policy in self.policies.items():
            result[policy_name] = set(policy.queries.values())
        return result

    def get_policy_mutators(self) -> Dict[str, Set[str]]:
        """Map policy names to the mutators they use."""
        result: Dict[str, Set[str]] = {}
        for policy_name, policy in self.policies.items():
            result[policy_name] = set(policy.mutators.values())
        return result
