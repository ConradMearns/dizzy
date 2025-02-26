from pydantic.dataclasses import dataclass

from dizzy.command_queue import Event


@dataclass
class ItemDiscovered(Event):
    timestamp: str
    path: str

@dataclass
class ItemScanned(Event):
    path: str
    blake2s_digest: str

@dataclass
class ImageScanned(Event):
    path: str