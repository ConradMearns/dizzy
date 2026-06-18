# The derivation chain for an entity, rendered newest-source-first, e.g.
#   garlic_croutons wasDerivedFrom sourdough_loaf
#   sourdough_loaf wasDerivedFrom active_starter
from gen_int.python.query.trace_provenance import trace_provenance_context
from gen_def.pydantic.query.trace_provenance import TraceProvenanceInput, TraceProvenanceOutput
from gen_def.sqla.models.provenance import ProvGeneration, ProvDerivation


def trace_provenance(
    input: TraceProvenanceInput, context: trace_provenance_context
) -> TraceProvenanceOutput:
    session = context.adapter.session

    def type_of(entity_id: str) -> str:
        generation = session.get(ProvGeneration, entity_id)
        return generation.entity_type if generation is not None else entity_id

    lines: list[str] = []
    current = input.entity_id
    seen: set[str] = set()
    while current is not None and current not in seen:
        seen.add(current)
        edge = session.get(ProvDerivation, current)
        if edge is None:
            break
        lines.append(f"{type_of(current)} wasDerivedFrom {type_of(edge.source_entity_id)}")
        current = edge.source_entity_id

    return TraceProvenanceOutput(lines=lines)
