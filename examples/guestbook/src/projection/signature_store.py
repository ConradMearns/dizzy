# Implementation — fold each GuestbookSigned event into the read model.
from gen_int.python.projection.signature_store_projection import signature_store_context
from gen_def.pydantic.events import GuestbookSigned
from gen_def.sqla.models.guestbook import Signature


def signature_store(
    event: GuestbookSigned,
    context: signature_store_context,
) -> None:
    # context.adapter is a SqlaAdapter — it hands us a live SQLAlchemy session.
    context.adapter.session.merge(
        Signature(
            id=event.signature_id,
            visitor_name=event.visitor_name,
            message=event.message,
            signed_at=event.signed_at,
        )
    )
    context.adapter.session.commit()
