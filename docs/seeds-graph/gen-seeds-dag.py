#!/usr/bin/env python3
"""Generate a self-contained, double-click-openable DAG viewer for Seeds.

Usage:
    python tools/gen-seeds-dag.py                    # -> docs/seeds-dag.html
    python tools/gen-seeds-dag.py --open             # ...and open in the browser
    python tools/gen-seeds-dag.py path/to/out.html   # custom output path

The seed data is read from `sd list --format json` and INLINED into the HTML
(file:// fetch() is blocked by browsers, so inlining is what makes the output a
single double-clickable file *and* keeps the mkdocs build free of any runtime
`sd` dependency). Layout/render is vanilla JS — no build, no deps.
"""

from __future__ import annotations

import json
import subprocess
import sys
import webbrowser
from pathlib import Path

PARENT = Path(__file__).resolve().parent
DEFAULT_OUT = PARENT / "graph.html"

def fetch_seeds() -> list[dict]:
    raw = subprocess.run(
        ["sd", "list", "--format", "json"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return json.loads(raw)["issues"]


HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Seeds DAG</title>
<style>
  :root { color-scheme: dark; }
  * { box-sizing: border-box; }
  body { margin: 0; font: 13px/1.4 ui-sans-serif, system-ui, sans-serif;
         background: #0e1116; color: #d7dde5; display: flex; height: 100vh; }
  #graph { flex: 1; overflow: auto; position: relative; }
  svg { display: block; }
  .edge { stroke: #3a4250; stroke-width: 1.2; fill: none; }
  .edge.hot { stroke: #f0a830; stroke-width: 2; }
  .node rect { rx: 5; stroke-width: 1.5; cursor: pointer; }
  .node text { pointer-events: none; fill: #e8edf3; }
  .node .id { font-weight: 700; font-size: 11px; }
  .node .title { font-size: 10px; fill: #aab4c0; }
  .node.dim { opacity: .18; }
  .node.sel rect { stroke: #fff !important; stroke-width: 2.5; }
  .blocked rect { stroke-dasharray: 4 3; }
  #side { width: 360px; border-left: 1px solid #222a35; padding: 16px;
          overflow: auto; background: #11151c; }
  #side h2 { margin: 0 0 4px; font-size: 15px; }
  #side .meta { color: #8a94a2; font-size: 12px; margin-bottom: 12px; }
  #side .desc { white-space: pre-wrap; color: #c4ccd6; }
  #side .deps { margin-top: 14px; }
  #side .deps b { color: #f0a830; }
  #side code { background: #1c232e; padding: 1px 5px; border-radius: 4px; }
  #legend { position: absolute; top: 10px; left: 10px; background: #11151ccc;
            border: 1px solid #222a35; border-radius: 6px; padding: 8px 10px;
            font-size: 11px; backdrop-filter: blur(4px); }
  #legend .row { display: flex; align-items: center; gap: 6px; margin: 2px 0; }
  #legend .sw { width: 12px; height: 12px; border-radius: 3px; }
  #controls { position: absolute; top: 10px; right: 10px; font-size: 11px; }
  #controls label { background: #11151ccc; border: 1px solid #222a35;
                    padding: 4px 8px; border-radius: 6px; cursor: pointer; }
  .muted { color: #6b7585; }
</style>
</head>
<body>
<div id="graph">
  <div id="legend"></div>
  <div id="controls"><label><input type="checkbox" id="hideClosed" checked> hide closed</label></div>
</div>
<div id="side"><span class="muted">Click a node. Hover to trace its blocking chain.<br><br>
Columns = blocking depth (left = do first). Dashed border = blocked by open work.</span></div>

<script>
const SEEDS = __DATA__;

const PRIO = {
  0: {label:"P0",  c:"#e5484d"}, 1: {label:"High", c:"#e5484d"},
  2: {label:"Med", c:"#f0a830"}, 3: {label:"Low",  c:"#4a8cf0"},
  4: {label:"Backlog", c:"#5a6675"},
};
const prioOf = s => PRIO[s.priority] || PRIO[4];

const COLW = 230, ROWH = 64, PADX = 30, PADY = 30, NW = 190, NH = 46;

function build(hideClosed) {
  const seeds = SEEDS.filter(s => !(hideClosed && s.status === "closed"));
  const ids = new Set(seeds.map(s => s.id));
  const byId = Object.fromEntries(seeds.map(s => [s.id, s]));
  const openSet = new Set(seeds.filter(s => s.status !== "closed").map(s => s.id));

  // edges: blocker -> blocked. Merge blockedBy + inverse of blocks.
  const edges = new Set();
  for (const s of seeds) {
    for (const b of (s.blockedBy || [])) if (ids.has(b)) edges.add(b + "|" + s.id);
    for (const b of (s.blocks || []))   if (ids.has(b)) edges.add(s.id + "|" + b);
  }
  const E = [...edges].map(e => e.split("|"));
  const preds = {}, succs = {};
  for (const id of ids) { preds[id] = []; succs[id] = []; }
  for (const [a, b] of E) { succs[a].push(b); preds[b].push(a); }

  // longest-path layering (cycle-guarded)
  const layer = {};
  const visiting = new Set();
  function L(id) {
    if (id in layer) return layer[id];
    if (visiting.has(id)) return 0;        // break cycle
    visiting.add(id);
    let m = 0;
    for (const p of preds[id]) m = Math.max(m, L(p) + 1);
    visiting.delete(id);
    return layer[id] = m;
  }
  for (const id of ids) L(id);

  // group by layer, order within layer by priority then id
  const cols = {};
  for (const id of ids) (cols[layer[id]] ||= []).push(id);
  for (const k in cols) cols[k].sort((x, y) =>
    (byId[x].priority - byId[y].priority) || x.localeCompare(y));

  const pos = {};
  let maxRows = 0;
  for (const k of Object.keys(cols).map(Number).sort((a, b) => a - b)) {
    cols[k].forEach((id, i) => pos[id] = { x: PADX + k * COLW, y: PADY + i * ROWH });
    maxRows = Math.max(maxRows, cols[k].length);
  }
  const ncols = Object.keys(cols).length;
  return { seeds, byId, openSet, E, preds, succs, pos,
           W: PADX * 2 + ncols * COLW, H: PADY * 2 + maxRows * ROWH };
}

function ancestors(id, preds) {
  const out = new Set(), stack = [id];
  while (stack.length) { const n = stack.pop();
    for (const p of preds[n]) if (!out.has(p)) { out.add(p); stack.push(p); } }
  return out;
}
function descendants(id, succs) {
  const out = new Set(), stack = [id];
  while (stack.length) { const n = stack.pop();
    for (const s of succs[n]) if (!out.has(s)) { out.add(s); stack.push(s); } }
  return out;
}

let selected = null;

function render() {
  const hideClosed = document.getElementById("hideClosed").checked;
  const g = build(hideClosed);
  const NS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(NS, "svg");
  svg.setAttribute("width", g.W); svg.setAttribute("height", g.H);

  const edgeEls = {};
  for (const [a, b] of g.E) {
    const pa = g.pos[a], pb = g.pos[b];
    const x1 = pa.x + NW, y1 = pa.y + NH / 2, x2 = pb.x, y2 = pb.y + NH / 2;
    const mx = (x1 + x2) / 2;
    const path = document.createElementNS(NS, "path");
    path.setAttribute("d", `M${x1},${y1} C${mx},${y1} ${mx},${y2} ${x2},${y2}`);
    path.setAttribute("class", "edge");
    svg.appendChild(path);
    (edgeEls[a] ||= []).push(path); (edgeEls[b] ||= []).push(path);
  }

  const nodeEls = {};
  for (const s of g.seeds) {
    const p = g.pos[s.id], pr = prioOf(s);
    const blocked = (s.blockedBy || []).some(b => g.openSet.has(b)) && s.status !== "closed";
    const grp = document.createElementNS(NS, "g");
    grp.setAttribute("class", "node" + (blocked ? " blocked" : ""));
    grp.setAttribute("transform", `translate(${p.x},${p.y})`);
    const rect = document.createElementNS(NS, "rect");
    rect.setAttribute("width", NW); rect.setAttribute("height", NH);
    rect.setAttribute("fill", s.status === "closed" ? "#1b2129" : "#1f2630");
    rect.setAttribute("stroke", pr.c);
    grp.appendChild(rect);
    const id = document.createElementNS(NS, "text");
    id.setAttribute("class", "id"); id.setAttribute("x", 9); id.setAttribute("y", 17);
    id.textContent = s.id + (s.status === "closed" ? " ✓" : "");
    grp.appendChild(id);
    const t = document.createElementNS(NS, "text");
    t.setAttribute("class", "title"); t.setAttribute("x", 9); t.setAttribute("y", 33);
    t.textContent = s.title.length > 30 ? s.title.slice(0, 29) + "…" : s.title;
    grp.appendChild(t);

    grp.addEventListener("mouseenter", () => highlight(s.id, g, nodeEls));
    grp.addEventListener("mouseleave", () => clearHi(g, nodeEls, edgeEls));
    grp.addEventListener("click", () => { selected = s.id; showSide(s, g); });
    nodeEls[s.id] = grp;
    svg.appendChild(grp);
  }

  const graph = document.getElementById("graph");
  [...graph.querySelectorAll("svg")].forEach(e => e.remove());
  graph.appendChild(svg);
  drawLegend();
  if (selected && g.byId[selected]) showSide(g.byId[selected], g);
}

function highlight(id, g, nodeEls) {
  const chain = new Set([id, ...ancestors(id, g.preds), ...descendants(id, g.succs)]);
  for (const [nid, el] of Object.entries(nodeEls))
    el.classList.toggle("dim", !chain.has(nid));
  // light any edge whose both endpoints are in the focused node's chain
  const paths = document.querySelectorAll("#graph svg .edge");
  g.E.forEach(([a, b], k) => {
    if (paths[k]) paths[k].classList.toggle("hot", chain.has(a) && chain.has(b));
  });
}

function clearHi(g, nodeEls) {
  for (const el of Object.values(nodeEls)) el.classList.remove("dim");
  document.querySelectorAll(".edge").forEach(e => e.classList.remove("hot"));
}

function showSide(s, g) {
  const pr = prioOf(s);
  for (const el of document.querySelectorAll(".node")) el.classList.remove("sel");
  const side = document.getElementById("side");
  const names = ids => (ids || []).filter(i => g.byId[i])
    .map(i => `<code>${i}</code> ${g.byId[i].title}`).join("<br>") || "<span class=muted>none</span>";
  side.innerHTML = `
    <h2>${s.id}</h2>
    <div class="meta">${s.title}</div>
    <div class="meta">${pr.label} · ${s.type || "?"} · ${s.status}
      ${(s.labels || []).map(l => `<code>${l}</code>`).join(" ")}
      ${s.plan_id ? ` · plan <code>${s.plan_id}</code>` : ""}</div>
    <div class="desc">${(s.description || "").replace(/</g, "&lt;")}</div>
    <div class="deps"><b>Blocked by:</b><br>${names(s.blockedBy)}</div>
    <div class="deps"><b>Blocks:</b><br>${names(s.blocks)}</div>`;
}

function drawLegend() {
  const seen = [1, 2, 3, 4];
  document.getElementById("legend").innerHTML =
    seen.map(p => `<div class="row"><span class="sw" style="background:${PRIO[p].c}"></span>${PRIO[p].label}</div>`).join("")
    + `<div class="row muted" style="margin-top:4px">▱ dashed = blocked</div>`;
}

document.getElementById("hideClosed").addEventListener("change", render);
render();
</script>
</body>
</html>
"""


def main() -> None:
    args = [a for a in sys.argv[1:] if a != "--open"]
    out = Path(args[0]).resolve() if args else DEFAULT_OUT
    seeds = fetch_seeds()
    html = HTML.replace("__DATA__", json.dumps(seeds, ensure_ascii=False))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out}  ({len(seeds)} seeds)")
    if "--open" in sys.argv:
        webbrowser.open(out.as_uri())


if __name__ == "__main__":
    main()
