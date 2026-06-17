# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Callable

from gen_def.pydantic.commands import NotifyNextPatron
from gen_def.pydantic.query.get_next_hold import GetNextHoldInput, GetNextHoldOutput


@dataclass
class notify_next_on_return_emitters:
    notify_next_patron: Callable[[NotifyNextPatron], None]


@dataclass
class notify_next_on_return_queries:
    get_next_hold: Callable[[GetNextHoldInput], GetNextHoldOutput]


@dataclass
class notify_next_on_return_context:
    emit: notify_next_on_return_emitters
    query: notify_next_on_return_queries
