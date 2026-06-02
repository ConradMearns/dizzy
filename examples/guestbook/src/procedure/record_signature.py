# Implementation — turn a SignGuestbook command into a GuestbookSigned fact.
from datetime import datetime, timezone
from uuid import uuid4

from gen_int.python.procedure.record_signature_context import record_signature_context
from gen_def.pydantic.commands import SignGuestbook
from gen_def.pydantic.events import GuestbookSigned


def record_signature(
    context: record_signature_context,
    command: SignGuestbook,
) -> None:
    # Business rule: a signature must carry a non-empty name.
    if not command.visitor_name.strip():
        raise ValueError("visitor_name must not be empty")

    # Stamp identity + time here, in the procedure — events are immutable facts,
    # so everything needed to replay them must be baked in at emit time.
    context.emit.guestbook_signed(
        GuestbookSigned(
            signature_id=str(uuid4()),
            visitor_name=command.visitor_name.strip(),
            message=command.message.strip(),
            signed_at=datetime.now(timezone.utc),
        )
    )
