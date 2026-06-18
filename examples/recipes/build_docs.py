# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml", "typst"]
# ///
"""Generate a cross-linked, colour-coded Typst reference from recipes.feat.yaml.

The feature-file is the single source of truth; this script turns it into a
human-readable reference: every command, event, procedure, policy, projection,
model, and query becomes a labelled section whose text is its description, and
the wiring becomes hyperlinks (a procedure links to the command it handles and
the events it emits; a command links back to the procedures that consume it and
the policies that dispatch it; and so on).

Each element gets a short DIZZY-style label — c/d/e/y/j/m/q + a number — shown as
a coloured badge (the palette + per-component arrow maps are lifted from
docs/whitepaper.typ), so the labels carry through into the table of contents.

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
# Per-component arrow map (from docs/figures.typ) shown at the top of each section.
MAP = {
    "command": "c_map", "procedure": "d_map", "event": "e_map", "policy": "y_map",
    "projection": "j_map", "model": "m_map", "query": "q_map",
}
SUBTITLE = {
    "command": "write intents", "event": "immutable facts",
    "procedure": "command handlers", "policy": "event reactions",
    "projection": "read-model builders", "model": "read-side schemas",
    "query": "read interfaces",
}
PLURAL = {
    "command": "Commands", "event": "Events", "procedure": "Procedures",
    "policy": "Policies", "projection": "Projections", "model": "Models",
    "query": "Queries",
}

# The colourful-blocks palette, lifted from the es() helper in docs/whitepaper.typ
# (m has no es colour there, so it gets a neutral slate).
PALETTE = """#let palette = (
  c: rgb("#4ab6d9"), e: rgb("#abcc51"), d: rgb("#f39a4f"), y: rgb("#eb6092"),
  j: rgb("#f5d341"), m: rgb("#6b8aa5"), q: rgb("#c2a1c7"),
)
#let badge(code, kind) = box(
  fill: palette.at(kind), inset: (x: 6pt, y: 3pt), radius: 3pt, outset: (y: 1pt),
  text(fill: luma(15), weight: "bold", size: 10pt, code),
)
#let chip(code, kind) = box(
  fill: palette.at(kind), inset: (x: 3.5pt, y: 1pt), radius: 2.5pt, outset: (y: 1pt),
  text(fill: luma(15), weight: "bold", size: 8pt, code),
)
#let eref(dest, code, kind, name) = link(dest)[#chip(code, kind) #raw(name)]
#let head(code, kind, name) = [#badge(code, kind) #h(0.5em) #raw(name)]
"""

# Per-component arrow maps, copied from docs/figures.typ (Q_map renamed q_map).
MAPS = """#let c_map = diagram(spacing: (1em, 3em),
  node((1,0), $y$, name: <y>), node((1,1), $c$, name: <c>), node((1,2), $d$, name: <d>),
  edge(<y>, <c>, label: "emits", bend: 0deg, "->"),
  edge(<c>, <d>, label: "triggers", bend: 0deg, "->"))

#let e_map = diagram(spacing: (1em, 3em),
  node((1,0), $d$, name: <d>), node((1,1), $e$, name: <e>),
  node((0,2), $y$, name: <y>), node((2,2), $j$, name: <j>),
  edge(<d>, <e>, label: "emits", bend: 0deg, "->"),
  edge(<e>, <y>, label: "triggers", bend: 0deg, "->"),
  edge(<e>, <j>, label: "triggers", bend: 0deg, "->"))

#let d_map = diagram(spacing: (1em, 3em),
  node((0,0), $c$, name: <c>), node((2,0), $q$, name: <q>),
  node((1,1), $d$, name: <d>), node((1,2), $e$, name: <e>),
  edge(<c>, <d>, label: "triggers", label-side: right, bend: 0deg, "->"),
  edge(<q>, <d>, label: "uses", label-side: left, bend: 0deg, "<-->"),
  edge(<d>, <e>, label: "emits", label-side: left, bend: 0deg, "->"))

