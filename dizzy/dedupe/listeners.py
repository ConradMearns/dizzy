from dizzy.command_queue import CommandQueue, Event, Listener
from dizzy.dedupe.events import ImageScanned, ItemDiscovered, ItemScanned

from datetime import datetime
import hashlib
import fsspec
import magic
import zipfile

class HashItem(Listener):
    def run(self, queue: CommandQueue, event: ItemDiscovered):
        with fsspec.open(event.path, "rb") as f:
            digest = hashlib.file_digest(f, "blake2s")
        queue.emit(ItemScanned(event.path, digest.hexdigest() ))

class ItemIsImage(Listener):
    def run(self, queue: CommandQueue, event: ItemDiscovered):
        mime = magic.from_file(event.path, mime=True)
        is_image = mime.startswith("image/")

        if not is_image:
            return
        
        queue.emit(ImageScanned( event.path ))


class ItemIsZIP(Listener):
    def run(self, queue: CommandQueue, event: ItemDiscovered):
        mime = magic.from_file(event.path, mime=True)
        is_zip = mime == "application/zip"

        if not is_zip:
            return

        with zipfile.ZipFile(event.path, 'r') as zipf:
            files =  [info.filename for info in zipf.infolist() if not info.is_dir()]
        print(files)

        for file in files:
            zippath =  f"zip://{event.path}::{file}"
            queue.emit(ItemDiscovered(timestamp=datetime.now().isoformat(), path=zippath))


class Print(Listener):
    def run(self, queue: CommandQueue, event: Event):
        from rich import print
        print(event)
