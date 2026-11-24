"use strict";
// Paging kept in the URL query; an error line with Retry.
function askPager(key, items, redraw) {
  const q = new URLSearchParams(location.search), sizes = [25, 50, 100];
  const size = sizes.includes(+q.get(key + "-size")) ? +q.get(key + "-size") : 25;
  const pages = Math.ceil(items.length / size) || 1;
  const page = Math.min(pages, Math.max(1, Math.floor(+q.get(key + "-page")) || 1)), from = (page - 1) * size;
  const go = (p, s) => {
    q.set(key + "-page", p); q.set(key + "-size", s);
    history.replaceState(null, "", "?" + q + location.hash); redraw();
  };
  const el = (tag, text) => Object.assign(document.createElement(tag), {textContent: text || ""});
  const nav = Object.assign(el("nav"), {className: "pager", hidden: items.length <= 25});
  nav.setAttribute("aria-label", "Pages");
  const step = (label, to, off) => {
    const b = Object.assign(el("button", label), {type: "button", disabled: off});
    b.dataset.focus = `${key}:${label}`;
    b.onclick = () => go(to, size);
    return b;
  };
  const pick = el("select");
  pick.setAttribute("aria-label", "Rows per page");
  pick.dataset.focus = `${key}:size`;
  for (const n of sizes) pick.add(new Option(`${n} per page`, n, false, n === size));
  pick.onchange = () => go(1, +pick.value);
  nav.append(step("Previous", page - 1, page < 2), el("span", `Showing ${from + 1}-${Math.min(from + size, items.length)} of ${items.length}`),
    step("Next", page + 1, page >= pages), pick);
  return {rows: items.slice(from, from + size), nav};
}
function askError(box, message, retry) {
  box.replaceChildren(message || "");
  box.hidden = !message;
  if (message && retry) {
    const b = Object.assign(document.createElement("button"), {type: "button", className: "retry", textContent: "Retry", onclick: retry});
    box.append(" ", b);
  }
}
