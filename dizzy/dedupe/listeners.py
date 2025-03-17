from dizzy.command_queue import CommandQueue, Event, Listener
from dizzy.dedupe.events import ImageScanned, ItemDiscovered, ItemHashed

from datetime import datetime
import hashlib
import fsspec
import magic
import zipfile

class HashItem(Listener):
    def run(self, queue: CommandQueue, event: ItemDiscovered):
        with fsspec.open(event.path, "rb") as f:
            # buffer = f.read(2048)
            digest = hashlib.file_digest(f, "blake2s")
        queue.emit(ItemHashed(event.path, digest.hexdigest() ))

class ItemIsImage(Listener):
    def run(self, queue: CommandQueue, event: ItemDiscovered):
        with fsspec.open(event.path, "rb") as f:
            buffer = f.read(2048)
            mime = magic.from_buffer(buffer, mime=True)

        is_image = mime.startswith("image/")

        if not is_image:
            return
        
        queue.emit(ImageScanned( event.path ))


class ItemIsZIP(Listener):
    def run(self, queue: CommandQueue, event: ItemDiscovered):
        with fsspec.open(event.path, "rb") as f:
            buffer = f.read(2048)
            mime = magic.from_buffer(buffer, mime=True)

        is_zip = mime == "application/zip"

        if not is_zip:
            return

        with fsspec.open(event.path, "rb") as f:
            with zipfile.ZipFile(f, 'r') as zipf:
                files = [info.filename for info in zipf.infolist() if not info.is_dir()]

        for file in files:
            zippath = f"zip://{file}::{event.path}"
            queue.emit(ItemDiscovered(timestamp=datetime.now().isoformat(), path=zippath))


class StoreItemSize(Listener):
    def run(self, queue: CommandQueue, event: ItemHashed):
        with fsspec.open(event.path, "rb") as f:
            size = len(f.read())
            print(size)


class Print(Listener):
    def run(self, queue: CommandQueue, event: Event):
        from rich import print
        print(event)
