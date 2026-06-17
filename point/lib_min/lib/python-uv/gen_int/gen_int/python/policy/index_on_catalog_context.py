# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Callable

from gen_def.pydantic.commands import IndexBook


@dataclass
class index_on_catalog_emitters:
    index_book: Callable[[IndexBook], None]


@dataclass
class index_on_catalog_context:
    emit: index_on_catalog_emitters
