# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.events import GuestbookSigned
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class signature_store_context:
    adapter: SqlaAdapter


class signature_store_projection(Protocol):
    """Persist each signature into the guestbook model"""

    def __call__(self, event: GuestbookSigned, context: signature_store_context) -> None:
        """Apply the projection — mutate model state in response to the event."""
        ...
