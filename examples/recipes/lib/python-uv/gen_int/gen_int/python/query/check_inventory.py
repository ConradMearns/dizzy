# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.query.check_inventory import CheckInventoryInput, CheckInventoryOutput
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class check_inventory_context:
    adapter: SqlaAdapter


class check_inventory_query(Protocol):
    """Whether an available entity of a given type exists, and its id"""

    def __call__(
        self, input: CheckInventoryInput, context: check_inventory_context
    ) -> CheckInventoryOutput:
        ...
