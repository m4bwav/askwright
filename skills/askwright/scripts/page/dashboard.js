"use strict";
const token = document.querySelector('meta[name="ask-token"]').content;
const sessions = document.querySelector("#sessions");
const search = document.querySelector("#search");
const product = document.querySelector("#product");
const showAll = document.querySelector("#show-all");
const showBroken = document.querySelector("#show-broken");
const error = document.querySelector("#error");
let rows = [];
let snapshot = null;
let refreshTask = null;
let opening = false;
let changing = false;
let view = "inbox";
const expanded = new Set();
// Column sort, newest first by default; remembered per browser when storage allows.
const columns = [["title", "Title"], ["project", "Project"], ["updated", "Last updated"], ["action", "Action"]];
let sort = {key: "updated", dir: "desc"};
try {
  const saved = JSON.parse(localStorage.getItem("askwright-sort") || "null");
  if (saved && columns.some(([key]) => key === saved.key) && ["asc", "desc"].includes(saved.dir)) sort = saved;
} catch (e) { /* storage unavailable: keep the default */ }
const previews = new Set();
const snoozeOptions = [[3600, "1 hour"], [14400, "4 hours"], [86400, "1 day"],
  [259200, "3 days"], [604800, "1 week"]];

function node(tag, text, className) {
  const el = document.createElement(tag);
  el.textContent = text;
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

function report(message) {
  error.textContent = message;
  error.hidden = !message;
}

function render() {
  const focused = document.activeElement.dataset.focus;
  const term = search.value.trim().toLowerCase();
  const inView = rows.filter(row => (row.state || "inbox") === view);
  // Unavailable sessions (moved or deleted folders, unreadable sets) stay hidden until asked for.
  const broken = inView.filter(row => row.error).length;
  document.querySelector("#broken-count").textContent = broken;
  showBroken.closest("label").hidden = !broken && !showBroken.checked;
  const visible = inView.filter(row => (row.error ? showBroken.checked :
      view !== "inbox" || showAll.checked || row.pending > 0) &&
    (!product.value || row.product === product.value) &&
    [row.title, row.path, row.context, row.product, row.session, row.asked_by, row.error,
      row.project && row.project.name, row.project && row.project.path]
      .join(" ").toLowerCase().includes(term));
  visible.sort(compare);
  sessions.replaceChildren();
  const table = node("table", "", "sessions");
  const head = node("tr", "");
  for (const [key, label] of columns) {
    const th = node("th", "");
    th.scope = "col";
    const on = sort.key === key;
    th.setAttribute("aria-sort", on ? (sort.dir === "asc" ? "ascending" : "descending") : "none");
    const button = node("button", label, "sort");
    button.type = "button";
    button.dataset.focus = `sort:${key}`;
    button.dataset.sort = key;
    const arrow = node("span", on ? (sort.dir === "asc" ? "▲" : "▼") : "", "arrow");
    arrow.setAttribute("aria-hidden", "true");
    button.append(arrow);
    button.addEventListener("click", () => setSort(key));
    th.append(button);
    head.append(th);
  }
  const thead = node("thead", "");
  thead.append(head);
  table.append(thead);
  for (const row of visible) {
    const body = node("tbody", "");
    body.dataset.session = row.id;
    const open = expanded.has(row.id);
    const tr = node("tr", "", "row" + (row.error ? " broken" : ""));
    const titleCell = node("td", "", "title");
    const toggle = node("button", "", "toggle");
    toggle.type = "button";
    toggle.dataset.focus = `${row.id}:toggle`;
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-controls", `detail-${row.id}`);
    const chev = node("span", open ? "▾" : "▸", "chev");
    chev.setAttribute("aria-hidden", "true");
    toggle.append(chev, node("span", row.title || "Unavailable session", "name"));
    toggle.addEventListener("click", () => {
      if (expanded.has(row.id)) expanded.delete(row.id);
      else expanded.add(row.id);
      render();
    });
    titleCell.append(toggle);
    if (!row.error) titleCell.append(node("span", row.pending ? `${row.pending} open` : "done", row.pending ? "badge" : "badge done"));
    const projectCell = node("td", "", "proj");
    if (row.project) {
      const link = node("a", row.project.name);
      link.href = "/projects/" + encodeURIComponent(row.project.slug);
      if (row.project.path) link.title = row.project.path;
      projectCell.append(link);
    } else {
      projectCell.append(node("span", "-", "meta"));
    }
    const whenCell = node("td", "", "updated");
    if (!row.error) whenCell.append(askTime.el(row.last_worked, ""));
    const actionCell = node("td", "", "action");
    if (!row.error) actionCell.append(isDone(row) ? copyButton(row, "Copy prompt", "quick") : openButton(row, "quick"));
    tr.append(titleCell, projectCell, whenCell, actionCell);
    body.append(tr);
    const detailRow = node("tr", "", "detail");
    detailRow.id = `detail-${row.id}`;
    detailRow.hidden = !open;
    const cell = node("td", "");
    cell.colSpan = 4;
    if (open) cell.append(...detail(row));
    detailRow.append(cell);
    body.append(detailRow);
    table.append(body);
  }
  if (visible.length) sessions.append(table);
  if (!visible.length) sessions.append(node("p", rows.length ?
    "No sessions match this view. Try another list, All sessions or clear the filters." :
    "No sessions registered yet. Agents register automatically when they create or serve an askwright set."));
  renderProjects();
  document.querySelector("#summary").textContent =
    `${needs(inView.reduce((sum, row) => sum + (row.pending || 0), 0))} attention across ` +
    `${plural(inView.filter(row => row.pending > 0).length, "session")}. Showing ${visible.length} of ` +
    `${plural(inView.length, "session")} in this list.`;
  for (const button of document.querySelectorAll("[data-view]")) {
    const key = button.dataset.view;
    const label = {inbox: "Inbox", snoozed: "Snoozed", archived: "Archive"}[key];
    button.textContent = `${label} (${rows.filter(row => (row.state || "inbox") === key).length})`;
    button.setAttribute("aria-pressed", String(key === view));
  }
  showAll.closest("label").hidden = view !== "inbox";
  if (focused) {
    const control = Array.from(sessions.querySelectorAll("[data-focus]")).find(el => el.dataset.focus === focused);
    if (control) control.focus();
  }
}

// A set is done when nothing needs attention and something was answered: its quick action copies the prompt.
function isDone(row) {
  return !row.error && row.pending === 0 && row.answered > 0;
}

function openButton(row, key) {
  const button = node("button", "Open questions", "open");
  button.type = "button";
  button.disabled = changing || opening;
  button.dataset.session = row.id;
  button.dataset.focus = `${row.id}:open:${key}`;
  button.setAttribute("aria-label", `Open questions: ${row.title}`);
  button.addEventListener("click", () => open(row, button));
  return button;
}

function copyButton(row, label, key) {
  const copy = node("button", label, "copy" + (key === "quick" ? " open" : ""));
  copy.type = "button";
  copy.dataset.focus = `${row.id}:copy:${key}`;
  copy.title = "Copy a prompt that tells the agent to act on these answers and continue";
  copy.setAttribute("aria-label", `Copy continue prompt: ${row.title}`);
  copy.addEventListener("click", () => copyPrompt(row));
  return copy;
}

// Everything the old session card showed, for the expanded row.
function detail(row) {
  const out = [];
  if (row.error) {
    out.push(node("p", row.error, "session-error"));
  } else {
    out.push(node("p", [row.product || "Product not recorded", row.session, row.asked_by]
      .filter(Boolean).join(" / "), "meta"));
    if (row.context) out.push(node("p", row.context));
    const when = node("p", "", "meta when");
    when.append(askTime.el(row.last_worked, "Worked on "), " · ", askTime.el(row.created, "created "));
    out.push(when);
    out.push(node("p", `${row.pending} need attention / ${row.answered} answered`, "count"));
    const details = [
      row.unsure ? `${row.unsure} not sure` : "",
      row.note_only ? `${row.note_only} note only` : "",
      row.stale ? `${row.stale} changed since answered` : "",
      row.waiting ? `${row.waiting} waiting on another answer` : "",
      row.paused ? "Paused" : "",
      row.done ? "Marked done" : ""
    ].filter(Boolean);
    if (details.length) out.push(node("p", details.join(" / "), "meta"));
    const preview = node("details", "", "preview");
    preview.open = previews.has(row.id);
    const summary = node("summary", "Next 5 questions");
    summary.dataset.focus = `${row.id}:preview`;
    preview.append(summary);
    const questions = row.next_questions || [];
    if (questions.length) {
      const list = node("ol", "");
      for (const question of questions) list.append(node("li", question.question));
      preview.append(list);
    } else {
      preview.append(node("p", "No questions need attention."));
    }
    preview.addEventListener("toggle", () => {
      if (preview.isConnected) {
        if (preview.open) previews.add(row.id);
        else previews.delete(row.id);
      }
    });
    out.push(preview);
  }
  const actions = node("div", "", "actions");
  if (!row.error) actions.append(openButton(row, "detail"), copyButton(row, "Copy continue prompt", "detail"));
  if (row.state === "snoozed") {
    out.push(node("p", `Snoozed until ${new Date(row.snoozed_until * 1000).toLocaleString()}`, "meta"));
  }
  if (row.state === "archived" || row.state === "snoozed") {
    const label = row.state === "archived" ? "Unarchive" : "Unsnooze";
    actions.append(actionButton(row, label, "restore"));
  } else {
    const snooze = node("details", "", "snooze");
    const summary = node("summary", "Snooze");
    summary.dataset.focus = `${row.id}:snooze`;
    snooze.append(summary);
    const menu = node("div", "", "snooze-menu");
    menu.setAttribute("role", "group");
    menu.setAttribute("aria-label", `Snooze duration: ${row.title || row.id}`);
    for (const [seconds, label] of snoozeOptions) {
      menu.append(actionButton(row, label, "snooze", seconds));
    }
    snooze.append(menu);
    actions.append(snooze);
  }
  if (row.state !== "archived") actions.append(actionButton(row, "Archive", "archive"));
  out.push(actions);
  if (row.path) out.push(node("p", row.path, "path"));
  return out;
}

// The Projects tab: one row per project, most open questions first, then most recently worked on.
function renderProjects() {
  const panel = document.querySelector("#projects");
  const counts = new Map();
  for (const row of rows) {
    if (!row.project) continue;
    const c = counts.get(row.project.slug) || {name: row.project.name, sets: 0, pending: 0, last: null};
    c.sets += 1;
    c.pending += row.pending || 0;
    if (row.last_worked && (!c.last || Date.parse(row.last_worked) > Date.parse(c.last))) c.last = row.last_worked;
    counts.set(row.project.slug, c);
  }
  const items = [...counts].sort((a, b) => b[1].pending - a[1].pending ||
    (Date.parse(b[1].last) || 0) - (Date.parse(a[1].last) || 0) || a[1].name.localeCompare(b[1].name));
  document.querySelector("#tab-projects").textContent = `Projects (${items.length})`;
  if (!items.length) {
    panel.replaceChildren(node("p", "No projects yet. A set names its project with ask.py new --project.", "empty"));
    return;
  }
  const table = node("table", "", "sessions project-list");
  const head = node("tr", "");
  for (const label of ["Project", "Sets", "Open", "Last worked on"]) head.append(node("th", label));
  const thead = node("thead", "");
  thead.append(head);
  const body = node("tbody", "");
  for (const [slug, c] of items) {
    const tr = node("tr", "", "row");
    const name = node("td", "", "title");
    const a = node("a", c.name);
    a.href = "/projects/" + encodeURIComponent(slug);
    name.append(a);
    const when = node("td", "", "updated");
    if (c.last) when.append(askTime.el(c.last, ""));
    tr.append(name, node("td", plural(c.sets, "set"), "num"), node("td", c.pending ? `${c.pending} open` : "none", "num"), when);
    body.append(tr);
  }
  table.append(thead, body);
  panel.replaceChildren(table);
}

// Sessions and Projects tabs; the choice is remembered per browser and #projects opens the Projects tab.
let tab = location.hash === "#projects" ? "projects" : "sessions";
if (!location.hash) {
  try { if (localStorage.getItem("askwright-tab") === "projects") tab = "projects"; } catch (e) { /* keep the default */ }
}
function showTab(key, focus) {
  tab = key;
  for (const button of document.querySelectorAll("[data-tab]")) {
    const on = button.dataset.tab === key;
    button.setAttribute("aria-selected", String(on));
    button.tabIndex = on ? 0 : -1;
    document.querySelector("#" + button.getAttribute("aria-controls")).hidden = !on;
    if (on && focus) button.focus();
  }
  try { localStorage.setItem("askwright-tab", key); } catch (e) { /* storage unavailable */ }
}
for (const button of document.querySelectorAll("[data-tab]")) {
  button.addEventListener("click", () => showTab(button.dataset.tab));
  button.addEventListener("keydown", event => {
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
    showTab(tab === "sessions" ? "projects" : "sessions", true);
  });
}
showTab(tab);

async function copyText(text) {
  try { await navigator.clipboard.writeText(text); return true; } catch (e) { /* fall back below */ }
  const area = document.createElement("textarea");
  area.value = text;
  area.setAttribute("readonly", "");
  area.className = "visually-hidden";
  document.body.append(area);
  area.select();
  let ok = false;
  try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
  area.remove();
  return ok;
}

// The next-session prompt's Execute line goes last, on its own line, ready to paste into a new session.
function nextLine(path) {
  return path ? `\nThen carry on with the next-session prompt:\nExecute ${path}` : "";
}

async function copyPrompt(row) {
  const counts = `Status when copied (${new Date().toLocaleString()}): ${row.answered} answered, ${row.unsure} not sure, ` +
    `${row.note_only} note only, ${Math.max(0, row.pending - row.unsure - row.note_only)} not answered or changed.`;
  const ok = await copyText(`${row.continue_prompt || ""}
${counts}${nextLine(row.next_prompt)}`);
  const status = document.querySelector("#action-status");
  status.textContent = ok ? `Copied the continue prompt for ${row.title}. Paste it into your agent's chat.` :
    "Could not copy; your browser blocked the clipboard.";
  const toast = document.querySelector("#toast");
  toast.textContent = status.textContent;
  toast.hidden = false;
  clearTimeout(copyPrompt.timer);
  copyPrompt.timer = setTimeout(() => { toast.hidden = true; }, 4000);
}

function actionButton(row, label, action, seconds) {
  const button = node("button", label);
  button.type = "button";
  button.disabled = changing || opening;
  button.dataset.focus = `${row.id}:${action}:${seconds || ""}`;
  button.setAttribute("aria-label", `${label}: ${row.title || row.id}`);
  button.addEventListener("click", () => changeState(row, action, seconds));
  return button;
}

async function changeState(row, action, seconds) {
  if (changing || opening) return;
  changing = true;
  report("");
  for (const button of sessions.querySelectorAll("button")) button.disabled = true;
  try {
    if (refreshTask) await refreshTask;
    await api("/api/session-state", {id: row.id, action, ...(seconds ? {seconds} : {})});
    const labels = {archive: "Archived", snooze: "Snoozed", restore: "Restored to inbox"};
    document.querySelector("#action-status").textContent = `${labels[action]}: ${row.title || row.id}`;
    // Let the server decide expiration and ordering, including changes made in other tabs.
    changing = false;
    await refresh();
    if (!document.activeElement.closest("tbody")) {
      document.querySelector(`[data-view="${view}"]`).focus();
    }
  } catch (e) {
    report(`Cannot ${action} ${row.title || row.id}: ${e.message}`);
  } finally {
    changing = false;
    for (const button of sessions.querySelectorAll("button")) button.disabled = false;
  }
}

function refresh() {
  if (opening || changing) return Promise.resolve();
  if (!refreshTask) refreshTask = loadSessions().finally(() => { refreshTask = null; });
  return refreshTask;
}

async function loadSessions() {
  try {
    const data = await api("/api/sessions");
    const next = JSON.stringify(data.sessions);
    if (snapshot !== next) {
      rows = data.sessions;
      snapshot = next;
      const selected = product.value;
      product.replaceChildren(new Option("All products", ""));
      for (const value of [...new Set(rows.map(row => row.product).filter(Boolean))].sort()) {
        product.add(new Option(value, value));
      }
      product.value = selected;
      if (product.selectedIndex < 0) product.value = "";
      render();
    }
    report("");
  } catch (e) {
    report(`Cannot refresh sessions: ${e.message}. Previously loaded counts may be out of date.`);
  }
}

async function open(row, button) {
  if (opening || changing) return;
  opening = true;
  button.disabled = true;
  button.textContent = "Opening...";
  report("");
  try {
    const data = await api("/api/open", {id: row.id});
    window.location.assign(data.url);
  } catch (e) {
    report(`Cannot open ${row.title}: ${e.message}`);
  } finally {
    opening = false;
    button.disabled = false;
    button.textContent = "Open questions";
  }
}

document.querySelector("#filters").addEventListener("submit", event => event.preventDefault());
search.addEventListener("input", render);
product.addEventListener("change", render);
showAll.addEventListener("change", render);
showBroken.addEventListener("change", render);
for (const button of document.querySelectorAll("[data-view]")) {
  button.addEventListener("click", () => {
    view = button.dataset.view;
    document.querySelector("#action-status").textContent = "";
    render();
  });
}
document.addEventListener("click", event => {
  for (const dropdown of sessions.querySelectorAll(".snooze[open]")) {
    if (!dropdown.contains(event.target)) dropdown.open = false;
  }
});
document.addEventListener("keydown", event => {
  if (event.key !== "Escape") return;
  for (const dropdown of sessions.querySelectorAll(".snooze[open]")) {
    dropdown.open = false;
    dropdown.querySelector("summary").focus();
  }
});
document.querySelector("#refresh").addEventListener("click", refresh);
window.addEventListener("pageshow", refresh);
refresh();
setInterval(refresh, 5000);

function needs(n) {
  return `${plural(n, "question")} ${n === 1 ? "needs" : "need"}`;
}

function plural(n, word) {
  return `${n} ${word}${n === 1 ? "" : "s"}`;
}

function setSort(key) {
  // A new column starts in its natural order: newest first for times, A to Z for text, open before done.
  sort = sort.key === key ? {key, dir: sort.dir === "asc" ? "desc" : "asc"} : {key, dir: key === "updated" ? "desc" : "asc"};
  try { localStorage.setItem("askwright-sort", JSON.stringify(sort)); } catch (e) { /* not remembered */ }
  render();
}

function sortValue(row, key) {
  if (key === "title") return (row.title || "").toLowerCase();
  if (key === "project") return row.project ? row.project.name.toLowerCase() : null;
  if (key === "updated") return row.error ? null : (Date.parse(row.last_worked) || null);
  return row.error ? null : (isDone(row) ? 1 : 0);
}

function compare(a, b) {
  const x = sortValue(a, sort.key), y = sortValue(b, sort.key);
  // Rows without a value (no project, unavailable) stay at the bottom in both directions.
  if (x === null || y === null) return x === y ? 0 : x === null ? 1 : -1;
  const order = x < y ? -1 : x > y ? 1 : 0;
  return (sort.dir === "asc" ? order : -order) || (a.title || "").localeCompare(b.title || "");
}
