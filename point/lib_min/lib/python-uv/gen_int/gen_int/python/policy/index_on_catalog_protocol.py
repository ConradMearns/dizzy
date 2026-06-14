# AUTO-GENERATED — do not edit
from typing import Protocol

from gen_def.pydantic.events import BookAdded
from gen_int.python.policy.index_on_catalog_context import (
    index_on_catalog_context,
)


class index_on_catalog_protocol(Protocol):
    """When a book is cataloged, queue it for search indexing by dispatching
index_book for the same catalog id and title. A policy dispatches commands;
it never emits events (the mirror of a procedure)."""

    def __call__(
        self,
        event: BookAdded,
        context: index_on_catalog_context,
    ) -> None:
        ...
