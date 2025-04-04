

from datetime import datetime
from pathlib import Path

from dizzy.command_queue import CommandQueueSystem

from dizzy.dedupe.events import ImageScanned, ItemDiscovered, ItemHashed, TagAdded
from dizzy.dedupe.listeners import (
    Print, HashItem, ItemIsImage, ItemIsZIP, 
    StoreItemSize, StoreToCAS, ExtractMetadata
)

from dizzy.dedupe.instrument_prov import instrumentation

system = CommandQueueSystem(instrumentation=instrumentation)

# Initial discovery and type detection
system.subscribe(ItemDiscovered, ItemIsZIP())  #> ItemDiscovered
system.subscribe(ItemDiscovered, ItemIsImage()) #> ImageScanned

# Process images
system.subscribe(ImageScanned, HashItem())      #> ItemHashed

# Process hashed items
system.subscribe(ItemHashed, StoreToCAS())      # Store in CAS
system.subscribe(ItemHashed, StoreItemSize())   # Get size as tag
system.subscribe(ItemHashed, ExtractMetadata()) # Extract EXIF as tags

# Debug output

system.subscribe(ImageScanned, Print())
system.subscribe(ItemHashed, Print())
system.subscribe(TagAdded, Print())


def run():
    while system.queue.has_items():
        system.run_next()


import typer

app = typer.Typer()

@app.command()
def scan(path: Path):
    path = str(path.absolute()) 
    event = ItemDiscovered(datetime.now().isoformat(), path)
    system.queue.emit(event)
    run()

if __name__ == "__main__":
    app()

# for item discovered
# if item is an image... extract metadata
# if item is a zip...

# first pass
# - collect information about each file, EXIF, meta, date, paths
# - what hard drive / datasource?
# - file size (good opportunity to try a migration)
# - file type
# - dealing with zips...

# saving data to CSV / parquet should be parallelizable and faster

# always at end
# app()


# scan(Path("dizzy/dedupe/test_data/multiple.zip"))
# scan(Path("dizzy/dedupe/test_data/zipped.zip"))

# phase 1
# - identify what we're dealing with
# how much storage are duplicates taking up?
