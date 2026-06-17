# Implementation — turn an AddBook command into a BookAdded fact.
from uuid import uuid4

from gen_int.python.procedure.catalog_book_context import catalog_book_context
from gen_def.pydantic.commands import AddBook
from gen_def.pydantic.events import BookAdded


def catalog_book(
    context: catalog_book_context,
    command: AddBook,
) -> None:
    # Business rule: a catalog entry needs at least one copy and a title.
    if command.copies < 1:
        raise ValueError("copies must be >= 1")
    if not command.title.strip():
        raise ValueError("title must not be empty")

    # Mint the catalog id here — events are immutable facts, so bake identity in.
    context.emit.book_added(
        BookAdded(
            catalog_id=str(uuid4()),
            title=command.title.strip(),
            copies=command.copies,
        )
    )
