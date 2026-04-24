async def core_loop(command_queue, event_store, registry):
    while True:
        command = await command_queue.get()
        procedure = registry.procedure(type(command))
        events = await procedure(command)
        for event in events:
            ok = await run_projections(event)  # writes to read model
            if ok:
                new_commands = await run_policies(event)
                for cmd in new_commands:
                    await command_queue.put(cmd)

async def query_loop(read_model_db, interval=0.5):
    while True:
        state = await read_model_db.fetch_current_state()
        render(state)  
        await asyncio.sleep(interval)

async def main():
    asyncio.create_task(core_loop(...))
    asyncio.create_task(query_loop(...))
    await asyncio.Event().wait()