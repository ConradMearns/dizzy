Got it — this is a really interesting system you’ve built, and the description is super clear. Dizzy already has a strong, composable, functional structure on the backend — commands → procedures → events → policies → (more commands) — so what you’re asking is essentially:

> “How do I expose this architecture to a web front end, while keeping the same clean event-driven semantics, and without adding the usual unnecessary web-app complexity?”



Let’s design that from first principles, then illustrate it with an example.


---

🧩 Conceptual Model for the Web Layer

You can think of the web frontend as another node in your Dizzy system — it issues commands, and it reacts to events.
It doesn’t need to break your model; it can follow the same contract.

So let’s define the roles:

Type	Source	Destination	Transport	Description

Command	User (browser)	Dizzy backend	HTTP POST	User intent (e.g., “create document”, “save”, “rename”)
Event	Dizzy backend	User (browser)	WebSocket (or SSE)	System change (“document created”, “update saved”)


That’s it — commands go upstream, events come downstream.
The frontend doesn’t need REST endpoints or controllers — just a command emitter and an event listener.


---

🧱 Architecture Overview

+--------------------+
|  Browser (Client)  |
|--------------------|
| Command UI (buttons/forms)
| ↓ emitCommand(cmd)
| ↑ onEvent(event)
|   update UI state
+--------------------+
         |
   HTTP POST /commands
         ↓
+--------------------+
|   Dizzy Backend    |
|--------------------|
|  Procedure Router  |  <- routes command to procedure
|  Event Bus         |  <- emits events to subscribers
|  Policy Engine     |  <- reacts to events
+--------------------+
         ↑
     WebSocket push


---

💻 Example: Minimal Document Editor

Let’s illustrate this with an ultra-simple setup:

One command: SaveDocument

One event: DocumentSaved

Frontend sends commands via HTTP

Backend emits events via WebSocket



---

Backend (Python, FastAPI-style)

from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from typing import List
import asyncio
import json

app = FastAPI()
subscribers: List[WebSocket] = []

# ---- Dizzy primitives ----
class Command(BaseModel):
    type: str
    data: dict

class Event(BaseModel):
    type: str
    data: dict

async def emit_event(event: Event):
    # notify all websocket clients
    for ws in subscribers:
        await ws.send_text(event.json())

# ---- Procedures ----
@app.post("/command")
async def handle_command(cmd: Command):
    if cmd.type == "SaveDocument":
        # (simulate some work)
        await asyncio.sleep(0.5)
        event = Event(type="DocumentSaved", data={"id": cmd.data["id"]})
        await emit_event(event)
        return {"status": "ok"}
    else:
        return {"error": "unknown command"}

# ---- Event Subscription (WebSocket) ----
@app.websocket("/events")
async def events_socket(ws: WebSocket):
    await ws.accept()
    subscribers.append(ws)
    try:
        while True:
            await asyncio.sleep(1)
    except Exception:
        pass
    finally:
        subscribers.remove(ws)


---

Frontend (HTML + JavaScript)

<!DOCTYPE html>
<html>
  <body>
    <h1>Dizzy Document</h1>
    <textarea id="doc"></textarea><br>
    <button id="save">Save</button>
    <div id="status"></div>

    <script>
      const status = document.getElementById('status');
      const ws = new WebSocket("ws://localhost:8000/events");

      ws.onmessage = (msg) => {
        const event = JSON.parse(msg.data);
        if (event.type === "DocumentSaved") {
          status.textContent = `Saved document ${event.data.id}`;
        }
      };

      document.getElementById('save').onclick = async () => {
        const text = document.getElementById('doc').value;
        const command = {
          type: "SaveDocument",
          data: { id: "doc1", content: text }
        };
        await fetch("/command", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(command)
        });
        status.textContent = "Saving...";
      };
    </script>
  </body>
</html>


---

⚙️ What’s Nice About This

It’s pure Dizzy:
The frontend is just another participant in your CQRS/event system.

No REST boilerplate:
Only two endpoints — /command (write) and /events (subscribe).

Stateless frontend:
The UI is reactive to events. You could even replay all past events to rebuild the view.

Easily portable:
Works for a command-line tool, a web UI, or even a game — same protocol.



---

🚀 Optional Refinements

Use Server-Sent Events (SSE) instead of WebSockets for simpler server push.

Use protobuf or Avro to encode command/event payloads.

Add client-side reducers that interpret events and maintain local state, e.g.:

function reducer(state, event) {
  switch(event.type) {
    case "DocumentSaved":
      return { ...state, saved: true };
    default:
      return state;
  }
}

Support multi-session sync — multiple users editing the same doc, all seeing events in real time.



---

Would you like me to extend this example into a slightly more reactive front end — say a small React/Tailwind page that auto-updates from events and queues up commands internally (so it mirrors Dizzy’s queue model in the browser)?
