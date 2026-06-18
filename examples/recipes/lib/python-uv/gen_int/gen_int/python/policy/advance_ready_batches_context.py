# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Callable

from gen_def.pydantic.commands import AdvanceBatch
from gen_def.pydantic.query.find_blocked_batches import FindBlockedBatchesInput, FindBlockedBatchesOutput


@dataclass
class advance_ready_batches_emitters:
    advance_batch: Callable[[AdvanceBatch], None]


@dataclass
class advance_ready_batches_queries:
    find_blocked_batches: Callable[[FindBlockedBatchesInput], FindBlockedBatchesOutput]


@dataclass
class advance_ready_batches_context:
    emit: advance_ready_batches_emitters
    query: advance_ready_batches_queries
