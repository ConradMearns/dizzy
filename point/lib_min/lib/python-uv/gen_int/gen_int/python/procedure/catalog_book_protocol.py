# AUTO-GENERATED — do not edit
from typing import Protocol

from gen_def.pydantic.commands import AddBook
from gen_int.python.procedure.catalog_book_context import (
    catalog_book_context,
)


class catalog_book_protocol(Protocol):
    """Record that a book was added to the catalog. Stamp a catalog id and carry
the title and copy count onto the book_added fact."""

    def __call__(
        self,
        context: catalog_book_context,
        command: AddBook,
    ) -> None:
        ...
