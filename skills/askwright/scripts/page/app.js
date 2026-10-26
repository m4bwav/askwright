// askwright page: one question per screen. Fixed code; the agent only writes questions.json.
// Answers live only in the set folder (answers.json): every change is posted at once and nothing is kept in the browser.
"use strict";
(() => {
  const TOKEN = document.querySelector('meta[name="ask-token"]').content;
  const $ = (sel, el = document) => el.querySelector(sel);
  const main = $("#main");
  const STATE_TEXT = { unanswered: "Not answered", answered: "Answered", unsure: "Not sure", note_only: "Note only, needs a choice" };
  const S = {
    set: null, questions: [], answers: {}, view: "question", current: null, history: [],
    showAnswered: false, editing: {}, dirty: new Set(), timers: {}, sig: "", leftPrompt: null,
    lookTimes: [], lookIdx: -1, keyInputs: [], tcOffer: null, firstLoad: true, serverTime: null,
    mediaIndex: {}, backgroundOpen: {},
  };

  // ------------------------------------------------------------ small helpers
  function h(tag, props, ...kids) {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(props || {})) {
      if (v == null || v === false) continue;
      if (k === "class") el.className = v;
      else if (k === "text") el.textContent = v;
      else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
      else if (v === true) el.setAttribute(k, "");
      else el.setAttribute(k, v);
    }
    for (const kid of kids.flat(3)) if (kid != null && kid !== false) el.append(kid.nodeType ? kid : String(kid));
    return el;
  }
  const byId = (id) => S.questions.find((q) => q.id === id);
  const isOpen = (q) => (q.status || "open") === "open";
  const fmtT = (t) => (Math.round(t * 10) / 10).toFixed(1) + " s";
  const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);

  async function api(path, opts = {}) {
    const headers = Object.assign({ "X-Ask-Token": TOKEN }, opts.headers || {});
    let r;
    try {
      r = await fetch(path, Object.assign({}, opts, { headers }));
    } catch (e) {
      throw new Error("the askwright server is not answering");
    }
    let d;
    try { d = await r.json(); } catch (e) { d = { ok: false, error: "HTTP " + r.status }; }
    if (!r.ok || !d.ok) throw new Error(d.error || "HTTP " + r.status);
    return d;
  }

  // ------------------------------------------------------------ state (mirrors ask.py answer_state and visibility)
  function stateOf(q, a) {
    if (!a) return "unanswered";
    if (a.choice === "unsure") return "unsure";
    if (q.kind === "text") { if ((a.text || "").trim()) return "answered"; }
    else if (q.kind === "multi") { if ((a.choices || []).length) return "answered"; }
    else if (q.kind === "rank") { if ((a.order || []).length) return "answered"; }
    else if (a.choice) return "answered";
    if ((a.note || "").trim() || (a.attachments || []).length) return "note_only";
    return "unanswered";
  }
  const st = (q) => stateOf(q, S.answers[q.id]);
  const done = (q) => ["answered", "unsure"].includes(st(q));
  function vis(q) {
    const si = q.show_if;
    if (!si) return "shown";
    const t = byId(si.question);
    const want = [].concat(si.option || []);
    const a = S.answers[si.question];
    if (!t || stateOf(t, a) !== "answered") return "waiting";
    const picked = (a.choices || []).length ? a.choices : [a.choice];
    return picked.some((p) => want.includes(p)) ? "shown" : "not_applicable";
  }
  const shown = () => S.questions.filter((q) => isOpen(q) && vis(q) === "shown");
  const inLine = (q) => !done(q) || q.id === S.current || S.showAnswered;
  const draft = (qid) => (S.answers[qid] = S.answers[qid] || {});

  function optLabel(q, oid) {
    if (oid === "unsure") return "Not sure, ask me later";
    if (oid === "other") return "Something else";
    const o = (q.options || []).find((x) => x.id === oid);
    return o ? o.label : oid;
  }
  function sideOf(q, oid) {
    const s = q.sides || {};
    return Object.keys(s).find((k) => k !== "randomized" && s[k] === oid) || null;
  }
  // Compare takes show their side ("Left") until a pick is made, then "Left (Take 2)": a blind pick, stored by id.
  function shownLabel(q, oid, reveal) {
    const side = sideOf(q, oid);
    if (!side) return optLabel(q, oid);
    return reveal ? cap(side) + " (" + optLabel(q, oid) + ")" : cap(side);
  }
  function answerText(q) {
    const a = S.answers[q.id] || {};
    const s = st(q);
    if (s === "unanswered") return "Not answered";
    if (s === "unsure") return "Not sure, ask me later";
    let t = "";
    if (s === "answered") {
      if (q.kind === "multi") t = a.choices.map((c) => shownLabel(q, c, true)).join(", ");
      else if (q.kind === "rank") t = a.order.map((c, i) => i + 1 + ". " + optLabel(q, c)).join("  ");
      else if (q.kind === "text") t = '"' + a.text.trim() + '"';
      else t = shownLabel(q, a.choice, true);
    } else t = "Note only, needs a choice";
    if ((a.note || "").trim()) t += " · note: " + a.note.trim().slice(0, 120);
    if ((a.attachments || []).length) t += " · " + a.attachments.length + " image(s)";
    return t;
  }

  // ------------------------------------------------------------ loading and polling
  async function load() {
    const d = await api("/api/set");
    const sig = d.questions.map((q) => q.id + ":" + (q.status || "open") + ":" + (q.rev || 1)).join("|");
    const before = new Set(S.questions.filter(isOpen).map((q) => q.id));
    const changed = S.sig && sig !== S.sig;
    S.sig = sig;
    S.set = d.set;
    S.serverTime = Date.parse(d.server_time);
    S.questions = d.questions;
    for (const [qid, a] of Object.entries(d.answers || {})) if (!S.dirty.has(qid)) S.answers[qid] = a;
    if (d.note) showBanner(d.note);
    $("#set-title").textContent = d.set.title || "Questions for you";
    document.title = (d.set.title || "Questions") + " · askwright";
    if (S.firstLoad) {
      S.firstLoad = false;
      welcome(d);
      const first = shown().find((q) => !done(q));
      if (first) { S.current = first.id; S.view = "question"; S.editing[first.id] = true; }
      else S.view = "finish";
      api("/api/event", post({ type: "visit" })).catch(() => {});
      render(false);
      return;
    }
    if (changed) {
      const now = new Set(S.questions.filter(isOpen).map((q) => q.id));
      const added = [...now].filter((x) => !before.has(x)).length;
      const closed = [...before].filter((x) => !now.has(x)).length;
      const parts = [];
      if (added) parts.push(added + (added === 1 ? " question was" : " questions were") + " added");
      if (closed) parts.push(closed + (closed === 1 ? " question was" : " questions were") + " closed");
      showNotice((parts.join(" and ") || "The questions were updated") + " while you were here.");
      const cur = S.current && byId(S.current);
      if (S.view === "question" && (!cur || !isOpen(cur))) { S.current = null; goNext(); return; }
      if (!typing()) render(false);
    } else topbar();
  }
  function post(obj) {
    return { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(obj) };
  }
  function ago(iso) {
    const s = Math.max(0, ((S.serverTime || Date.now()) - Date.parse(iso)) / 1000);
    if (s < 90) return "a minute ago";
    if (s < 5400) return Math.round(s / 60) + " min ago";
    if (s < 129600) return Math.round(s / 3600) + " h ago";
    return Math.round(s / 86400) + " days ago";
  }
  function welcome(d) {
    if (!d.last_visit) return;
    const left = shown().filter((q) => !done(q));
    let t = "Welcome back.";
    if (d.last_answer) {
      const q = byId(d.last_answer.q);
      t += " Last answer " + ago(d.last_answer.t) + (q ? " (" + q.title + ")" : "") + ".";
    }
    const names = left.slice(0, 5).map((q) => q.title).join(", ") + (left.length > 5 ? " and " + (left.length - 5) + " more" : "");
    t += left.length
      ? " " + left.length + " left: " + names + "."
      : " Every question is answered; check them below.";
    showNotice(t);
  }

  // ------------------------------------------------------------ saving
  function setSave(text, bad) {
    const el = $("#save-status");
    el.textContent = text;
    el.classList.toggle("bad", !!bad);
  }
  function changed(qid, now) {
    S.dirty.add(qid);
    clearTimeout(S.timers[qid]);
    setSave("Saving…");
    S.timers[qid] = setTimeout(() => save(qid), now ? 0 : 600);
  }
  function body(qid) {
    const q = byId(qid);
    const a = S.answers[qid] || {};
    return {
      qid, q_rev: q.rev || 1,
      choice: a.choice || null,
      choices: q.kind === "multi" ? a.choices || [] : null,
      order: q.kind === "rank" && (a.order || []).length ? a.order : null,
      text: q.kind === "text" ? a.text || "" : null,
      note: a.note || "", attachments: a.attachments || [], timecodes: a.timecodes || [],
      guess_revealed: !!a.guess_revealed, guess_revealed_before_pick: !!a.guess_revealed_before_pick,
    };
  }
  async function save(qid) {
    clearTimeout(S.timers[qid]);
    if (!S.dirty.has(qid)) return true;
    const sent = JSON.stringify(body(qid));
    try {
      const d = await api("/api/answer", { method: "POST", headers: { "Content-Type": "application/json" }, body: sent });
      if (JSON.stringify(body(qid)) === sent) {
        S.dirty.delete(qid);
        S.answers[qid] = Object.assign(S.answers[qid] || {}, { state: d.answer.state, rev: d.answer.rev });
      }
      const t = new Date();
      setSave("Saved " + String(t.getHours()).padStart(2, "0") + ":" + String(t.getMinutes()).padStart(2, "0"));
      hideBanner();
      topbar();
      return true;
    } catch (e) {
      setSave("Not saved", true);
      const q = byId(qid);
      showBanner("Your answer to \"" + (q ? q.title : qid) + "\" is not saved: " + e.message +
        ". Keep this tab open, ask the agent to start the server again (ask.py serve), then press Retry.", () => flush());
      return false;
    }
  }
  async function flush() {
    let ok = true;
    for (const qid of [...S.dirty]) ok = (await save(qid)) && ok;
    return ok;
  }
  window.addEventListener("pagehide", () => {
    for (const qid of S.dirty) {
      fetch("/api/answer", { method: "POST", keepalive: true, body: JSON.stringify(body(qid)),
        headers: { "Content-Type": "application/json", "X-Ask-Token": TOKEN } });
    }
  });
  window.addEventListener("beforeunload", (e) => { if (S.dirty.size) e.preventDefault(); });

  function showBanner(text, retry) {
    const b = $("#banner");
    b.replaceChildren(text, retry ? h("button", { type: "button", class: "btn small", onclick: retry, text: "Retry" }) : "");
    b.hidden = false;
  }
  function hideBanner() { $("#banner").hidden = true; }
  function showNotice(text) {
    const n = $("#notice");
    n.replaceChildren(text, h("button", { type: "button", class: "btn small", text: "Dismiss", onclick: () => { n.hidden = true; } }));
    n.hidden = false;
  }

  // ------------------------------------------------------------ navigation
  function goTo(qid, push = true) {
    if (push && S.view === "question" && S.current && S.current !== qid) S.history.push(S.current);
    if (push && S.view !== "question" && S.current) S.history.push(S.current);
    S.current = qid;
    S.view = "question";
    const q = byId(qid);
    S.editing[qid] = !done(q);
    render(true);
  }
  function nextQ() {
    const list = shown();
    const i = list.findIndex((q) => q.id === S.current);
    const after = list.slice(i + 1).concat(list.slice(0, Math.max(i, 0)));
    return after.find((q) => q.id !== S.current && (S.showAnswered || !done(q))) || null;
  }
  function goNext() {
    const n = nextQ();
    if (n) goTo(n.id);
    else { if (S.current) S.history.push(S.current); S.view = "finish"; render(true); }
  }
  function goBack() {
    while (S.history.length) {
      const id = S.history.pop();
      const q = byId(id);
      if (q && isOpen(q) && vis(q) === "shown" && id !== S.current) return goTo(id, false);
    }
    if (S.view !== "question" && S.current) return goTo(S.current, false);
    const list = shown();
    const i = list.findIndex((q) => q.id === S.current);
    if (i > 0) goTo(list[i - 1].id, false);
  }
  // Leaving a question with a note but no pick asks once; going on stores it as note_only, never as a choice.
  async function leave(then) {
    const q = S.view === "question" && byId(S.current);
    if (q && q.kind !== "text" && st(q) === "note_only" && S.leftPrompt !== q.id) {
      S.leftPrompt = q.id;
      return showLeavePrompt(q, then);
    }
    S.leftPrompt = null;
    stopMedia();
    await flush();
    then();
  }
  function showLeavePrompt(q, then) {
    const box = $("#leave-prompt");
    const keep = h("button", { type: "button", class: "btn", text: "Keep it as 'Something else'", onclick: () => {
      if (q.kind === "multi") draft(q.id).choices = ["other"]; else draft(q.id).choice = "other";
      changed(q.id, true);
      leave(then);
    } });
    const go = h("button", { type: "button", class: "btn", text: "Go on without picking", onclick: () => leave(then) });
    box.replaceChildren(h("div", { class: "prompt", role: "alert" },
      h("p", { text: "You wrote a note but did not pick an option. Pick one above, or keep the note as 'Something else'." }),
      h("div", { class: "row" }, keep, go)));
    keep.focus();
  }
  function stopMedia() { main.querySelectorAll("video, audio").forEach((m) => m.pause()); }

  // ------------------------------------------------------------ render
  function topbar() {
    const list = shown();
    const answered = list.filter(done).length;
    const left = list.length - answered;
    const i = list.findIndex((q) => q.id === S.current);
    const pos = S.view === "question" && i >= 0 ? "Question " + (i + 1) + " of " + list.length + " · " : "";
    $("#progress").textContent = pos + answered + " answered · " + left + " left";
    const ba = $("#btn-answered");
    ba.hidden = answered === 0;
    ba.textContent = (S.showAnswered ? "Hide answered (" : "Show answered (") + answered + ")";
    ba.setAttribute("aria-pressed", String(S.showAnswered));
    const back = $("#btn-back");
    const next = $("#btn-next");
    back.disabled = S.view === "question" && !S.history.length && i <= 0;
    if (S.view === "question") {
      const n = nextQ();
      next.textContent = n ? "Next: " + n.title : "Check answers";
      next.disabled = false;
    } else if (S.view === "overview") {
      next.textContent = "Check answers";
      next.disabled = false;
    } else {
      next.textContent = "Next";
      next.disabled = true;
    }
  }
  function render(focus) {
    S.keyInputs = [];
    S.lookTimes = [];
    S.lookIdx = -1;
    S.tcOffer = null;
    if (S.view === "overview") renderOverview();
    else if (S.view === "finish") renderFinish();
    else renderQuestion(byId(S.current));
    topbar();
    if (focus) { const h1 = $("h1", main); (h1 || main).focus(); window.scrollTo(0, 0); }
  }

  function mediaEl(m, primary) {
    if (m.missing) return h("p", { class: "missing", text: "Missing file: " + m.missing });
    let el;
    if (m.type === "video") {
      el = h("video", { controls: true, preload: "metadata", playsinline: true, src: m.url, "aria-label": m.label || m.alt || "Video" },
        m.captions_url ? h("track", { kind: "captions", src: m.captions_url, srclang: "en", label: "Captions", default: true }) : null);
      if (m.start) el.addEventListener("loadedmetadata", () => { if (el.currentTime === 0) el.currentTime = m.start; }, { once: true });
    } else if (m.type === "audio") {
      el = h("audio", { controls: true, preload: "metadata", src: m.url, "aria-label": m.label || m.alt || "Audio" });
    } else {
      el = h("img", { src: m.url, alt: m.alt || "", loading: "lazy" });
    }
    if (primary) el.dataset.primary = "1";
    const capt = m.caption || (m.type !== "image" && m.label);
    return h("figure", null, el, capt ? h("figcaption", { text: capt }) : null);
  }

  function questionMedia(q) {
    const items = q.media || [];
    const imagesOnly = items.every((m) => m.type === "image");
    const gallery = imagesOnly && items.length > 1 &&
      (q.media_layout === "gallery" || (!q.media_layout || q.media_layout === "auto") && items.length >= 3);
    if (!gallery) return h("div", { class: "media" }, items.map((m, i) => mediaEl(m, i === 0)),
      items.length === 1 && imagesOnly && items[0].url && !items[0].missing
        ? h("a", { class: "link", href: items[0].url, target: "_blank", rel: "noopener noreferrer",
          text: "Open full-size image" }) : null);
    const region = h("section", { class: "media gallery", tabindex: "0", role: "region",
      "aria-roledescription": "carousel", "aria-label": "Review cases" });
    const slide = h("div", { class: "gallery-slide", role: "group", "aria-roledescription": "slide" });
    const count = h("p", { class: "gallery-count", role: "status", "aria-live": "polite", "aria-atomic": "true" });
    const select = h("select", { id: "gallery-case", class: "gallery-select",
      "aria-label": "Go to case", onchange: () => show(+select.value) },
      items.map((m, i) => h("option", { value: i, text: "Case " + (i + 1) +
        (m.label || m.caption ? ": " + (m.label || m.caption).replace(/^case\s+\d+\s*:\s*/i, "").slice(0, 90) : "") })));
    const previous = h("button", { type: "button", class: "btn", text: "Previous case",
      onclick: () => show(S.mediaIndex[q.id] - 1) });
    const next = h("button", { type: "button", class: "btn", text: "Next case",
      onclick: () => show(S.mediaIndex[q.id] + 1) });
    const original = h("a", { class: "link", target: "_blank", rel: "noopener noreferrer",
      text: "Open full-size image" });
    function show(index) {
      const focused = document.activeElement;
      index = Math.max(0, Math.min(index, items.length - 1));
      S.mediaIndex[q.id] = index;
      slide.replaceChildren(mediaEl(items[index], true));
      slide.setAttribute("aria-label", "Case " + (index + 1) + " of " + items.length);
      count.textContent = "Case " + (index + 1) + " of " + items.length;
      select.value = String(index);
      previous.disabled = index === 0;
      next.disabled = index === items.length - 1;
      if (focused === previous && previous.disabled || focused === next && next.disabled) {
        region.focus({ preventScroll: true });
      }
      original.hidden = !items[index].url || !!items[index].missing;
      if (!original.hidden) original.href = items[index].url;
    }
    region.addEventListener("keydown", (e) => {
      if (e.ctrlKey || e.metaKey || e.altKey || e.target.tagName === "SELECT") return;
      if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
      e.preventDefault();
      e.stopPropagation();
      show(S.mediaIndex[q.id] + (e.key === "ArrowRight" ? 1 : -1));
    });
    region.append(h("div", { class: "gallery-controls" }, previous, select, next),
      count, slide, original);
    show(S.mediaIndex[q.id] || 0);
    return region;
  }

  function inlineMd(text) {
    const out = [];
    const re = /(\*\*([^*]+)\*\*|\*([^*]+)\*|`([^`]+)`|\[([^\]]+)\]\((https?:\/\/[^)\s]+)\))/g;
    let last = 0, m;
    while ((m = re.exec(text))) {
      out.push(text.slice(last, m.index));
      if (m[2]) out.push(h("strong", { text: m[2] }));
      else if (m[3]) out.push(h("em", { text: m[3] }));
      else if (m[4]) out.push(h("code", { text: m[4] }));
      else out.push(h("a", { href: m[6], target: "_blank", rel: "noopener noreferrer", text: m[5] }));
      last = re.lastIndex;
    }
    out.push(text.slice(last));
    return out;
  }
  function md(text) {
    const out = [];
    for (const block of String(text || "").split(/\n\s*\n/)) {
      const lines = block.split("\n").filter((l) => l.trim());
      if (!lines.length) continue;
      if (lines.every((l) => /^\s*[-*] /.test(l))) out.push(h("ul", null, lines.map((l) => h("li", null, inlineMd(l.replace(/^\s*[-*] /, ""))))));
      else if (lines.every((l) => /^\s*\d+\. /.test(l))) out.push(h("ol", null, lines.map((l) => h("li", null, inlineMd(l.replace(/^\s*\d+\. /, ""))))));
      else if (/^#{1,3} /.test(lines[0]) && lines.length === 1) out.push(h("h3", null, inlineMd(lines[0].replace(/^#+ /, ""))));
      else out.push(h("p", null, inlineMd(lines.join(" "))));
    }
    return out;
  }
  function table(cols, rows, caption) {
    return h("table", null, caption ? h("caption", { text: caption }) : null,
      h("thead", null, h("tr", null, cols.map((c) => h("th", { scope: "col", text: c })))),
      h("tbody", null, (rows || []).map((r) => h("tr", null, r.map((c) => h("td", { text: c == null ? "" : String(c) }))))));
  }
  function onePager(blocks, qid) {
    const kids = blocks.map((b) => {
      switch (b.type) {
        case "text": return h("div", null, md(b.text));
        case "image": case "chart": return mediaEl(Object.assign({}, b, { type: "image" }));
        case "video": case "audio": return mediaEl(b);
        case "table": return table(b.columns || [], b.rows, b.caption);
        case "options_compared": return table(["Option", "For", "Against", "What happens"],
          (b.rows || []).map((r) => [r.option, r.pros, r.cons, r.consequence]), b.caption);
        case "facts": return h("dl", { class: "facts" }, (b.items || []).map((f) => [h("dt", { text: f.label }), h("dd", { text: f.value })]));
        default: return null;
      }
    });
    return h("details", { class: "onepager", open: !!S.backgroundOpen[qid],
      ontoggle: (e) => { S.backgroundOpen[qid] = e.currentTarget.open; } },
      h("summary", { text: "Background for this question" }), kids);
  }

  function renderQuestion(q) {
    if (!q) { S.view = "finish"; return renderFinish(); }
    const a = S.answers[q.id] || {};
    const editing = !!S.editing[q.id];
    const art = h("article", { class: "q", "data-q": q.id });
    if ((q.one_pager || []).length) art.append(onePager(q.one_pager, q.id));
    art.append(h("p", { class: "caption", text: q.title + (q.reversible === false ? " · hard to undo" : "") }),
      h("h1", { tabindex: "-1", id: "q-h" }, q.question));
    if (q.hint) art.append(h("p", { class: "hint", text: q.hint }));
    art.append(h("section", { class: "why", "aria-labelledby": "why-h" }, h("h2", { id: "why-h", text: "Why this matters" }), h("p", { text: q.why })));
    if ((q.look_for || []).length) {
      const items = q.look_for.map((t) => {
        const times = [...t.matchAll(/(\d+(?:\.\d+)?)\s*s\b/g)].map((m) => parseFloat(m[1]));
        S.lookTimes.push(...times);
        return h("li", null, t, times.map((x) => h("button", { type: "button", class: "btn small", text: "Play from " + fmtT(x), onclick: () => seek(x, true) })));
      });
      art.append(h("section", { class: "look", "aria-labelledby": "look-h" }, h("h2", { id: "look-h", text: "What to look for" }), h("ul", null, items)));
      S.lookTimes.sort((x, y) => x - y);
    }
    if ((q.media || []).length) art.append(questionMedia(q));
    if (!editing) {
      art.append(h("div", { class: "readonly" }, h("span", { text: "You answered: " + answerText(q) }),
        h("button", { type: "button", class: "btn small", text: "Change", onclick: () => { S.editing[q.id] = true; render(false); $("#ans input, #ans textarea, #ans button", main)?.focus(); } })));
    }
    art.append(answerArea(q, a, editing));
    art.append(guessArea(q, a));
    art.append(noteArea(q, a, editing));
    art.append(h("div", { id: "leave-prompt" }));
    main.replaceChildren(art);
  }

  function optRow(type, name, value, label, sub, checked, n, extra) {
    const input = h("input", { type, name, value, checked });
    if (n <= 9) S.keyInputs.push(input);
    return h("label", { class: "opt" + (extra ? " extra" : ""), "data-oid": value },
      input, h("span", { class: "key", "aria-hidden": "true", text: n <= 9 ? String(n) : "" }),
      h("span", { class: "txt" }, h("span", { class: "label", text: label }), sub ? h("span", { class: "cons", text: sub }) : null));
  }

  function answerArea(q, a, editing) {
    const fs = h("fieldset", { id: "ans", disabled: !editing }, h("legend", { text: q.kind === "rank" ? "Your order" : q.kind === "multi" ? "Your answer (pick any)" : "Your answer" }));
    const name = "ans-" + q.id;
    let n = 1;
    if (q.kind === "rank") {
      const order = (a.order && a.order.length ? a.order : q.options.map((o) => o.id)).slice();
      const ol = h("ol", { class: "rank" });
      const draw = () => ol.replaceChildren(...order.map((oid, i) => h("li", null,
        h("span", { class: "pos", text: i + 1 + "." }), h("span", { class: "label", text: optLabel(q, oid) }),
        h("button", { type: "button", class: "btn small", "aria-label": "Move " + optLabel(q, oid) + " up", disabled: i === 0, text: "Up", onclick: () => move(i, -1) }),
        h("button", { type: "button", class: "btn small", "aria-label": "Move " + optLabel(q, oid) + " down", disabled: i === order.length - 1, text: "Down", onclick: () => move(i, 1) }))));
      const move = (i, d) => {
        [order[i], order[i + d]] = [order[i + d], order[i]];
        draw();
        if ((draft(q.id).order || []).length) { draft(q.id).order = order.slice(); changed(q.id, true); }
        ol.querySelectorAll("li")[i + d].querySelector(d < 0 ? "button" : "button:last-child").focus();
      };
      draw();
      const useBtn = h("button", { type: "button", class: "btn primary", text: (a.order || []).length ? "Order saved" : "Use this order", onclick: () => {
        const d = draft(q.id); d.order = order.slice(); if (d.choice === "unsure") d.choice = null;
        useBtn.textContent = "Order saved"; unsure.checked = false; picked(q); changed(q.id, true);
      } });
      const unsure = h("input", { type: "checkbox", value: "unsure", checked: a.choice === "unsure" });
      unsure.addEventListener("change", () => { const d = draft(q.id); d.choice = unsure.checked ? "unsure" : null; if (unsure.checked) { d.order = []; useBtn.textContent = "Use this order"; } picked(q); changed(q.id, true); });
      fs.append(ol, h("div", { class: "rank-actions" }, useBtn, h("label", { class: "opt extra" }, unsure, h("span", { class: "label", text: "Not sure, ask me later" }))));
      return fs;
    }
    if (q.kind === "text") {
      const ta = h("textarea", { id: "ans-text", rows: "4" });
      ta.value = a.text || "";
      ta.addEventListener("input", () => { const d = draft(q.id); d.text = ta.value; if (ta.value.trim() && d.choice === "unsure") { d.choice = null; unsure.checked = false; } changed(q.id); });
      const unsure = h("input", { type: "checkbox", value: "unsure", checked: a.choice === "unsure" });
      unsure.addEventListener("change", () => { draft(q.id).choice = unsure.checked ? "unsure" : null; changed(q.id, true); });
      fs.append(h("div", { class: "answer-text" }, h("label", { for: "ans-text", class: "visually-hidden", text: "Your answer" }), ta),
        h("div", { class: "opts" }, h("label", { class: "opt extra" }, unsure, h("span", { class: "label", text: "Not sure, ask me later" }))));
      return fs;
    }
    const multi = q.kind === "multi";
    const reveal = done(q);
    const box = h("div", { class: "opts" + (q.kind === "scale" ? " scale" : "") });
    const chosen = multi ? a.choices || [] : [a.choice];
    for (const o of q.options) {
      const row = optRow(multi ? "checkbox" : "radio", name, o.id, shownLabel(q, o.id, reveal), o.consequence, chosen.includes(o.id), n++);
      if ((o.media || []).length) row.querySelector(".txt").append(...o.media.map((m) => mediaEl(m)));
      box.append(row);
    }
    if (q.kind !== "scale") box.append(h("hr", { class: "sep" }));
    box.append(optRow(multi ? "checkbox" : "radio", name, "unsure", "Not sure, ask me later", null, a.choice === "unsure", n++, true));
    box.append(optRow(multi ? "checkbox" : "radio", name, "other", "Something else", "Say what in the note below", chosen.includes("other"), n++, true));
    box.addEventListener("change", (e) => {
      const v = e.target.value;
      const d = draft(q.id);
      if (multi) {
        if (v === "unsure") { d.choice = e.target.checked ? "unsure" : null; if (e.target.checked) d.choices = []; }
        else { d.choices = [...box.querySelectorAll("input:checked")].map((i) => i.value).filter((x) => x !== "unsure"); if (d.choices.length) d.choice = null; }
        box.querySelectorAll("input").forEach((i) => { i.checked = v === "unsure" ? (i.value === "unsure" && !!d.choice) : (i.value === "unsure" ? false : (d.choices || []).includes(i.value)); });
      } else d.choice = v;
      picked(q);
      changed(q.id, true);
      if (v === "other" && e.target.checked && !(d.note || "").trim()) $("#note", main)?.focus();
    });
    fs.append(box);
    return fs;
  }
  // After a pick: reveal compare sides and refresh the guess line, without re-rendering (a playing video keeps playing).
  function picked(q) {
    const reveal = done(q);
    main.querySelectorAll(".opt[data-oid]").forEach((row) => {
      const oid = row.dataset.oid;
      if (oid !== "unsure" && oid !== "other") row.querySelector(".label").textContent = shownLabel(q, oid, reveal);
    });
    const g = $("#guess-line", main);
    if (g) g.replaceWith(guessLine(q));
    topbar();
  }

  function guessText(q) {
    const g = q.guess || {};
    if (q.kind === "multi") return (g.options || []).map((o) => shownLabel(q, o, done(q))).join(", ");
    if (q.kind === "rank") return (g.order || []).map((o, i) => i + 1 + ". " + optLabel(q, o)).join("  ");
    if (q.kind === "text") return '"' + (g.text || "") + '"';
    return shownLabel(q, g.option, done(q));
  }
  function guessLine(q) {
    const g = q.guess || {};
    return h("p", { id: "guess-line" }, h("strong", { text: "My guess: " }), guessText(q) + ". ", g.why || "");
  }
  function guessArea(q, a) {
    const g = q.guess;
    if (!g) return h("div");
    const wrap = h("div", { class: "guess" });
    if (g.confidence === "high" || a.guess_revealed) wrap.append(guessLine(q));
    else {
      const btn = h("button", { type: "button", class: "btn small", text: "Show my guess", onclick: () => {
        const d = draft(q.id);
        d.guess_revealed = true;
        if (!done(q)) d.guess_revealed_before_pick = true;
        changed(q.id, true);
        wrap.replaceChildren(guessLine(q));
      } });
      wrap.append(h("p", null, "I am not sure about this one, so my guess is hidden until you want it. ", btn));
    }
    return wrap;
  }

  function noteArea(q, a, editing) {
    const wrap = h("div", { class: "note" });
    const ta = h("textarea", { id: "note", rows: "3", disabled: !editing });
    ta.value = a.note || "";
    const offer = h("div", { class: "note-tools", hidden: true });
    const chips = h("ul", { class: "chips", "aria-label": "Times this note refers to" });
    const atts = h("div", { class: "atts" });
    const file = h("input", { type: "file", accept: "image/png,image/jpeg,image/gif,image/webp", multiple: true, class: "visually-hidden", tabindex: "-1", "aria-hidden": "true" });
    const add = h("button", { type: "button", class: "btn small", text: "Add image", disabled: !editing, onclick: () => file.click() });
    file.addEventListener("change", () => { upload(q, [...file.files]); file.value = ""; });
    const drawChips = () => chips.replaceChildren(...(draft(q.id).timecodes || []).map((tc, i) => h("li", null,
      h("button", { type: "button", class: "link", text: "at " + fmtT(tc.t), onclick: () => seek(tc.t, false) }),
      h("button", { type: "button", class: "link", "aria-label": "Remove the time " + fmtT(tc.t), text: "×", disabled: !editing,
        onclick: () => { draft(q.id).timecodes.splice(i, 1); changed(q.id, true); drawChips(); } }))));
    const drawAtts = () => atts.replaceChildren(...(draft(q.id).attachments || []).map((p, i) => h("figure", null,
      h("img", { src: "/m/0/" + p.split("/").map(encodeURIComponent).join("/"), alt: "Attached image " + (i + 1) }),
      h("button", { type: "button", class: "btn small", text: "Remove", "aria-label": "Remove attached image " + (i + 1), disabled: !editing,
        onclick: () => { draft(q.id).attachments.splice(i, 1); changed(q.id, true); drawAtts(); } }))));
    S.drawAtts = drawAtts;
    ta.addEventListener("input", () => { draft(q.id).note = ta.value; changed(q.id); });
    ta.addEventListener("keydown", (e) => {
      if (e.key === "Escape") { ta.blur(); return; }
      if (e.key.length !== 1 || e.ctrlKey || e.metaKey || e.altKey) return;
      const v = playing();
      if (v) {
        v.pause();
        const t = v.currentTime;
        offer.replaceChildren(h("button", { type: "button", class: "btn small", text: "Tie this note to " + fmtT(t), onclick: () => {
          const d = draft(q.id);
          d.timecodes = (d.timecodes || []).concat([{ t: Math.round(t * 100) / 100 }]);
          changed(q.id, true); drawChips(); offer.hidden = true; ta.focus();
        } }), h("span", { class: "hint", text: "The video paused while you write." }));
        offer.hidden = false;
      }
    });
    wrap.addEventListener("dragover", (e) => { if (editing) { e.preventDefault(); wrap.classList.add("drag"); } });
    wrap.addEventListener("dragleave", () => wrap.classList.remove("drag"));
    wrap.addEventListener("drop", (e) => {
      wrap.classList.remove("drag");
      const files = [...(e.dataTransfer?.files || [])].filter((f) => f.type.startsWith("image/"));
      if (files.length && editing) { e.preventDefault(); upload(q, files); }
    });
    drawChips();
    drawAtts();
    wrap.append(h("label", { for: "note", class: "lbl" }, "Note ", h("span", { class: "hint", text: "(optional; paste or drop images here)" })),
      ta, offer, chips, h("div", { class: "note-tools" }, add, file), atts);
    return wrap;
  }
  async function upload(q, files) {
    for (const f of files) {
      setSave("Uploading image…");
      try {
        const d = await api("/api/attachment", { method: "POST", headers: { "Content-Type": f.type || "application/octet-stream", "X-Ask-Qid": q.id }, body: f });
        const a = draft(q.id);
        a.attachments = (a.attachments || []).concat([d.path]);
        changed(q.id, true);
        if (S.current === q.id && S.drawAtts) S.drawAtts();
      } catch (e) {
        setSave("Image not saved", true);
        showBanner("The image was not saved: " + e.message + ".");
      }
    }
  }
  document.addEventListener("paste", (e) => {
    if (S.view !== "question" || !S.editing[S.current]) return;
    const items = [...(e.clipboardData?.items || [])].filter((i) => i.kind === "file" && i.type.startsWith("image/"));
    const files = items.map((i) => i.getAsFile()).filter(Boolean);
    if (!files.length) return;
    e.preventDefault();
    upload(byId(S.current), files);
  });

  // ------------------------------------------------------------ media keys
  const mediaList = () => [...main.querySelectorAll(".media video, .media audio")];
  const playing = () => mediaList().find((m) => !m.paused);
  function primary() { return mediaList()[0] || null; }
  function seek(t, play) {
    const m = primary();
    if (!m) return;
    m.currentTime = t;
    if (play) m.play().catch(() => {});
  }

  // ------------------------------------------------------------ overview and finish
  function renderOverview() {
    const list = S.questions.filter(isOpen);
    const rows = list.map((q) => {
      const v = vis(q);
      if (v === "not_applicable") return null;
      if (v === "waiting") {
        const t = byId(q.show_if.question);
        return h("li", null, h("span", { text: q.title }), h("span", { class: "tag", text: "Shows if you pick " + [].concat(q.show_if.option).map((o) => optLabel(t, o)).join(" or ") + " in " + t.title }));
      }
      const s = st(q);
      return h("li", null, h("a", { href: "#", onclick: (e) => { e.preventDefault(); leave(() => goTo(q.id)); }, text: q.title }), h("span", { class: "tag " + s, text: STATE_TEXT[s] }));
    });
    main.replaceChildren(h("h1", { tabindex: "-1", text: "All questions" }),
      h("p", { text: "Pick any question to go to it. Answered questions open read-only until you press Change." }),
      h("ol", { class: "tasks" }, rows),
      h("button", { type: "button", class: "btn", text: "Back to the question", onclick: () => (S.current ? goTo(S.current, false) : goNext()) }));
  }
  function renderFinish() {
    const list = shown();
    const counts = { answered: 0, unsure: 0, note_only: 0, unanswered: 0 };
    list.forEach((q) => counts[st(q)]++);
    const lead = [counts.answered + " answered"];
    if (counts.unsure) lead.push(counts.unsure + " not sure");
    if (counts.note_only) lead.push(counts.note_only + " with a note but no choice");
    if (counts.unanswered) lead.push(counts.unanswered + " not answered");
    const msg = h("p", { class: "done-msg", role: "status" });
    const finish = (type) => async () => {
      await flush();
      try {
        await api("/api/event", post({ type }));
        msg.textContent = type === "done"
          ? "Thank you. Your answers are saved; the agent can read them now. You can close this tab."
          : "Saved. Come back to this page any time; it opens where you left off.";
      } catch (e) { showBanner("Could not record that: " + e.message + "."); }
    };
    main.replaceChildren(h("h1", { tabindex: "-1", text: "Check your answers" }),
      h("p", { text: lead.join(", ") + "." }),
      h("dl", { class: "check" }, list.map((q) => h("div", null, h("dt", { text: q.title }), h("dd", { text: answerText(q) }),
        h("dd", null, h("a", { href: "#", onclick: (e) => { e.preventDefault(); goTo(q.id); }, text: done(q) ? "Change" : "Answer", "aria-label": (done(q) ? "Change " : "Answer ") + q.title }))))),
      counts.unanswered + counts.note_only
        ? h("p", { class: "hint", text: "Questions without a choice reach the agent as not answered; it will not guess for you." })
        : null,
      h("div", { class: "finish-actions" },
        h("button", { type: "button", class: "btn", text: "I'm done for now", onclick: finish("pause") }),
        h("button", { type: "button", class: "btn primary", text: "All done", onclick: finish("done") })),
      msg);
  }

  // ------------------------------------------------------------ controls and keys
  $("#btn-next").addEventListener("click", () => {
    if (S.view === "question") leave(goNext);
    else if (S.view === "overview") { S.view = "finish"; render(true); }
  });
  $("#btn-back").addEventListener("click", () => leave(goBack));
  $("#btn-overview").addEventListener("click", () => leave(() => { S.view = "overview"; render(true); }));
  $("#btn-answered").addEventListener("click", () => { S.showAnswered = !S.showAnswered; topbar(); if (S.view === "overview") render(false); });
  $("#btn-keys").addEventListener("click", () => $("#keys").showModal());
  $("#keys-close").addEventListener("click", () => $("#keys").close());

  function typing() {
    const el = document.activeElement;
    return !!el && (el.tagName === "TEXTAREA" || el.isContentEditable || (el.tagName === "INPUT" && !["radio", "checkbox", "button", "file"].includes(el.type)));
  }
  document.addEventListener("keydown", (e) => {
    if (e.ctrlKey || e.metaKey || e.altKey || typing() || $("#keys").open) return;
    const el = document.activeElement;
    const onControl = el && ["INPUT", "BUTTON", "VIDEO", "AUDIO", "A", "SUMMARY"].includes(el.tagName);
    const k = e.key;
    if (el?.tagName === "SELECT") return;
    if (/^[1-9]$/.test(k) && S.view === "question") {
      const input = S.keyInputs[+k - 1];
      if (input && !input.disabled) { input.click(); input.focus(); e.preventDefault(); }
    } else if (k === "n" || (k === "ArrowRight" && !onControl)) { e.preventDefault(); $("#btn-next").click(); }
    else if (k === "p" || (k === "ArrowLeft" && !onControl)) { e.preventDefault(); $("#btn-back").click(); }
    else if (k === "u" && S.view === "question") {
      const u = main.querySelector('input[value="unsure"]');
      if (u && !u.disabled) { u.click(); e.preventDefault(); }
    } else if (k === "/" && S.view === "question") { const n = $("#note", main); if (n && !n.disabled) { e.preventDefault(); n.focus(); } }
    else if (k === " " && !onControl && S.view === "question") {
      const m = primary();
      if (m) { e.preventDefault(); m.paused ? m.play().catch(() => {}) : m.pause(); }
    } else if ((k === "j" || k === "l") && S.view === "question") {
      const m = primary();
      if (m) m.currentTime = Math.max(0, m.currentTime + (k === "l" ? 1 : -1));
    } else if ((k === "[" || k === "]") && S.lookTimes.length) {
      S.lookIdx = (S.lookIdx + (k === "]" ? 1 : -1) + S.lookTimes.length) % S.lookTimes.length;
      seek(S.lookTimes[S.lookIdx], true);
    } else if (k === "o") { e.preventDefault(); $("#btn-overview").click(); }
    else if (k === "?") { e.preventDefault(); $("#keys").showModal(); }
  });

  load().catch((e) => {
    main.replaceChildren(h("h1", { tabindex: "-1", text: "The questions could not be loaded" }),
      h("p", { text: e.message + ". Ask the agent to run ask.py serve again and open the new link." }));
  });
  setInterval(() => { load().catch(() => {}); }, 20000);
  window.addEventListener("focus", () => { if (!S.firstLoad) load().catch(() => {}); });
})();
