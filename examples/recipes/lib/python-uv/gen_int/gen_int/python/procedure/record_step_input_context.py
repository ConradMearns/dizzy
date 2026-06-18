# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Callable

from gen_def.pydantic.events import StepInputAdded


@dataclass
class record_step_input_emitters:
    step_input_added: Callable[[StepInputAdded], None]


@dataclass
class record_step_input_context:
    emit: record_step_input_emitters
