from pydantic.dataclasses import dataclass

from dizzy.command_queue import Event


@dataclass
class TagAdded(Event):
    hash: str      # The file's hash
    key: str       # Tag key (e.g. "creation_date", "exif_make", etc)
    value: str     # Tag value


@dataclass
class ItemDiscovered(Event):
    timestamp: str
    path: str

@dataclass
class ItemHashed(Event):
    path: str
    blake2s_digest: str

@dataclass
class ImageScanned(Event):
    path: str
