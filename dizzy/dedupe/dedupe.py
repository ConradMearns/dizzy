

from datetime import datetime
from pathlib import Path

from dizzy.command_queue import CommandQueueSystem

from dizzy.dedupe.events import ImageScanned, ItemDiscovered, ItemScanned
from dizzy.dedupe.listeners import Print, HashItem, ItemIsImage, ItemIsZIP

from dizzy.dedupe.instrument_prov import instrumentation

# TODO definitely broken...
# system = CommandQueueSystem(instrumentation=instrumentation)
# instrumentation.subscribe(CommandQueueSystem.ActivityStarted, Print())

system = CommandQueueSystem()

# system.register(ItemDiscovered)
# system.register(ItemScanned)

system.subscribe(ItemDiscovered, HashItem())
system.subscribe(ItemDiscovered, ItemIsImage())
system.subscribe(ItemDiscovered, ItemIsZIP())

for event_type in system.listeners:
    system.subscribe(event_type, Print())

system.subscribe(ImageScanned, Print())



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
app()
