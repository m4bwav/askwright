"use strict";
const token = document.querySelector('meta[name="ask-token"]').content;
const slug = decodeURIComponent(location.pathname.split("/").pop());
const STATUS = {"active": "Active", "needs-direction": "Needs direction", "paused": "Paused", "done": "Done"};
const KINDS = {prompt: "Prompt run", note: "Note", status: "Status", direction: "Needs direction", set: "Question set"};
let project = null;
let showAll = false;

function node(tag, text, className) {
  const el = document.createElement(tag);
  if (text) el.textContent = text;
  if (className) el.className = className;
  return el;
}

async function api(path, body) {
  const response = await fetch(path, {
    method: body ? "POST" : "GET",
    headers: {"X-Ask-Token": token, ...(body ? {"Content-Type": "application/json"} : {})},
    ...(body ? {body: JSON.stringify(body)} : {})
  });
  const data = await response.json();
  if (!response.ok || !data.ok) throw new Error(data.error || `Request failed (${response.status})`);
  return data;
}

function fact(list, label, value, note) {
  const pair = node("div", "");
  const dd = node("dd", "");
  if (value instanceof Node) dd.append(value);
  else dd.textContent = value;
  if (note) dd.append(node("span", note, "fact-note"));
  pair.append(node("dt", label), dd);
  list.append(pair);
}

function place(text, href) {
  const li = node("li", "");
  if (href) {
    const a = node("a", text);
    a.href = href;
    a.rel = "noopener noreferrer";
    a.target = "_blank";
    li.append(a);
  } else {
    li.append(node("code", text));
  }
  return li;
}

async function openSet(row, button) {
  button.disabled = true;
  button.textContent = "Opening…";
  try { location.assign((await api("/api/open", {id: row.id})).url); }
  catch (e) { report(`Cannot open ${row.title}: ${e.message}`); button.disabled = false; button.textContent = "Open questions"; }
}

function setCard(row) {
  const card = node("article", "", "set-card");
  card.dataset.session = row.id;
  const head = node("h3", "");
  head.append(node("span", row.title || "Unavailable session", "set-title"));
  if (!row.error) head.append(node("span", row.pending ? `${row.pending} open` : "done", row.pending ? "badge" : "badge done"));
  card.append(head);
  if (row.error) { card.append(node("p", row.error, "session-error")); return card; }
  if (row.context) card.append(node("p", row.context));
  const meta = node("p", "", "meta");
  meta.append(`${row.answered} answered · `, askTime.el(row.last_worked, "worked on "), " · ", askTime.el(row.created, "created "));
  card.append(meta);
  const button = node("button", "Open questions", row.pending ? "open" : "");
  button.type = "button";
  button.addEventListener("click", () => openSet(row, button));
  card.append(button);
  return card;
}

function report(message) {
  const error = document.querySelector("#error");
  error.textContent = message;
  error.hidden = !message;
}

function toast(message) {
  const el = document.querySelector("#toast");
  el.textContent = message;
  el.hidden = false;
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => { el.hidden = true; }, 2200);
}

async function copyText(text) {
  try { await navigator.clipboard.writeText(text); return true; } catch (e) { /* fall back below */ }
  const area = document.createElement("textarea");
  area.value = text;
  area.className = "visually-hidden";
  document.body.append(area);
  area.select();
  let ok = false;
  try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
  area.remove();
  return ok;
}

function promptWhen(run) {
  if (!run) return "none recorded";
  const span = node("span", "");
  span.append(askTime.el(run.at));
  span.title = run.path || run.text;
  return span;
}

