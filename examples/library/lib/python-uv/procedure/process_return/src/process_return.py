# Implementation — turn a ReturnBook command into a BookReturned fact.
from gen_int.python.procedure.process_return_context import process_return_context
from gen_def.pydantic.commands import ReturnBook
from gen_def.pydantic.events import BookReturned


def process_return(
    context: process_return_context,
    command: ReturnBook,
) -> None:
    if not command.book_id.strip():
        raise ValueError("return_book requires a book_id")

    # The procedure just records the fact. Deciding who to notify next is a
    # *reaction* to this fact, and lives in the notify_next_on_return policy.
    context.emit.book_returned(
        BookReturned(book_id=command.book_id.strip())
    )
