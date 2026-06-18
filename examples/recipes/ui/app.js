"use strict";

// ── The catalog the "Seed sourdough demo" button posts (same data as demo.py) ──
const SEED = {
  ingredients: [
    ["flour", "Bread flour", "g"],
    ["water", "Water", "ml"],
    ["salt", "Fine sea salt", "g"],
    ["olive_oil", "Olive oil", "ml"],
    ["garlic", "Garlic", "clove"],
  ],
  tools: [
    ["jar", "Glass fermentation jar"],
    ["mixer", "Stand mixer"],
    ["oven", "Deck oven"],
    ["knife", "Chef's knife"],
    ["bowl", "Mixing bowl"],
  ],
  recipes: [
    {
      recipe_id: "cultivate_starter", name: "Sourdough starter",
      output_type: "active_starter", output_unit: "jar",
      steps: [[1, "mix", "jar"], [2, "ferment", "jar"]],
      inputs: [[1, "flour", 100, "g"], [1, "water", 100, "ml"]],
    },
    {
      recipe_id: "bake_sourdough", name: "Sourdough loaf", requires_type: "active_starter",
      output_type: "sourdough_loaf", output_unit: "loaf",
      steps: [[1, "mix", "mixer"], [2, "ferment", "jar"], [3, "bake", "oven"]],
      inputs: [[1, "flour", 500, "g"], [1, "water", 350, "ml"], [1, "salt", 10, "g"]],
    },
    {
      recipe_id: "make_croutons", name: "Garlic croutons", requires_type: "sourdough_loaf",
      output_type: "garlic_croutons", output_unit: "bowl",
      steps: [[1, "cut", "knife"], [2, "toss", "bowl"], [3, "bake", "oven"]],
      inputs: [[2, "olive_oil", 30, "ml"], [2, "garlic", 2, "clove"]],
    },
  ],
};

// Friendly batch-id prefixes per recipe (so batches read "starter-1", "loaf-1", ...).
const SHORT = { cultivate_starter: "starter", bake_sourdough: "loaf", make_croutons: "croutons" };

const STEP = 450; // ms between revealed cascade events

// In-memory provenance graph, folded from the event stream (it *is* a projection).
const graph = { nodes: new Map(), edges: [] }; // nodes: id -> {id, type}; edges: {output, source}

// ── tiny helpers ──────────────────────────────────────────────────────────────
const $ = (id) => document.getElementById(id);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const SVGNS = "http://www.w3.org/2000/svg";

async function api(method, path, body) {
  const opts = { method, headers: { "content-type": "application/json" } };
  if (body !== undefined) opts.body = JSON.stringify(body);
  const res = await fetch(path, opts);
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`${method} ${path} → ${res.status}: ${detail}`);
  }
  return res.status === 204 ? null : res.json();
}

function setStatus(msg) { $("status").textContent = msg; }

// Unzip a parallel-list query output into an array of row objects.
function rows(out, keys) {
  const n = Math.max(0, ...keys.map((k) => (out[k] || []).length));
  return Array.from({ length: n }, (_, i) =>
    Object.fromEntries(keys.map((k) => [k, (out[k] || [])[i]]))
  );
}

// ── data ────────────────────────────────────────────────────────────────────
async function getRecipes() {
  const out = await api("GET", "/recipes");
  return rows(out, ["recipe_ids", "names", "requires_types", "output_types", "output_units"]);
}
async function getBatches() {
  const out = await api("GET", "/batches");
  return rows(out, ["batch_ids", "recipe_ids", "requires_types", "statuses"]);
}

// ── rendering: start bar + board ──────────────────────────────────────────────
async function refresh() {
  const [recipes, batches] = [await getRecipes(), await getBatches()];

  const bar = $("start-bar");
  bar.innerHTML = recipes.length ? "<span class='hint'>Start a batch:</span>" : "";
  for (const r of recipes) {
    const b = document.createElement("button");
    b.className = "mini";
    b.textContent = `+ ${r.names}`;
    b.title = `${r.recipe_ids} → ${r.output_types}`;
    b.onclick = () => startBatch(r, batches);
    bar.appendChild(b);
  }

  for (const status of ["blocked", "ready", "completed"]) $(`col-${status}`).innerHTML = "";
  for (const b of batches) renderCard(b);
  return batches;
}