#let y_map = diagram(spacing: (1em, 3em),
  node((0,0), $e$, name: <e>), node((2,0), $q$, name: <q>),
  node((1,1), $y$, name: <y>), node((1,2), $c$, name: <c>),
  edge(<e>, <y>, label: "triggers", label-side: right, bend: 0deg, "->"),
  edge(<q>, <y>, label: "uses", label-side: left, bend: 0deg, "<-->"),
  edge(<y>, <c>, label: "emits", label-side: left, bend: 0deg, "->"))

#let j_map = diagram(spacing: (1em, 3em),
  node((1,0), $e$, name: <e>), node((1,1), $j$, name: <j>), node((1,2), $m$, name: <m>),
  edge(<e>, <j>, label: "triggers", bend: 0deg, "->"),
  edge(<j>, <m>, label: "maps to", bend: 0deg, "->"))

#let m_map = diagram(spacing: (1em, 3em),
  node((1,0), $j$, name: <j>), node((1,1), $m$, name: <m>), node((1,2), $Q$, name: <Q>),
  edge(<j>, <m>, label: "maps to", bend: 0deg, "->"),
  edge(<m>, <Q>, label: "serves", bend: 0deg, "<-->"))

#let q_map = diagram(spacing: (1em, 3em),
  node((1,0), $m$, name: <m>), node((1,1), $Q$, name: <Q>), node((1,2), $q$, name: <q>),
  node((0,3), $d$, name: <d>), node((2,3), $y$, name: <y>),
  edge(<m>, <Q>, label: "serves", bend: 0deg, "<-->"),
  edge(<Q>, <q>, label: "call / response", bend: 0deg, "<-->"),
  edge(<q>, <d>, label: "uses", bend: 0deg, "<-->"),
  edge(<q>, <y>, label: "uses", bend: 0deg, "<-->"))
