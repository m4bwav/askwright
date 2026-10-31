"use strict";
// Relative times for every askwright page: "3 hours ago" in the text, the exact time on hover.
window.askTime = (function () {
  const units = [["year", 31536000], ["month", 2592000], ["week", 604800], ["day", 86400], ["hour", 3600], ["minute", 60]];
  const rtf = typeof Intl !== "undefined" && Intl.RelativeTimeFormat ? new Intl.RelativeTimeFormat(undefined, { numeric: "auto" }) : null;
  function relative(iso, now) {
    const t = Date.parse(iso);
    if (!iso || isNaN(t)) return "";
    const s = Math.round((t - (now || Date.now())) / 1000);
    for (const [unit, size] of units) {
      if (Math.abs(s) >= size) {
        const n = Math.round(s / size);
        return rtf ? rtf.format(n, unit) : Math.abs(n) + " " + unit + (Math.abs(n) === 1 ? "" : "s") + (n < 0 ? " ago" : " from now");
      }
    }
    return "just now";
  }
  function exact(iso) {
    const t = Date.parse(iso);
    return isNaN(t) ? "" : new Date(t).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
  }
  // A <time> element: datetime attribute, relative text, exact title.
  function el(iso, prefix) {
    const node = document.createElement("time");
    if (!iso || isNaN(Date.parse(iso))) { node.textContent = (prefix || "") + "unknown"; return node; }
    node.dateTime = iso;
    node.textContent = (prefix || "") + relative(iso);
    node.title = exact(iso);
    return node;
  }
  return { relative, exact, el };
})();
