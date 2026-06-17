# AUTO-GENERATED — do not edit
from typing import Protocol

from gen_def.pydantic.events import BookReturned
from gen_int.python.policy.notify_next_on_return_context import (
    notify_next_on_return_context,
)


class notify_next_on_return_protocol(Protocol):
    """When a book is returned, consult the hold queue and, if a patron is waiting, dispatch a notification command for the next one in line."""

    def __call__(
        self,
        event: BookReturned,
        context: notify_next_on_return_context,
    ) -> None:
        ...
