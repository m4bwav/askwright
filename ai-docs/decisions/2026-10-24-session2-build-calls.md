---
kind: decision
title: Small calls made while building askwright 0.1 (session 2)
date: 2026-10-24
tags: [build, page, server, schema]
---

# Small calls made while building askwright 0.1

Made in session 2 without asking (Mark's rule: decide small calls, record them, flag them in one line).

| # | Call | Why |
|---|---|---|
| B1 | A `compare` question with `sides` shows "Left" and "Right" as the option labels until a pick, then "Left (Take 2)". The stored answer is the option id. | The plan said sides are revealed after the pick, but a person cannot pick "Take 2" without knowing which side it is on. Side labels keep the pick blind to take numbers and keep the answer stable (R-F16). |
| B2 | Two extra commands: `new` (an empty set) and `stop`. `serve --detach` starts a background server and returns its JSON. | Agents cannot hold a foreground server; `stop` kills by the PID in `server.json` only after `/api/ping` proves that PID is the set's server, so a reused PID is never killed (kill by PID only). |
| B3 | Media is served at `/m/<root index>/<path>`, only for media extensions (video, audio, image, `.vtt`), after resolving symlinks and checking the root. | Keeps `answers.json` and `server.json` (which holds the token) unreachable over HTTP; the set folder is root 0, so attachments are served the same way. |
| B4 | Every `/api/` route needs the token, GET included, and every request needs a 127.0.0.1 or localhost Host header; POSTs also need a matching Origin when one is sent. | DNS rebinding could otherwise read answers through GET /api/set. |
| B5 | "Not sure" leaves the line like an answer; a note-only question stays in it. | "Not sure" is a deliberate deferral the finish screen shows; a bare note is not an answer (F1). |
| B6 | An answered question reached by Back, a link or "Show answered" opens read-only with a Change button. | The plan's "read-only until Change" for shown-again questions; it stops a stray number key from changing an old answer. |
| B7 | The page also reloads the set when the tab regains focus, besides the 20 s poll. | The person returns to the tab hours later; added and closed questions should show at once. |
| B8 | `reversible: false` shows "· hard to undo" beside the title. | The plan's example carried `reversible` (R-F18) but no rule used it. |
| B9 | Video media breaks out of the 48rem text column up to 72rem. | Found on the real set: side-by-side pairs left each take about 360 px wide. |
| B10 | The install is 132 KB against the plan's 120 KB target; `scripts/budget.py` is green under 120 KB and yellow to 200 KB. | ask.py (54 KB) and app.js (38 KB) carry the whole feature set; cutting them would cut checks or page behaviour. |
| B11 | `ask.py lint` warns on an image without `alt` and on a title over 80 characters. | Accessibility (WCAG 1.1.1) and the title's role as a caption. |