function renderCard(b) {
  const col = $(`col-${b.statuses}`);
  if (!col) return;
  const card = document.createElement("div");
  card.className = "card";
  card.id = `card-${b.batch_ids}`;
  card.dataset.status = b.statuses;
  const waiting = b.requires_types
    ? `<div class="waiting">waiting on ${b.requires_types}</div>` : "";
  const advance = b.statuses === "ready"
    ? `<div class="row"><button class="mini advance" data-batch="${b.batch_ids}">advance ▶</button></div>` : "";
  card.innerHTML =
    `<div class="id">${b.batch_ids}</div><div class="meta">${b.recipe_ids}</div>${waiting}${advance}`;
  col.appendChild(card);
  const btn = card.querySelector(".advance");
  if (btn) btn.onclick = () => advance(b.batch_ids);
}

// ── actions ───────────────────────────────────────────────────────────────────
async function seed() {
  setStatus("seeding…");
  for (const [ingredient_type, name, unit] of SEED.ingredients)
    await api("POST", "/ingredients", { ingredient_type, name, unit });
  for (const [tool_id, name] of SEED.tools)
    await api("POST", "/tools", { tool_id, name });
  for (const r of SEED.recipes) {
    const body = {
      recipe_id: r.recipe_id, name: r.name,
      output_type: r.output_type, output_unit: r.output_unit,
    };
    if (r.requires_type) body.requires_type = r.requires_type;
    await api("POST", "/recipes", body);
    for (const [step_order, activity_kind, tool_id] of r.steps)
      await api("POST", "/recipe-steps", { recipe_id: r.recipe_id, step_order, activity_kind, tool_id });
    for (const [step_order, ingredient_type, qty, unit] of r.inputs)
      await api("POST", "/step-inputs", { recipe_id: r.recipe_id, step_order, ingredient_type, qty, unit });
  }
  setStatus("seeded — start the three batches");
  logCommand("seeded catalog (5 ingredients, 5 tools, 3 recipes)");
  await refresh();
}

async function startBatch(recipe, existing) {
  const short = SHORT[recipe.recipe_ids] || recipe.recipe_ids;
  const n = existing.filter((b) => b.recipe_ids === recipe.recipe_ids).length + 1;
  const batch_id = `${short}-${n}`;
  logCommand(`start_batch ${batch_id}`);
  const { events } = await api("POST", "/batches", { batch_id, recipe_id: recipe.recipe_ids });
  events.forEach(logEvent);
  await refresh();
}

async function advance(batchId) {
  setStatus(`advancing ${batchId}…`);
  document.querySelectorAll(".advance").forEach((b) => (b.disabled = true));
  logCommand(`advance_batch ${batchId}`);
  const { events } = await api("POST", "/batches/advance", { batch_id: batchId });

  // Animated replay: reveal one event at a time, folding each into the live state.
  for (const e of events) {
    logEvent(e);
    const d = e.data;
    if (e.event === "entity_produced") {
      graph.nodes.set(d.entity_id, { id: d.entity_id, type: d.entity_type });
      drawGraph(d.entity_id);
      pulse(d.batch_id);
    } else if (e.event === "entity_derived") {
      graph.edges.push({ output: d.output_entity_id, source: d.source_entity_id });
      drawGraph();
    } else if (e.event === "batch_completed") {
      moveToCompleted(d.batch_id);
    }
    await sleep(STEP);
  }
  setStatus(`done — ${batchId} cascaded`);
  await refresh();
}

async function reset() {
  await api("POST", "/reset");
  graph.nodes.clear();
  graph.edges.length = 0;
  drawGraph();
  $("log").innerHTML = "<div class='entry empty'>reset — seed the demo to begin</div>";
  $("trace").textContent = "";
  setStatus("");
  await refresh();
}

// ── board animation helpers ────────────────────────────────────────────────────
function pulse(batchId) {
  const card = $(`card-${batchId}`);
  if (!card) return;
  card.classList.add("pulse");
  setTimeout(() => card.classList.remove("pulse"), 300);
}
function moveToCompleted(batchId) {
  const card = $(`card-${batchId}`);
  if (!card) return;
  card.dataset.status = "completed";
  const btn = card.querySelector(".row");
  if (btn) btn.remove();
  $("col-completed").appendChild(card);
}

