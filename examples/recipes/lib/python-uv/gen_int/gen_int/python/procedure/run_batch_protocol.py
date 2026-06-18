# AUTO-GENERATED — do not edit
from typing import Protocol

from gen_def.pydantic.commands import AdvanceBatch
from gen_int.python.procedure.run_batch_context import (
    run_batch_context,
)


class run_batch_protocol(Protocol):
    """Run a batch to completion, emitting PROV relationship facts as it goes.
Resolve the batch's recipe via get_batch, then load the recipe header (get_recipe), its steps (get_recipe_steps) and step inputs (get_step_inputs).
For each step emit step_performed (the activity, with its tool). For each step input emit entity_consumed (prov:used). If the recipe has a requires_type, resolve the available upstream entity via check_inventory, emit entity_consumed for it, and after producing the output emit entity_derived to link output ⟶ source (prov:wasDerivedFrom).
Finally emit one entity_produced (prov:wasGeneratedBy) for the recipe's output_type — the signal the cascade policy listens for — then batch_completed."""

    def __call__(
        self,
        context: run_batch_context,
        command: AdvanceBatch,
    ) -> None:
        ...
