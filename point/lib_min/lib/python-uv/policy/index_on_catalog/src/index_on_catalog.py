# Implementation — when a book is cataloged, dispatch index_book (a command).
# A policy dispatches commands; it never emits events (the mirror of a procedure).
from gen_int.python.policy.index_on_catalog_context import index_on_catalog_context
from gen_def.pydantic.events import BookAdded
from gen_def.pydantic.commands import IndexBook


def index_on_catalog(
    event: BookAdded,
    context: index_on_catalog_context,
) -> None:
    context.emit.index_book(
        IndexBook(
            catalog_id=event.catalog_id,
            title=event.title,
        )
    )
