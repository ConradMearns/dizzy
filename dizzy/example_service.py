
import dizzy.command_handler as ch

import duckdb

from rich.console import Console

from dizzy.command_queue import CommandQueueSystem
# from rich import print

class ExampleService:

    def __init__(self):
        
        self.console = Console()
                
        conn = duckdb.connect("prov.db")
        # conn = duckdb.connect(":memory:")
        instrumentation = CommandQueueSystem()
        instrumentation.subscribe(CommandQueueSystem.ActivityStarted, ch.HandleActivityStarted(conn))
        instrumentation.subscribe(CommandQueueSystem.ActivityEnded, ch.HandleActivityEnded(conn))
        instrumentation.subscribe(CommandQueueSystem.EntityHasJSON, ch.HandleEntityHasJSON(conn))
        instrumentation.subscribe(CommandQueueSystem.ActivityCrashed, ch.HandleActivityCrashed(conn))
        instrumentation.subscribe(CommandQueueSystem.ActivityUsedEntity, ch.HandleActivityUsedEntity(conn))
        instrumentation.subscribe(CommandQueueSystem.EntityGeneratedFromActivity, ch.HandleEntityGeneratedFromActivity(conn))
        instrumentation.subscribe(CommandQueueSystem.EntityDerivedFromEntity, ch.HandleEntityDerivedFromEntity(conn))
        
        for registration in instrumentation.registered_events.values():
            instrumentation.subscribe(registration, PrintEvent())
            # instrumentation.subscribe(registration, BuildLedger())
        
        self.cqs = CommandQueueSystem(instrumentation=instrumentation)
            
    
    def start(self):
        with self.console.status("[bold green]Running...") as status:
            while self.cqs.queue.has_items():
                # self.console.log(event)
                self.cqs.run_next()
                self.cqs.run_policies()