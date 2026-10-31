"use strict";
const token = document.querySelector('meta[name="ask-token"]').content;
const sessions = document.querySelector("#sessions");
const search = document.querySelector("#search");
const product = document.querySelector("#product");
const showAll = document.querySelector("#show-all");
const error = document.querySelector("#error");
let rows = [];
let snapshot = null;
let refreshTask = null;
let opening = false;
let changing = false;
let view = "inbox";
const expanded = new Set();
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
  const visible = inView.filter(row => (view !== "inbox" || showAll.checked || row.pending > 0 || row.error) &&
    (!product.value || row.product === product.value) &&
    [row.title, row.path, row.context, row.product, row.session, row.asked_by, row.error,
      row.project && row.project.name, row.project && row.project.path]
      .join(" ").toLowerCase().includes(term));
  sessions.replaceChildren();
  for (const row of visible) {
    const card = node("article", "");
    card.dataset.session = row.id;
    if (row.project) {
      const proj = node("p", "Project: ", "project");
      const link = node("a", row.project.name);
      link.href = "/projects/" + encodeURIComponent(row.project.slug);
      if (row.project.path) link.title = row.project.path;
      proj.append(link);
      card.append(proj);
    }
    card.append(node("h2", row.title || "Unavailable session"));
    if (row.error) {
      card.append(node("p", row.error, "session-error"));
    } else {
      card.append(node("p", [row.product || "Product not recorded", row.session, row.asked_by]
        .filter(Boolean).join(" / "), "meta"));
      if (row.context) card.append(node("p", row.context));
      const when = node("p", "", "meta when");
      when.append(askTime.el(row.last_worked, "Worked on "), " · ", askTime.el(row.created, "created "));
      card.append(when);
      card.append(node("p", `${row.pending} need attention / ${row.answered} answered`, "count"));
      const details = [
        row.unsure ? `${row.unsure} not sure` : "",
        row.note_only ? `${row.note_only} note only` : "",
        row.stale ? `${row.stale} changed since answered` : "",
        row.waiting ? `${row.waiting} waiting on another answer` : "",
        row.paused ? "Paused" : "",
        row.done ? "Marked done" : ""
      ].filter(Boolean);
      if (details.length) card.append(node("p", details.join(" / "), "meta"));
      const preview = node("details", "", "preview");
      preview.open = expanded.has(row.id);
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
          if (preview.open) expanded.add(row.id);
          else expanded.delete(row.id);
        }
      });
      card.append(preview);
      const button = node("button", "Open questions", "open");
      button.type = "button";
      button.disabled = changing || opening;
      button.dataset.session = row.id;
      button.dataset.focus = `${row.id}:open`;
      button.setAttribute("aria-label", `Open questions: ${row.title}`);
      button.addEventListener("click", () => open(row, button));
      const copy = node("button", "Copy continue prompt", "copy");
      copy.type = "button";
      copy.dataset.focus = `${row.id}:copy`;
      copy.setAttribute("aria-label", `Copy continue prompt: ${row.title}`);
      copy.addEventListener("click", () => copyPrompt(row));
      const actions = node("div", "", "actions");
      actions.append(button, copy);
      card.append(actions);
    }
    const actions = card.querySelector(".actions") || node("div", "", "actions");
    if (!card.contains(actions)) card.append(actions);
    if (row.state === "snoozed") {
      card.append(node("p", `Snoozed until ${new Date(row.snoozed_until * 1000).toLocaleString()}`, "meta"));
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
    if (row.path) card.append(node("p", row.path, "path"));
    sessions.append(card);
  }
  if (!visible.length) sessions.append(node("p", rows.length ?
    "No sessions match this view. Try another list, All sessions or clear the filters." :
    "No sessions registered yet. Agents register automatically when they create or serve an askwright set."));
  renderProjects();
  document.querySelector("#summary").textContent =
    `${inView.reduce((sum, row) => sum + (row.pending || 0), 0)} questions need attention across ` +
    `${inView.filter(row => row.pending > 0).length} sessions. Showing ${visible.length} of ${inView.length} sessions in this list.`;
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

function renderProjects() {
  const nav = document.querySelector("#projects");
  const counts = new Map();
  for (const row of rows) {
    if (!row.project) continue;
    const c = counts.get(row.project.slug) || {name: row.project.name, sets: 0, pending: 0};
    c.sets += 1;
    c.pending += row.pending || 0;
    counts.set(row.project.slug, c);
  }
  const items = [...counts].sort((a, b) => b[1].pending - a[1].pending || a[1].name.localeCompare(b[1].name));
  nav.hidden = !items.length;
  const list = nav.querySelector("ul");
  list.replaceChildren(...items.map(([slug, c]) => {
    const li = node("li", "");
    const a = node("a", c.name);
    a.href = "/projects/" + encodeURIComponent(slug);
    li.append(a, node("span", c.pending ? ` ${c.pending} open` : ` ${c.sets} set${c.sets === 1 ? "" : "s"}`, "meta"));
    return li;
  }));
}

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

async function copyPrompt(row) {
  const counts = `Status when copied (${new Date().toLocaleString()}): ${row.answered} answered, ${row.unsure} not sure, ` +
    `${row.note_only} note only, ${Math.max(0, row.pending - row.unsure - row.note_only)} not answered or changed.`;
  const ok = await copyText(`${row.continue_prompt || ""}
${counts}`);
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
    if (!document.activeElement.closest("article")) {
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
