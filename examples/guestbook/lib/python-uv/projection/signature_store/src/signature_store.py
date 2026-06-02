# Implementation stub — fill in your logic here
from gen_int.python.projection.signature_store_projection import signature_store_projection
from gen_int.python.projection.signature_store_projection import signature_store_context
from gen_def.pydantic.events import GuestbookSigned


def signature_store(
    event: GuestbookSigned,
    context: signature_store_context,
) -> None:
    raise NotImplementedError
