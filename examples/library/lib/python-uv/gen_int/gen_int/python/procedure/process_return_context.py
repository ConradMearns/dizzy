# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Callable

from gen_def.pydantic.events import BookReturned


@dataclass
class process_return_emitters:
    book_returned: Callable[[BookReturned], None]


@dataclass
class process_return_context:
    emit: process_return_emitters
