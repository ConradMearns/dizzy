# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Callable

from gen_def.pydantic.events import HoldPlaced


@dataclass
class record_hold_emitters:
    hold_placed: Callable[[HoldPlaced], None]


@dataclass
class record_hold_context:
    emit: record_hold_emitters