"""


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
        """A hyperlink chip to another element, shown as a coloured `c1 name`."""
        if name not in code.get(kind, {}):
            return f"#raw(\"{name}\")"  # referenced but not declared
        return f"#eref(<{PREFIX[kind]}-{name}>, \"{code[kind][name]}\", \"{LETTER[kind]}\", \"{name}\")"

    def refs(kind: str, names) -> str:
        rendered = [ref(kind, n) for n in listify(names)]
        return " ".join(rendered) if rendered else "—"

    # --- Cross-reference indexes (derived, so links go both ways) ---
    procs = dict(sections["procedure"])
    pols = dict(sections["policy"])
    projs = dict(sections["projection"])
    qrys = dict(sections["query"])

    procs_handling = lambda cmd: [n for n, i in procs.items() if i.get("command") == cmd]
    policies_dispatching = lambda cmd: [n for n, i in pols.items() if cmd in listify(i.get("emits"))]
    procs_emitting = lambda evt: [n for n, i in procs.items() if evt in listify(i.get("emits"))]
    policies_reacting = lambda evt: [n for n, i in pols.items() if i.get("event") == evt]
    projections_folding = lambda evt: [n for n, i in projs.items() if i.get("event") == evt]
    projections_into = lambda model: [n for n, i in projs.items() if i.get("model") == model]
    queries_reading = lambda model: [n for n, i in qrys.items() if i.get("model") == model]

    def consumers_of_query(q):
        a = [("procedure", n) for n, i in procs.items() if q in listify(i.get("queries"))]
        b = [("policy", n) for n, i in pols.items() if q in listify(i.get("queries"))]
        return a + b

    # --- Emit the Typst document ---
    out: list[str] = []
    w = out.append

    w('#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge')
    w('#set document(title: "Recipe kitchen — feature reference")')
    w('#set page(numbering: "1", margin: 2.2cm)')
    w("#set text(size: 10pt)")
    w("#set par(justify: true)")
    w("#set heading(numbering: none)")
    w('#show link: set text(fill: rgb("#2b6cb0"))')
    w(PALETTE)
    w(MAPS)
    w('#align(center)[#text(20pt, weight: "bold")[Recipe kitchen]]')
    w('#align(center)[#text(9pt, fill: gray)[feature reference — '
      "generated from #raw(\"recipes.feat.yaml\") by #raw(\"build_docs.py\")]]")
    w("")
    # Legend: the colourful blocks, one per component kind.
    legend = "  #h(1em) ".join(
        f'#badge("{LETTER[k]}", "{LETTER[k]}") {k.capitalize()}' for k in sections
    )
    w(f"#align(center)[{legend}]")
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
        w(f'== #head("{code[kind][name]}", "{LETTER[kind]}", "{name}") '
          f"<{PREFIX[kind]}-{name}>")

    def section_header(kind: str) -> None:
        w(f'= #badge("{LETTER[kind]}", "{LETTER[kind]}") #h(0.4em) {PLURAL[kind]} '
          f'#text(11pt, fill: gray)[— {SUBTITLE[kind]}]')
        w(f"#align(center)[#pad(y: 0.6em, {MAP[kind]})]")
        w("")

    def describe(info: dict) -> None:
        if info.get("description"):
            w(paragraphs(info["description"]))
        w("")

    # Commands ----------------------------------------------------------------
    section_header("command")
    for name, info in sections["command"]:
        item_heading("command", name)
        describe(info)
        meta("Handled by", refs("procedure", procs_handling(name)))
        meta("Dispatched by", refs("policy", policies_dispatching(name)))
        w("")

    # Events ------------------------------------------------------------------
    section_header("event")
    for name, info in sections["event"]:
        item_heading("event", name)
        describe(info)
        meta("Emitted by", refs("procedure", procs_emitting(name)))
        meta("Reacted to by", refs("policy", policies_reacting(name)))
        meta("Folded by", refs("projection", projections_folding(name)))
        w("")

    # Procedures --------------------------------------------------------------
    section_header("procedure")
    for name, info in sections["procedure"]:
        item_heading("procedure", name)
        describe(info)
        meta("Handles", refs("command", info.get("command")))
        meta("Emits", refs("event", info.get("emits")))
        meta("Queries", refs("query", info.get("queries")))
        w("")

    # Policies ----------------------------------------------------------------
    section_header("policy")
    for name, info in sections["policy"]:
        item_heading("policy", name)
        describe(info)
        meta("On event", refs("event", info.get("event")))
        meta("Dispatches", refs("command", info.get("emits")))
        meta("Queries", refs("query", info.get("queries")))
        w("")

    # Projections -------------------------------------------------------------
    section_header("projection")
    for name, info in sections["projection"]:
        item_heading("projection", name)
        describe(info)
        meta("On event", refs("event", info.get("event")))
        meta("Into model", refs("model", info.get("model")))
        w("")

    # Models ------------------------------------------------------------------
    section_header("model")
    for name, info in sections["model"]:
        item_heading("model", name)
        describe(info)
        adapters = " ".join(f"#raw(\"{a}\")" for a in listify(info.get("adapters"))) or "—"
        meta("Adapters", adapters)
        meta("Written by", refs("projection", projections_into(name)))
        meta("Read by", refs("query", queries_reading(name)))
        w("")

    # Queries -----------------------------------------------------------------
    section_header("query")
    for name, info in sections["query"]:
        item_heading("query", name)
        describe(info)
        meta("Reads model", refs("model", info.get("model")))
        used = consumers_of_query(name)
        meta("Used by", " ".join(ref(k, n) for k, n in used) if used else "—")
        w("")

    TYP.write_text("\n".join(out) + "\n")
    counts = ", ".join(f"{len(v)} {PLURAL[k].lower()}" for k, v in sections.items())
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
