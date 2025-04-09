from pydantic.dataclasses import dataclass

from dizzy.command_queue import Event
from dizzy.dedupe.domain import ItemID


@dataclass
class TagAdded(Event):
    image_id: ItemID
    # hash: str      # The file's hash
    key: str       # Tag key (e.g. "creation_date", "exif_make", etc)
    value: str     # Tag value


@dataclass
class ItemDiscovered(Event):
    item_id: ItemID
    timestamp: str
    path: str
    item_id: ItemID

# @dataclass
# class ItemHashed(Event):
#     item_id: ItemID
#     path: str
#     blake2s_digest: str

@dataclass
class ImageScanned(Event):
    item_id: ItemID
    path: str
