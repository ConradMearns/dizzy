# AUTO-GENERATED — do not edit
from typing import Protocol

from gen_def.pydantic.commands import NotifyNextPatron
from gen_int.python.procedure.send_notification_context import (
    send_notification_context,
)


class send_notification_protocol(Protocol):
    """Record that a patron was notified their held book is ready"""

    def __call__(
        self,
        context: send_notification_context,
        command: NotifyNextPatron,
    ) -> None:
        ...
