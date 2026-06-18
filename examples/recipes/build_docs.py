# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml", "typst"]
# ///
"""Generate a cross-linked Typst reference document from recipes.feat.yaml.

The feature-file is the single source of truth; this script turns it into a
human-readable reference: every command, event, procedure, policy, projection,
model, and query becomes a labelled section whose text is its description, and
the wiring becomes hyperlinks (a procedure links to the command it handles and
the events it emits; a command links back to the procedures that consume it and
the policies that dispatch it; and so on).

Each element gets a short DIZZY-style label — c/d/e/y/j/m/q + a number — which
shows up in the table of contents (c1, e3, d6, y1, …).

Run it (uv installs the inline deps automatically):

    uv run examples/recipes/build_docs.py

Writes recipes.typ next to the feature-file, and recipes.pdf if Typst compiles.
"""

import pathlib
import sys

import yaml

HERE = pathlib.Path(__file__).parent
FEAT = HERE / "recipes.feat.yaml"
TYP = HERE / "recipes.typ"
PDF = HERE / "recipes.pdf"

# DIZZY component symbols (see `dizzy onboard`): the ToC label letter per kind,
# and a unique prefix for the Typst cross-reference label of each element.
LETTER = {
    "command": "c", "procedure": "d", "event": "e", "policy": "y",
    "projection": "j", "model": "m", "query": "q",
}
PREFIX = {
    "command": "cmd", "procedure": "proc", "event": "evt", "policy": "pol",
    "projection": "proj", "model": "model", "query": "qry",
}


def normalize(section: dict | None) -> list[tuple[str, dict]]:
    """A feature-file section maps name -> (shorthand string | mapping). Return an
    ordered list of (name, info-dict), expanding the `name: description` shorthand."""
    items: list[tuple[str, dict]] = []
    for name, value in (section or {}).items():
        if isinstance(value, str):
            items.append((name, {"description": value}))
        else:
            items.append((name, value or {}))
    return items


def listify(value) -> list[str]:
    """Coerce a field that may be a single string or a list into a list."""
    if value is None:
        return []
    return [value] if isinstance(value, str) else list(value)


def esc(text: str) -> str:
    """Escape Typst markup so descriptions render as literal prose."""
    text = text.replace("\\", "\\\\")
    for ch in "#$*_`<>@":
        text = text.replace(ch, "\\" + ch)
    return text.strip()


def paragraphs(text: str) -> str:
    """Render a (possibly multi-paragraph) description as escaped Typst paragraphs."""
    blocks = [b.strip() for b in (text or "").split("\n\n") if b.strip()]
    return "\n\n".join(esc(" ".join(b.split())) for b in blocks)