// ── event log ──────────────────────────────────────────────────────────────────
function logCommand(text) {
  const log = $("log");
  if (log.querySelector(".empty")) log.innerHTML = "";
  const el = document.createElement("div");
  el.className = "cmd";
  el.textContent = `→ ${text}`;
  log.appendChild(el);
  log.scrollTop = log.scrollHeight;
}
function logEvent(e) {
  const log = $("log");
  if (log.querySelector(".empty")) log.innerHTML = "";
  const d = e.data;
  const detail =
    d.entity_type || d.batch_id || d.entity_id || d.recipe_id || "";
  const el = document.createElement("div");
  el.className = "entry";
  el.innerHTML = `<span class="ev">${e.event}</span><span>${detail}</span>`;
  log.appendChild(el);
  log.scrollTop = log.scrollHeight;
}

// ── provenance graph (hand-rolled SVG, layered left→right by derivation depth) ──
function depthOf(id, seen = new Set()) {
  if (seen.has(id)) return 0;
  seen.add(id);
  const edge = graph.edges.find((e) => e.output === id);
  return edge ? 1 + depthOf(edge.source, seen) : 0;
}

function drawGraph(freshId) {
  const svg = $("graph");
  svg.innerHTML = "";

  const defs = document.createElementNS(SVGNS, "defs");
  defs.innerHTML =
    '<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">' +
    '<path d="M0,0 L10,5 L0,10 z" fill="#9aa4b2"/></marker>';
  svg.appendChild(defs);

  const ids = [...graph.nodes.keys()];
  if (!ids.length) return;

  // Position: x by derivation depth, y stacked within each depth column.
  const byDepth = new Map();
  const pos = new Map();
  for (const id of ids) {
    const depth = depthOf(id);
    if (!byDepth.has(depth)) byDepth.set(depth, []);
    byDepth.get(depth).push(id);
  }
  const W = 150, H = 44;
  for (const [depth, members] of byDepth) {
    members.forEach((id, i) => {
      pos.set(id, { x: 40 + depth * 250, y: 30 + i * 70 });
    });
  }

  // Edges: source (earlier) → output (later), arrow points to the derived entity.
  for (const e of graph.edges) {
    const a = pos.get(e.source), b = pos.get(e.output);
    if (!a || !b) continue;
    const line = document.createElementNS(SVGNS, "line");
    line.setAttribute("class", "edge");
    line.setAttribute("x1", a.x + W); line.setAttribute("y1", a.y + H / 2);
    line.setAttribute("x2", b.x); line.setAttribute("y2", b.y + H / 2);
    svg.appendChild(line);
  }

  // Nodes.
  for (const id of ids) {
    const p = pos.get(id);
    const node = graph.nodes.get(id);
    const g = document.createElementNS(SVGNS, "g");
    g.setAttribute("class", "node" + (id === freshId ? " fresh" : ""));
    g.setAttribute("transform", `translate(${p.x},${p.y})`);
    g.onclick = () => traceNode(id);

    const rect = document.createElementNS(SVGNS, "rect");
    rect.setAttribute("width", W); rect.setAttribute("height", H);
    rect.setAttribute("rx", 6);
    const text = document.createElementNS(SVGNS, "text");
    text.setAttribute("x", W / 2); text.setAttribute("y", H / 2 + 4);
    text.setAttribute("text-anchor", "middle");
    text.textContent = node.type;
    g.append(rect, text);
    svg.appendChild(g);
  }
}

async function traceNode(entityId) {
  const out = await api("GET", `/provenance/${encodeURIComponent(entityId)}`);
  $("trace").textContent = out.lines && out.lines.length
    ? out.lines.join("\n")
    : `${entityId} — a root entity (derived from nothing)`;
}

// ── boot ────────────────────────────────────────────────────────────────────
$("seed").onclick = () => seed().catch((e) => setStatus(e.message));
$("reset").onclick = () => reset().catch((e) => setStatus(e.message));
refresh().then((batches) => {
  if (!batches.length) $("log").innerHTML = "<div class='entry empty'>seed the demo to begin</div>";
}).catch((e) => setStatus(e.message));
