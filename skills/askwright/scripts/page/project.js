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

async function load() {
  try {
    project = (await api("/api/project?slug=" + encodeURIComponent(slug))).project;
    render(project);
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
setInterval(load, 15000);
