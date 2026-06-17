# Implementation — turn a NotifyNextPatron command into a PatronNotified fact.
from gen_int.python.procedure.send_notification_context import send_notification_context
from gen_def.pydantic.commands import NotifyNextPatron
from gen_def.pydantic.events import PatronNotified


def send_notification(
    context: send_notification_context,
    command: NotifyNextPatron,
) -> None:
    # A real system would send an email/SMS here; we just record that it happened.
    context.emit.patron_notified(
        PatronNotified(
            book_id=command.book_id,
            patron=command.patron,
        )
    )
