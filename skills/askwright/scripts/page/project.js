"use strict";
const token = document.querySelector('meta[name="ask-token"]').content;
const slug = decodeURIComponent(location.pathname.split("/").pop());

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

function fact(list, label, iso) {
  const dt = node("dt", label);
  const dd = node("dd", "");
  dd.append(askTime.el(iso));
  const pair = node("div", "");
  pair.append(dt, dd);
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

function setCard(row) {
  const card = node("article", "", "set-card");
  card.dataset.session = row.id;
  card.append(node("h3", row.title || "Unavailable session"));
  if (row.error) { card.append(node("p", row.error, "session-error")); return card; }
  if (row.context) card.append(node("p", row.context));
  const meta = node("p", "", "meta");
  meta.append(`${row.pending} need attention · ${row.answered} answered · `, askTime.el(row.last_worked, "worked on "),
    " · ", askTime.el(row.created, "created "));
  card.append(meta);
  const button = node("button", "Open questions", "open");
  button.type = "button";
  button.addEventListener("click", async () => {
    button.disabled = true;
    button.textContent = "Opening…";
    try { location.assign((await api("/api/open", {id: row.id})).url); }
    catch (e) { report(`Cannot open ${row.title}: ${e.message}`); button.disabled = false; button.textContent = "Open questions"; }
  });
  card.append(button);
  return card;
}

function report(message) {
  const error = document.querySelector("#error");
  error.textContent = message;
  error.hidden = !message;
}

async function load() {
  try {
    const p = (await api("/api/project?slug=" + encodeURIComponent(slug))).project;
    document.title = `askwright | ${p.name}`;
    document.querySelector("#name").textContent = p.name;
    document.querySelector("#description").textContent = p.description || "No description yet (ask.py project NAME --description TEXT).";
    const facts = document.querySelector("#facts");
    facts.replaceChildren();
    fact(facts, "Created", p.created);
    fact(facts, "Last worked on", p.last_worked);
    const places = document.querySelector("#places");
    places.replaceChildren(...p.repos.map(r => place(r, /^https?:\/\//.test(r) ? r : null)), ...p.dirs.map(d => place(d)));
    document.querySelector("#where").hidden = !(p.repos.length || p.dirs.length);
    const sets = document.querySelector("#sets");
    sets.replaceChildren(...(p.sets.length ? p.sets.map(setCard) : [node("p", "No question sets yet.")]));
    report("");
  } catch (e) {
    document.querySelector("#name").textContent = "Project not found";
    report(e.message);
  }
}

load();
setInterval(load, 15000);
