"""lib_runner — runs ONE real generated handler inside the lib's own uv env and
POSTs its emissions to the executor's HTTP sink.

This is the language-specific half of try_lib_executor, kept behind the subprocess
boundary: it is launched as `uv run --project <lib> python lib_runner.py <spec.json>`
so it sees the generated gen_def/gen_int/handler packages. It imports only the stdlib
plus those packages (urllib for the POST), so the lib env needs no extra deps.

The spec (one JSON arg) is computed by the parent from the feat:
  {signature: procedure|policy, out_kind: emit|dispatch,
   handler_module, handler_func,
   context_module, context_class, emitters_class,
   input_module, input_class, payload, sink_url}

Wiring mirrors the generated demo: build a context whose emit.<name> callbacks are
ours (they POST), construct the typed command/event from `payload`, call the handler
(procedure(context, command) | policy(event, context)).
"""

import dataclasses
import importlib
import json
import sys
import urllib.request


def post(url: str, body: dict) -> None:
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}
    )
    urllib.request.urlopen(req, timeout=10).read()


def main(spec: dict) -> int:
    sink = spec["sink_url"]
    out_kind = spec["out_kind"]  # "emit" (events) | "dispatch" (commands)

    ctx_mod = importlib.import_module(spec["context_module"])
    context_class = getattr(ctx_mod, spec["context_class"])
    emitters_class = getattr(ctx_mod, spec["emitters_class"])

    # One callback per emitter field; the field name IS the emitted event/command name.
    # The handler hands us a typed pydantic payload — we serialize and POST it.
    def make_cb(name: str):
        def cb(payload) -> None:
            post(sink, {"name": name, "kind": out_kind, "data": payload.model_dump(mode="json")})
        return cb

    fields = [f.name for f in dataclasses.fields(emitters_class)]
    emitters = emitters_class(**{name: make_cb(name) for name in fields})
    context = context_class(emit=emitters)

    input_class = getattr(importlib.import_module(spec["input_module"]), spec["input_class"])
    trigger = input_class(**spec["payload"])

    handler = getattr(importlib.import_module(spec["handler_module"]), spec["handler_func"])

    try:
        if spec["signature"] == "procedure":
            handler(context, trigger)  # procedure(context, command)
        else:
            handler(trigger, context)  # policy(event, context)
    except Exception as exc:  # a real handler raising == a finding, not a crash
        post(sink, {"finding": True, "error": f"{type(exc).__name__}: {exc}"})
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(json.loads(sys.argv[1])))