def main() -> int:
    feat = yaml.safe_load(FEAT.read_text())

    sections = {
        "command": normalize(feat.get("commands")),
        "event": normalize(feat.get("events")),
        "procedure": normalize(feat.get("procedures")),
        "policy": normalize(feat.get("policies")),
        "projection": normalize(feat.get("projections")),
        "model": normalize(feat.get("models")),
        "query": normalize(feat.get("queries")),
    }

    # name -> "c1" style code, per kind, in file order.
    code: dict[str, dict[str, str]] = {}
    for kind, items in sections.items():
        code[kind] = {name: f"{LETTER[kind]}{i}" for i, (name, _) in enumerate(items, 1)}

    def ref(kind: str, name: str) -> str:
        """A hyperlink to another element, shown as `c1 name`."""
        if name not in code.get(kind, {}):
            return f"`{name}`"  # referenced but not declared — render plainly
        return f"#link(<{PREFIX[kind]}-{name}>)[{code[kind][name]} `{name}`]"

    def refs(kind: str, names) -> str:
        rendered = [ref(kind, n) for n in listify(names)]
        return ", ".join(rendered) if rendered else "—"

    # --- Cross-reference indexes (derived, so links go both ways) ---
    procs = dict(sections["procedure"])
    pols = dict(sections["policy"])
    projs = dict(sections["projection"])
    qrys = dict(sections["query"])

    def procs_handling(cmd):
        return [n for n, i in procs.items() if i.get("command") == cmd]

    def policies_dispatching(cmd):
        return [n for n, i in pols.items() if cmd in listify(i.get("emits"))]

    def procs_emitting(evt):
        return [n for n, i in procs.items() if evt in listify(i.get("emits"))]

    def policies_reacting(evt):
        return [n for n, i in pols.items() if i.get("event") == evt]

    def projections_folding(evt):
        return [n for n, i in projs.items() if i.get("event") == evt]

    def consumers_of_query(q):
        a = [("procedure", n) for n, i in procs.items() if q in listify(i.get("queries"))]
        b = [("policy", n) for n, i in pols.items() if q in listify(i.get("queries"))]
        return a + b

    def projections_into(model):
        return [n for n, i in projs.items() if i.get("model") == model]

    def queries_reading(model):
        return [n for n, i in qrys.items() if i.get("model") == model]

    # --- Emit the Typst document ---
    out: list[str] = []
    w = out.append

    w('#set document(title: "Recipe kitchen — feature reference")')
    w('#set page(numbering: "1", margin: 2.2cm)')
    w("#set text(size: 10pt)")
    w("#set par(justify: true)")
    w("#set heading(numbering: none)")
    w('#show link: set text(fill: rgb("#2b6cb0"))')
    w("")
    w('#align(center)[#text(20pt, weight: "bold")[Recipe kitchen]]')
    w('#align(center)[#text(9pt, fill: gray)[feature reference — '
      "generated from #raw(\"recipes.feat.yaml\") by #raw(\"build_docs.py\")]]")
    w("")
    if feat.get("description"):
        w(paragraphs(feat["description"]))
        w("")
    w("#outline(title: [Contents], depth: 2, indent: auto)")
    w("#pagebreak()")
    w("")

    def meta(label: str, body: str) -> None:
        if body and body != "—":
            w(f"#text(9pt)[*{label}* {body}] \\")

    def item_heading(kind: str, name: str) -> None:
        w(f"== {code[kind][name]} · `{name}` <{PREFIX[kind]}-{name}>")

    # Commands ----------------------------------------------------------------
    w("= Commands #h(0.4em) #text(11pt, fill: gray)[— write intents]")
    w("")
    for name, info in sections["command"]:
        item_heading("command", name)
        if info.get("description"):
            w(paragraphs(info["description"]))
        w("")
        meta("Handled by", refs("procedure", procs_handling(name)))
        meta("Dispatched by", refs("policy", policies_dispatching(name)))
        w("")

    # Events ------------------------------------------------------------------
    w("= Events #h(0.4em) #text(11pt, fill: gray)[— immutable facts]")
    w("")
    for name, info in sections["event"]:
        item_heading("event", name)
        if info.get("description"):
            w(paragraphs(info["description"]))
        w("")
        meta("Emitted by", refs("procedure", procs_emitting(name)))
        meta("Reacted to by", refs("policy", policies_reacting(name)))
        meta("Folded by", refs("projection", projections_folding(name)))
        w("")

    # Procedures --------------------------------------------------------------
    w("= Procedures #h(0.4em) #text(11pt, fill: gray)[— command handlers]")
    w("")
    for name, info in sections["procedure"]:
        item_heading("procedure", name)
        if info.get("description"):
            w(paragraphs(info["description"]))
        w("")
        meta("Handles", refs("command", info.get("command")))
        meta("Emits", refs("event", info.get("emits")))
        meta("Queries", refs("query", info.get("queries")))
        w("")

    # Policies ----------------------------------------------------------------
    w("= Policies #h(0.4em) #text(11pt, fill: gray)[— event reactions]")
    w("")
    for name, info in sections["policy"]:
        item_heading("policy", name)
        if info.get("description"):
            w(paragraphs(info["description"]))
        w("")
        meta("On event", refs("event", info.get("event")))
        meta("Dispatches", refs("command", info.get("emits")))
        meta("Queries", refs("query", info.get("queries")))
        w("")

    # Projections -------------------------------------------------------------
    w("= Projections #h(0.4em) #text(11pt, fill: gray)[— read-model builders]")
    w("")
    for name, info in sections["projection"]:
        item_heading("projection", name)
        if info.get("description"):
            w(paragraphs(info["description"]))
        w("")
        meta("On event", refs("event", info.get("event")))
        meta("Into model", refs("model", info.get("model")))
        w("")

    # Models ------------------------------------------------------------------
    w("= Models #h(0.4em) #text(11pt, fill: gray)[— read-side schemas]")
    w("")
    for name, info in sections["model"]:
        item_heading("model", name)
        if info.get("description"):
            w(paragraphs(info["description"]))
        w("")
        adapters = ", ".join(f"`{a}`" for a in listify(info.get("adapters"))) or "—"
        meta("Adapters", adapters)
        meta("Written by", refs("projection", projections_into(name)))
        meta("Read by", refs("query", queries_reading(name)))
        w("")

    # Queries -----------------------------------------------------------------
    w("= Queries #h(0.4em) #text(11pt, fill: gray)[— read interfaces]")
    w("")
    for name, info in sections["query"]:
        item_heading("query", name)
        if info.get("description"):
            w(paragraphs(info["description"]))
        w("")
        meta("Reads model", refs("model", info.get("model")))
        used = consumers_of_query(name)
        meta("Used by", ", ".join(ref(k, n) for k, n in used) if used else "—")
        w("")

    TYP.write_text("\n".join(out) + "\n")
    counts = ", ".join(f"{len(v)} {k}s" for k, v in sections.items())
    print(f"wrote {TYP.relative_to(HERE.parent.parent)}  ({counts})")

    # Compile to PDF if we can.
    try:
        import typst

        typst.compile(str(TYP), output=str(PDF))
        print(f"wrote {PDF.relative_to(HERE.parent.parent)}")
    except Exception as exc:  # noqa: BLE001 — report and keep the .typ
        print(f"(skipped PDF: {exc})", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
