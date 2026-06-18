# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Callable

from gen_def.pydantic.events import IngredientRegistered


@dataclass
class record_ingredient_emitters:
    ingredient_registered: Callable[[IngredientRegistered], None]


@dataclass
class record_ingredient_context:
    emit: record_ingredient_emitters
