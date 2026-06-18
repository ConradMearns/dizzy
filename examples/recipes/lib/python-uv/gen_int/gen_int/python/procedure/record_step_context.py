# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Callable

from gen_def.pydantic.events import RecipeStepAdded


@dataclass
class record_step_emitters:
    recipe_step_added: Callable[[RecipeStepAdded], None]


@dataclass
class record_step_context:
    emit: record_step_emitters
