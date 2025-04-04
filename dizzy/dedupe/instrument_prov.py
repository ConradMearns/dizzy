import duckdb

import dizzy.command_handler as ch

from dizzy.command_queue import CommandQueueSystem


conn = duckdb.connect("prov.duckdb")
# conn = duckdb.connect(":memory:")
instrumentation = CommandQueueSystem()
instrumentation.subscribe(CommandQueueSystem.ActivityStarted, ch.HandleActivityStarted(conn))
instrumentation.subscribe(CommandQueueSystem.ActivityEnded, ch.HandleActivityEnded(conn))
instrumentation.subscribe(CommandQueueSystem.EntityHasJSON, ch.HandleEntityHasJSON(conn))
instrumentation.subscribe(CommandQueueSystem.ActivityCrashed, ch.HandleActivityCrashed(conn))
instrumentation.subscribe(CommandQueueSystem.ActivityUsedEntity, ch.HandleActivityUsedEntity(conn))
instrumentation.subscribe(CommandQueueSystem.EntityGeneratedFromActivity, ch.HandleEntityGeneratedFromActivity(conn))
instrumentation.subscribe(CommandQueueSystem.EntityDerivedFromEntity, ch.HandleEntityDerivedFromEntity(conn))
