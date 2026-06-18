# AUTO-GENERATED — do not edit
from typing import Protocol

from gen_def.pydantic.commands import StartBatch
from gen_int.python.procedure.open_batch_context import (
    open_batch_context,
)


class open_batch_protocol(Protocol):
    """Open a batch for a recipe. Look up the recipe's requires_type; if it is empty the batch is immediately ready. Otherwise ask check_inventory whether an entity of that type is available: if so the batch is ready, if not it is blocked. Emit batch_opened with the resolved status and requires_type so the cascade policy can find it later."""

    def __call__(
        self,
        context: open_batch_context,
        command: StartBatch,
    ) -> None:
        ...