function renderAttention(p) {
  const items = [];
  if (p.status === "needs-direction") {
    const li = node("li", "", "direction");
    li.append(node("strong", "Direction wanted: "), p.direction || "the agent is waiting on your call.");
    items.push(li);
  }
  const waiting = p.sets.filter(r => r.pending > 0 && !r.error);
  if (waiting.length) {
    const li = node("li", "");
    li.append(`${p.pending} question${p.pending === 1 ? " waits" : "s wait"} for your answers in ${waiting.length} set${waiting.length === 1 ? "" : "s"}. `);
    const button = node("button", waiting.length > 1 ? "Open the newest" : "Open it", "open");
    button.title = waiting[0].title;
    button.type = "button";
    button.addEventListener("click", () => openSet(waiting[0], button));
    li.append(button);
    items.push(li);
  }
  document.querySelector("#attention-list").replaceChildren(...items);
  document.querySelector("#attention").hidden = !items.length;
}

function renderTimeline(p) {
  const withLog = document.querySelector("#show-log").checked;
  const items = p.timeline.filter(h => withLog || h.source !== "log");
  const shown = showAll ? items : items.slice(0, 20);
  const list = document.querySelector("#timeline");
  list.replaceChildren(...shown.map(h => {
    const li = node("li", "", "event " + (h.source === "log" ? "from-log" : "kind-" + h.kind));
    const when = askTime.el(h.at);
    when.className = "when";
    li.append(when, node("span", KINDS[h.kind] || h.kind, "kind"), node("span", h.text, "what"));
    if (h.path) li.title = h.path;
    return li;
  }));
  if (!items.length) list.append(node("li", "Nothing recorded yet. Agents add entries with ask.py project NAME --note or --prompt-run.", "meta"));
  const more = document.querySelector("#more-history");
  more.hidden = items.length <= 20;
  more.textContent = showAll ? "Show fewer" : `Show all (${items.length})`;
}

