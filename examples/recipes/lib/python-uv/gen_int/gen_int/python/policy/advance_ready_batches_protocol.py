# AUTO-GENERATED — do not edit
from typing import Protocol

from gen_def.pydantic.events import EntityProduced
from gen_int.python.policy.advance_ready_batches_context import (
    advance_ready_batches_context,
)


class advance_ready_batches_protocol(Protocol):
    """When an entity is produced, exactly one lot of it now exists — so it can unblock exactly one waiting batch. Consult find_blocked_batches for the produced type (oldest-first) and dispatch advance_batch for only the first one. A policy emits commands only — never events — so the host routes advance_batch back into run_batch, whose own entity_produced re-triggers this policy. Producing N lots advances N waiting batches, one per lot; the cascade ends when nothing is waiting for the produced type."""

    def __call__(
        self,
        event: EntityProduced,
        context: advance_ready_batches_context,
    ) -> None:
        ...
