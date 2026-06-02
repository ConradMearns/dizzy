# AUTO-GENERATED — do not edit
from typing import Protocol

from gen_def.pydantic.commands import SignGuestbook
from gen_int.python.procedure.record_signature_context import (
    record_signature_context,
)


class record_signature_protocol(Protocol):
    """Validate the signature and record it as a fact"""

    def __call__(
        self,
        context: record_signature_context,
        command: SignGuestbook,
    ) -> None:
        ...