function render(p) {
  document.title = `askwright | ${p.name}`;
  document.querySelector("#name").textContent = p.name;
  const status = document.querySelector("#status");
  status.textContent = STATUS[p.status] || p.status;
  status.dataset.status = p.status;
  status.hidden = false;
  document.querySelector("#description").textContent = p.description || "No description yet (ask.py project NAME --description TEXT).";
  renderAttention(p);
  const facts = document.querySelector("#facts");
  facts.replaceChildren();
  fact(facts, "Created", askTime.el(p.created));
  fact(facts, "Last worked on", askTime.el(p.last_worked));
  fact(facts, "First prompt run", promptWhen(p.first_prompt));
  fact(facts, "Last prompt run", promptWhen(p.last_prompt), p.prompt_runs > 1 ? ` · ${p.prompt_runs} runs` : "");
  fact(facts, "Question sets", String(p.sets.length), ` · ${p.pending} open · ${p.answered} answered`);
  const next = p.prompt_files[0];
  document.querySelector("#next").hidden = !next;
  if (next) {
    document.querySelector("#next-path").textContent = next.path;
    document.querySelector("#next-path").title = "changed " + askTime.exact(next.modified);
    const rest = p.prompt_files.slice(1);
    document.querySelector("#other-prompts").hidden = !rest.length;
    document.querySelector("#prompt-files").replaceChildren(...rest.map(f => {
      const li = place(f.path);
      li.append(" ", askTime.el(f.modified, "changed "));
      return li;
    }));
  }
  const goals = document.querySelector("#goals");
  goals.replaceChildren(...(p.goals.length ? p.goals.map(g => node("li", g)) :
    [node("li", "No goals recorded (ask.py project NAME --goal TEXT).", "meta")]));
  document.querySelector("#state").hidden = !p.handoffs.length;
  document.querySelector("#handoffs").replaceChildren(...p.handoffs.map(h => {
    const box = node("div", "", "handoff");
    const meta = node("p", "", "meta");
    meta.append(node("code", h.path), " · ", askTime.el(h.modified, "updated "));
    box.append(meta, node("div", h.excerpt.replace(/^#{1,6}\s+/gm, "") + (h.excerpt.length >= 1500 ? " …" : ""), "excerpt"));
    return box;
  }));
  const places = document.querySelector("#places");
  places.replaceChildren(...p.repos.map(r => place(r, /^https?:\/\//.test(r) ? r : null)), ...p.dirs.map(d => place(d)));
  document.querySelector("#where").hidden = !(p.repos.length || p.dirs.length);
  const sets = document.querySelector("#sets");
  sets.replaceChildren(...(p.sets.length ? p.sets.map(setCard) : [node("p", "No question sets yet.")]));
  renderTimeline(p);
}

function list(items, empty) {
  const ul = node("ul", "", "places");
  if (!items.length) return node("p", empty, "meta");
  items.forEach(t => ul.append(node("li", t)));
  return ul;
}

function renderGrind(g) {
  const sec = document.querySelector("#grind");
  sec.hidden = !g;
  if (!g) return;
  const body = document.querySelector("#grind-body");
  body.replaceChildren();
  (g.problems || []).forEach(p => body.append(node("p", "Could not read: " + p, "meta")));
  if (g.problems && g.problems.length && !g.waiting) return;
  body.append(node("h3", "Waiting on a person"), list(g.waiting || [], "Nothing waits on a person."));
  body.append(node("h3", "Being worked"),
    list((g.working || []).map(w => `${w.id} ${w.title}` + (w.person ? ` (${w.person})` : "")), "No item claimed."));
  if ((g.asks || []).length)
    body.append(node("h3", "Open asks"), list(g.asks.map(a => `${a.title}: ${a.open} open`), ""));
  const c = Object.entries(g.counts || {}).map(([k, v]) => `${k} ${v}`).join(" · ");
  if (c) body.append(node("p", "Since " + (g.since || "today") + ": " + c, "meta"));
}

function renderChains(c) {
  const sec = document.querySelector("#chains");
  const runs = (c && c.runs) || [], probs = (c && c.problems) || [];
  sec.hidden = !runs.length && !probs.length;
  if (sec.hidden) return;
  const body = document.querySelector("#chains-body");
  body.replaceChildren(...probs.map(p => node("p", "Could not read: " + p, "meta")));
  const ul = node("ul", "", "places");
  runs.forEach(r => {
    const li = node("li", "");
    li.append(node("strong", r.name), node("span",
      ` · ${r.sessions} sessions · ${DUR(Math.round(r.seconds / 60))} · ${(r.tokens / 1e6).toFixed(1)} M tokens` +
      (r.usd ? ` · $${r.usd.toFixed(2)}` : "") + (r.open ? ` · ${r.open} open` : ""), "meta"));
    if (r.last) li.append(" ", askTime.el(r.last, "last "));
    ul.append(li);
  });
  body.append(ul);
  if (c.total > runs.length) body.append(node("p", `${c.total - runs.length} older runs not shown.`, "meta"));
}

const AGO = m => m == null ? "" : m < 60 ? `${m} min ago` : `${Math.floor(m / 60)} h ${m % 60} min ago`;
const DUR = m => m < 60 ? `${m} min` : `${Math.floor(m / 60)} h ${m % 60} min`;

function agentRow(r) {
  const box = node("article", "", "agent " + r.status.replace(/[^a-z]+/g, "-"));
  const head = node("p", "", "agent-head");
  head.append(node("strong", r.status), node("span", " " + (r.kind || (r.claims.length && !r.cwd ? "grindwright claim" : "session")), "meta"));
  if (r.claims.some(c => c.quiet || (c.session_info || {}).quiet)) head.append(node("span", " quiet mode (no new work)", "tag"));
  if (r.claims.some(c => c.handed_to || c.handed_off || c.handoff)) head.append(node("span", " handed off", "tag"));
  if (r.claims.some(c => c.taken_over_from || c.took_over || c.takeover)) head.append(node("span", " taken over", "tag"));
  box.append(head);
  const what = r.claims.map(c => `${c.id} ${c.title}`).join("; ") || r.title || r.name || "No claimed task";
  box.append(node("p", what, "agent-what"));
  const facts = node("dl", "", "facts small");
  const add = (k, v) => { if (v) fact(facts, k, v); };
  add("Branch", r.branch);
  add("Folder", r.worktree || r.cwd);
  add("Machine", r.machine);
  add("Started", r.started ? when(r.started) : "");
  add("Last activity", r.last_activity ? `${when(r.last_activity)} (${AGO(r.minutes_quiet)})` : "none seen");
  if (r.running_minutes != null) add("Running for", DUR(r.running_minutes) + (r.status === "live" ? " so far" : ""));
  add("Session", r.session);
  if (r.stale_reason) add("Why stale", r.stale_reason);
  add("How it is known", r.evidence.join("; "));
  box.append(facts);
  if (r.subagents.length) {
    const ul = node("ul", "", "subagents");
    r.subagents.forEach(a => ul.append(node("li", `${a.description || a.id} · ${a.status} · ${AGO(a.minutes_quiet)}`)));
    box.append(node("p", "Subagents running", "meta"), ul);
  }
  return box;
}

function when(iso) {
  const d = new Date(iso);
  return isNaN(d) ? iso : d.toLocaleString();
}

function totalsText(t) {
  if (!t || !t.running_minutes) return "";
  const days = Object.entries(t.by_day || {}).map(([d, m]) => `${d} ${DUR(m)}`).join(", ");
  return ` Agent time: ${DUR(t.running_minutes)} in total (${days}).`;
}

async function loadExtras() {
  try {
    const x = await api("/api/project-extras?slug=" + encodeURIComponent(slug));
    renderGrind(x.grind);
    renderChains(x.chain_runs);
  } catch (e) {
    renderChains({runs: [], problems: ["grind board and chain runs: " + e.message]});
  }
}

async function loadAgents() {
  const meta = document.querySelector("#running-meta");
  try {
    const d = await api("/api/agents?slug=" + encodeURIComponent(slug));
    const live = d.rows.filter(r => r.status === "live").length;
    meta.textContent = (d.rows.length ? `${d.rows.length} seen, ${live} live.` : "No agent session seen in this project's folders.")
      + totalsText(d.totals) + ` Checked ${when(d.built)}; refreshes every 15 s. ${d.note || ""}`;
    const rows = document.querySelector("#running-rows");
    rows.replaceChildren(...d.rows.map(agentRow), ...d.problems.map(p => node("p", "Could not read: " + p, "problem")));
    const idle = d.worktrees_idle || [];
    document.querySelector("#idle-trees").hidden = !idle.length;
    document.querySelector("#idle-list").replaceChildren(...idle.map(t =>
      node("li", `${t.path} (${t.branch || "no branch"}) · last git write ${t.minutes_since_git == null ? "unknown" : AGO(t.minutes_since_git)}`)));
  } catch (e) {
    meta.textContent = "Could not check who is running: " + e.message + ". Do not assume nobody is.";
    meta.className = "problem";
  }
}

function renderLinks(p) {
  const box = document.querySelector("#plugin-links");
  const links = p.links || {};
  box.replaceChildren(...Object.entries(links).filter(([k]) => k !== "steerwright" || !document.querySelector('a[href="/go/steerwright"]'))
    .map(([k, href]) => { const a = node("a", k, "chip secondary"); a.href = href; a.title = `${k} page for this project`; return a; }));
}

async function load() {
  try {
    project = (await api("/api/project?slug=" + encodeURIComponent(slug))).project;
    render(project);
    renderLinks(project);
    report("");
  } catch (e) {
    document.querySelector("#name").textContent = "Project not found";
    report(e.message);
  }
}

document.querySelector("#copy-start").addEventListener("click", async () => {
  const next = project && project.prompt_files[0];
  if (next) toast(await copyText(`Execute ${next.path}`) ? "Start command copied" : "Copy failed: select the path instead");
});
document.querySelector("#show-log").addEventListener("change", () => project && renderTimeline(project));
document.querySelector("#more-history").addEventListener("click", () => { showAll = !showAll; if (project) renderTimeline(project); });
load();
loadAgents();
loadExtras();
setInterval(() => { load(); loadAgents(); }, 15000);
setInterval(loadExtras, 60000);
