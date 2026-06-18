# AUTO-GENERATED — do not edit
from typing import Protocol

from gen_def.pydantic.events import EntityProduced
from gen_int.python.policy.advance_ready_batches_context import (
    advance_ready_batches_context,
)


class advance_ready_batches_protocol(Protocol):
    """When an entity is produced, any batch that was blocked waiting for that entity type is now ready. Consult find_blocked_batches for the produced type and dispatch advance_batch for each waiting batch. A policy emits commands only — never events — so the host routes advance_batch back into run_batch, whose entity_produced re-triggers this policy. The cascade ends when no batch is waiting for the produced type."""

    def __call__(
        self,
        event: EntityProduced,
        context: advance_ready_batches_context,
    ) -> None:
        ...
