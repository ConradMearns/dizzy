# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Callable

from gen_def.pydantic.events import BookAdded


@dataclass
class catalog_book_emitters:
    book_added: Callable[[BookAdded], None]


@dataclass
class catalog_book_context:
    emit: catalog_book_emitters
