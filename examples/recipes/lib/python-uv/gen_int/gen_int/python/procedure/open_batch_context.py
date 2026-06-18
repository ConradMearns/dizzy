# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Callable

from gen_def.pydantic.events import BatchOpened
from gen_def.pydantic.query.get_recipe import GetRecipeInput, GetRecipeOutput
from gen_def.pydantic.query.check_inventory import CheckInventoryInput, CheckInventoryOutput


@dataclass
class open_batch_emitters:
    batch_opened: Callable[[BatchOpened], None]


@dataclass
class open_batch_queries:
    get_recipe: Callable[[GetRecipeInput], GetRecipeOutput]
    check_inventory: Callable[[CheckInventoryInput], CheckInventoryOutput]


@dataclass
class open_batch_context:
    emit: open_batch_emitters
    query: open_batch_queries
