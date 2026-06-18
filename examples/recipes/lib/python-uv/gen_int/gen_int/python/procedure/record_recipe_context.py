# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Callable

from gen_def.pydantic.events import RecipeDefined


@dataclass
class record_recipe_emitters:
    recipe_defined: Callable[[RecipeDefined], None]


@dataclass
class record_recipe_context:
    emit: record_recipe_emitters
