import pytest
import networkx as nx
from typing import List, Dict, Type, Set

from pydantic.dataclasses import dataclass

from dizzy.command_queue import CommandQueueSystem, CommandQueue, Event, Listener


# Sample events for testing
@dataclass
class EventA(Event):
    value: str

@dataclass
class EventB(Event):
    value: str

@dataclass
class EventC(Event):
    value: str

@dataclass
class EventD(Event):
    value: str


# Sample listeners with output_type_hints
class ListenerAtoB(Listener):
    output_type_hints = [EventB]
    
    def run(self, queue: CommandQueue, event: EventA):
        queue.emit(EventB(value=f"B from {event.value}"))


class ListenerBtoC(Listener):
    output_type_hints = [EventC]
    
    def run(self, queue: CommandQueue, event: EventB):
        queue.emit(EventC(value=f"C from {event.value}"))


class ListenerCtoD(Listener):
    output_type_hints = [EventD]
    
    def run(self, queue: CommandQueue, event: EventC):
        queue.emit(EventD(value=f"D from {event.value}"))


def build_dag(system: CommandQueueSystem) -> nx.DiGraph:
    """
    Build a Directed Acyclic Graph (DAG) from a CommandQueueSystem.
    
    Both Events and Listeners are nodes in the graph.
    Edges represent the flow from input events to listeners and from listeners to output events.
    
    Args:
        system: The CommandQueueSystem to analyze
        
    Returns:
        A networkx DiGraph representing the event flow
    """
    G = nx.DiGraph()
    
    # Add all registered event types as nodes
    for event_type in system.registered_events.values():
        G.add_node(event_type.__name__, type="event", event_type=event_type)
    
    # Add listeners as nodes and create edges
    for event_type, listeners in system.listeners.items():
        for i, listener in enumerate(listeners):
            # Create a unique ID for each listener instance
            listener_id = f"{type(listener).__name__}_{id(listener)}"
            
            # Add listener node
            G.add_node(listener_id, type="listener", listener_class=type(listener).__name__)
            
            # Add edge from input event to listener
            input_type = listener.input_type_hint()
            G.add_edge(input_type.__name__, listener_id)
            
            # Add edges from listener to output events
            output_types = listener.__class__.output_type_hints
            for output_type in output_types:
                G.add_edge(listener_id, output_type.__name__)
    
    return G


def test_dag_construction():
    """Test that we can construct a DAG from type hints and verify it's acyclic."""
    # Set up the command queue system
    system = CommandQueueSystem()
    
    # Register listeners
    listener_a_to_b = ListenerAtoB()
    listener_b_to_c = ListenerBtoC()
    listener_c_to_d = ListenerCtoD()
    
    system.subscribe(EventA, listener_a_to_b)
    system.subscribe(EventB, listener_b_to_c)
    system.subscribe(EventC, listener_c_to_d)
    
    # Build the DAG
    G = build_dag(system)
    
    # Verify that the graph is a DAG (no cycles)
    assert nx.is_directed_acyclic_graph(G), "Graph should be acyclic"
    
    # Get listener node IDs
    listener_a_to_b_id = f"ListenerAtoB_{id(listener_a_to_b)}"
    listener_b_to_c_id = f"ListenerBtoC_{id(listener_b_to_c)}"
    listener_c_to_d_id = f"ListenerCtoD_{id(listener_c_to_d)}"
    
    # Verify event nodes exist
    event_nodes = [node for node, attrs in G.nodes(data=True) if attrs.get('type') == 'event']
    assert set(event_nodes) == {"EventA", "EventB", "EventC", "EventD"}
    
    # Verify listener nodes exist
    listener_nodes = [node for node, attrs in G.nodes(data=True) if attrs.get('type') == 'listener']
    assert len(listener_nodes) == 3
    
    # Verify the expected edges
    expected_edges = [
        ("EventA", listener_a_to_b_id),
        (listener_a_to_b_id, "EventB"),
        ("EventB", listener_b_to_c_id),
        (listener_b_to_c_id, "EventC"),
        ("EventC", listener_c_to_d_id),
        (listener_c_to_d_id, "EventD")
    ]
    
    for src, dst in expected_edges:
        assert G.has_edge(src, dst), f"Expected edge from {src} to {dst}"


def test_dag_with_cycle():
    """Test that a cycle in the event flow is detected."""
    # Set up the command queue system with a cycle
    system = CommandQueueSystem()
    
    # Create a cycle: A -> B -> C -> A
    class CycleListenerCtoA(Listener):
        output_type_hints = [EventA]
        
        def run(self, queue: CommandQueue, event: EventC):
            queue.emit(EventA(value=f"A from {event.value}"))
    
    # Register listeners to create a cycle
    listener_a_to_b = ListenerAtoB()
    listener_b_to_c = ListenerBtoC()
    listener_c_to_a = CycleListenerCtoA()
    
    system.subscribe(EventA, listener_a_to_b)
    system.subscribe(EventB, listener_b_to_c)
    system.subscribe(EventC, listener_c_to_a)
    
    # Build the DAG
    G = build_dag(system)
    
    # Verify that the graph is NOT a DAG (has cycles)
    assert not nx.is_directed_acyclic_graph(G), "Graph should have cycles"
    
    # Find and print the cycles for debugging
    cycles = list(nx.simple_cycles(G))
    assert len(cycles) > 0, "Expected at least one cycle"
    
    # Verify the cycle contains the expected nodes
    # The cycle should be: EventA -> ListenerAtoB -> EventB -> ListenerBtoC -> EventC -> CycleListenerCtoA -> EventA
    listener_a_to_b_id = f"ListenerAtoB_{id(listener_a_to_b)}"
    listener_b_to_c_id = f"ListenerBtoC_{id(listener_b_to_c)}"
    listener_c_to_a_id = f"CycleListenerCtoA_{id(listener_c_to_a)}"
    
    # Check if any cycle contains all the expected nodes
    expected_nodes = {"EventA", "EventB", "EventC", listener_a_to_b_id, listener_b_to_c_id, listener_c_to_a_id}
    cycle_nodes = set()
    for cycle in cycles:
        cycle_nodes.update(cycle)
    
    # The cycle nodes should be a subset of the expected nodes
    assert expected_nodes.issubset(cycle_nodes), f"Expected cycle nodes {expected_nodes} to be in {cycle_nodes}"

if __name__ == "__main__":
    import dagviz

    system = CommandQueueSystem()
    
    # Register listeners
    system.subscribe(EventA, ListenerAtoB())
    system.subscribe(EventB, ListenerBtoC())
    system.subscribe(EventB, ListenerBtoC())
    system.subscribe(EventB, ListenerBtoC())
    system.subscribe(EventC, ListenerCtoD())
    
    # Build the DAG
    G = build_dag(system)

    r = dagviz.render_svg(G)
    print(r)
    with open('dag.svg', 'w') as f:
        f.write(r)
