from dizzy.command_queue import CommandQueue, Event, Listener
from dizzy.dedupe.events import ImageScanned, ItemDiscovered, ItemHashed, TagAdded

from datetime import datetime
import hashlib
import fsspec
import magic
import zipfile
import os
from pathlib import Path
from PIL import Image
import shutil

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


class StoreToCAS(Listener):
    def run(self, queue: CommandQueue, event: ItemHashed):
        cas_dir = Path("CAS")
        cas_dir.mkdir(exist_ok=True)
        
        dest_path = cas_dir / event.blake2s_digest
        if not dest_path.exists():
            with fsspec.open(event.path, "rb") as src:
                with open(dest_path, "wb") as dst:
                    shutil.copyfileobj(src, dst)


class ExtractMetadata(Listener):
    def run(self, queue: CommandQueue, event: ItemHashed):
        with fsspec.open(event.path, "rb") as img_buf:

            with Image.open(img_buf) as img:
                # Get creation date from EXIF
                exif = img._getexif()
                if exif:
                    # DateTimeOriginal (36867) or DateTime (306)
                    date_taken = exif.get(36867) or exif.get(306)
                    if date_taken:
                        queue.emit(TagAdded(
                            hash=event.blake2s_digest,
                            key="creation_date",
                            value=date_taken
                        ))
                    
                    # Camera make (271) and model (272)
                    make = exif.get(271)
                    if make:
                        queue.emit(TagAdded(
                            hash=event.blake2s_digest,
                            key="camera_make",
                            value=make
                        ))
                    
                    model = exif.get(272)
                    if model:
                        queue.emit(TagAdded(
                            hash=event.blake2s_digest,
                            key="camera_model",
                            value=model
                        ))


class StoreItemSize(Listener):
    def run(self, queue: CommandQueue, event: ItemHashed):
        with fsspec.open(event.path, "rb") as f:
            size = len(f.read())
            queue.emit(TagAdded(
                hash=event.blake2s_digest,
                key="file_size",
                value=str(size)
            ))


class Print(Listener):
    def run(self, queue: CommandQueue, event: Event):
        from rich import print
        print(event)
