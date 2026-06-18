# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.query.trace_provenance import TraceProvenanceInput, TraceProvenanceOutput
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class trace_provenance_context:
    adapter: SqlaAdapter


class trace_provenance_query(Protocol):
    """The derivation chain for an entity, rendered newest-source-first"""

    def __call__(
        self, input: TraceProvenanceInput, context: trace_provenance_context
    ) -> TraceProvenanceOutput:
        ...
