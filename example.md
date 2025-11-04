Perfect — this is exactly the kind of clarity that helps.

So we’re staying entirely off the web stack, meaning no HTTP, FastAPI, or REST. The goal is:

Keep the Dizzy event/command loop intact (command → procedure → event → policy).

Add a Streamlit front end that can connect to this in-process (or inter-process) loop via asyncio queues — not HTTP endpoints.

Allow a procedure (like a chat stream) to yield or emit streaming data, which the Streamlit app can progressively render.


That’s absolutely doable — and honestly, this approach is much cleaner and more “Dizzy-native.”
We’ll make the Streamlit UI act as a participant in the system — just another agent connected by queues.

Let’s build it step by step.


---

🧩 1. Core Concept

We’ll run the Dizzy loop and the Streamlit UI in the same Python process, connected via asyncio.Queue objects.

If you want them in different processes, you can later replace these queues with e.g. multiprocessing.Queue, ZeroMQ, or Redis streams — the interface will stay the same.

Communication model:

[ Streamlit UI ]
       │
       │  puts Command into →  command_queue
       │
       ▼
[ Dizzy runtime: procedure dispatcher ]
       │
       │  emits events into → event_queue
       │
       ▼
[ Streamlit UI ]
   reacts to event stream

The Streamlit app doesn’t call any functions directly; it sends a Command and listens for Events.
The Dizzy runtime sits in the middle doing the work.


---

⚙️ 2. Minimal Dizzy Runtime (Async queues)

Let’s write a simple core system — one procedure and one event emitter.
We’ll also add a streaming procedure that mimics OpenAI-like token streaming.

# dizzy_core.py
import asyncio
from dataclasses import dataclass, asdict

@dataclass
class Command:
    type: str
    data: dict

@dataclass
class Event:
    type: str
    data: dict

class DizzyRuntime:
    def __init__(self):
        self.command_queue = asyncio.Queue()
        self.event_queue = asyncio.Queue()
        self.procedures = {}

    def register_procedure(self, command_type, coro_fn):
        self.procedures[command_type] = coro_fn

    async def start(self):
        while True:
            cmd = await self.command_queue.get()
            handler = self.procedures.get(cmd.type)
            if handler:
                async for evt in handler(cmd):
                    await self.event_queue.put(evt)
            else:
                await self.event_queue.put(Event("UnknownCommand", {"type": cmd.type}))

# Example procedure: streams responses like an AI model
async def chat_stream_procedure(cmd: Command):
    user_input = cmd.data["text"]
    for token in ["Hello", ", ", "this ", "is ", "Dizzy!"]:
        await asyncio.sleep(0.3)  # simulate latency
        yield Event("ChatStreamChunk", {"text": token})
    yield Event("ChatComplete", {"text": "Done"})


---

🧠 3. Integrating with Streamlit

Streamlit runs in a synchronous environment, but we can use asyncio in the background.
We’ll use a background thread or task to run the Dizzy runtime loop.
Then Streamlit communicates through queues.

# app.py
import asyncio
import streamlit as st
from dizzy_core import DizzyRuntime, Command, chat_stream_procedure

# --- Global runtime and event loop ---
if "dizzy" not in st.session_state:
    loop = asyncio.new_event_loop()
    runtime = DizzyRuntime()
    runtime.register_procedure("ChatWithModel", chat_stream_procedure)
    st.session_state.loop = loop
    st.session_state.runtime = runtime

    async def runner():
        await runtime.start()

    import threading
    threading.Thread(target=loop.run_until_complete, args=(runner(),), daemon=True).start()

runtime = st.session_state.runtime
loop = st.session_state.loop

# --- Streamlit UI ---
st.title("Dizzy Chat")

prompt = st.chat_input("You:")
placeholder = st.empty()

async def send_and_stream(text):
    # Send command
    await runtime.command_queue.put(Command("ChatWithModel", {"text": text}))
    # Collect streamed events
    output = ""
    while True:
        event = await runtime.event_queue.get()
        if event.type == "ChatStreamChunk":
            output += event.data["text"]
            placeholder.markdown(output)
        elif event.type == "ChatComplete":
            break

if prompt:
    # Run coroutine in background
    asyncio.run_coroutine_threadsafe(send_and_stream(prompt), loop)


---

🪄 4. What’s Happening Here

Lifecycle

1. Streamlit starts → initializes DizzyRuntime once in st.session_state.


2. A background thread runs the async Dizzy loop.


3. User types a message → Streamlit sends a Command into runtime.command_queue.


4. The Dizzy runtime picks it up, finds the procedure (chat_stream_procedure).


5. The procedure yields Event objects (stream chunks) into event_queue.


6. Streamlit consumes them and updates the UI in real time.



No HTTP, no REST, no FastAPI.
Just Python objects traveling through queues.


---

🧩 5. Optional Improvements

Multiple subscribers — you can have multiple UIs, CLI tools, or background workers consuming the same event_queue.

Policies — add another loop subscribing to events and writing to a database or file.

Backpressure control — set queue sizes and timeouts to prevent memory bloat.

Persistence layer — log emitted events to a file for replay (true event sourcing).



---

✅ Summary

You now have:

A pure Dizzy runtime running asynchronously off HTTP.

A Streamlit UI that acts as a command source and event consumer.

Streaming output (token-by-token) integrated smoothly with Streamlit widgets.

Clean separation — the UI never calls logic directly, just emits/receives messages.



---

Would you like me to show a version of this where the Dizzy runtime runs as a separate process, and the Streamlit app connects to it over a lightweight message bus (like multiprocessing.Queue or ZeroMQ)?
That would let you decouple them entirely while keeping the same event/command interface.
