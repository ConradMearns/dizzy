# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Callable

from gen_def.pydantic.events import GuestbookSigned


@dataclass
class record_signature_emitters:
    guestbook_signed: Callable[[GuestbookSigned], None]


@dataclass
class record_signature_context:
    emit: record_signature_emitters
