# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.query.list_signatures import ListSignaturesInput, ListSignaturesOutput
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class list_signatures_context:
    adapter: SqlaAdapter


class list_signatures_query(Protocol):
    """List all guestbook signatures, newest first"""

    def __call__(
        self, input: ListSignaturesInput, context: list_signatures_context
    ) -> ListSignaturesOutput:
        ...
