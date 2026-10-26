# Changelog: askwright

Every change to [README.md](README.md) and its companions, newest first, each with the reason. Reasons cite findings in [RESEARCH.md](RESEARCH.md) (`R-`), lessons in [LEARNINGS.md](LEARNINGS.md) (`L-`), and test runs in [TESTS.md](TESTS.md) (`T-`). State in `evergreen.json`. Protocol: MAINTENANCE.md.

Entry shape: `### C-YYYYMMDD-n · date · one-line summary`, then `because:` (IDs or "user request"), `files:` (file and section), and a sentence on what changed. Cite section headings, not line numbers.

### C-20261026-2 · 2026-10-26 · 0.4.0: previews, snooze and archive for session cards
- because: user request
- files: ask.py (five-question previews and persistent session-state API), page/dashboard.html, dashboard.js, dashboard.css, README.md, plugin.json, tests/test_ask.py, tests/test_page.py
- Each session card previews up to five questions needing attention. Snooze hides the session for a chosen duration and returns it automatically. Snoozed and Archive lists have restore controls. State lives outside question sets, survives registration and restarts, and leaves answers untouched.

### C-20261026-1 · 2026-10-26 · 0.3.0: shared question-session inbox
- because: user request
- files: ask.py (registry, dashboard, register, session metadata and reopen API), page/dashboard.html, dashboard.js, dashboard.css, index.html, SKILL.md, schema.md, README.md, plugin.json, tests/test_ask.py, tests/test_page.py
- A master page lists registered sessions across local projects and agent products, with live attention counts, search, product filtering and an All sessions view. Creating or serving a set registers its canonical folder atomically. Stopped question pages reopen with their answers intact. The independent dashboard retains its port for bookmarks and uses the same loopback, Host, Origin and token protections as question pages.

### C-20261025-3 · 2026-10-25 · Review individual cases before deciding model policy
- because: user correction, L-014 `evidence-before-policy`
- files: SKILL.md (review granularity and synthesis), writing-questions.md, README.md, LEARNINGS.md, page/app.js, evals/evals.json, evals/check_set.py, tests/test_ask.py, tests/test_page.py
- Batch reviews now call for one question per frame/pair with Good / Keep / Reject checks and both/neither outcomes. Galleries remain available for supporting views or explicit aggregate judgments. Single-image comparisons retain a full-size link. The agent synthesizes per-case picks before recommending a model/default change.

### C-20261025-2 · 2026-10-25 · 0.2.0: compact image galleries and collapsed background
- because: user request, L-012 `compact-review-cases`
- files: page/app.js and app.css (case navigation, bounded images, native background disclosure), ask.py (media_layout and long-media lint), schema.md, writing-questions.md, SKILL.md, tests/test_ask.py, tests/test_page.py, evals/evals.json, README.md, plugin.json
- Three or more question images use a gallery automatically. Authors can request a gallery for two images or keep a simultaneous stack. Keyboard case navigation does not answer or change questions. Background starts collapsed and remembers expansion during page navigation. Authoring guidance distinguishes examples supporting one decision from independent questions.

### C-20261025-1 · 2026-10-25 · `ask.py add` takes a questions.json-shaped file
- because: L-011 `add-takes-questions-wrapper`
- files: skills/askwright/scripts/ask.py `cmd_add`, tests/test_ask.py `test_close_and_add`
- `add` now accepts `{"questions": [...]}` as well as a list or one question; before, the wrapper was linted as one blank question with seven errors that did not name the cause.

### C-20261024-4 · 2026-10-24 · 0.1.1: a link to the new wiki
- because: user request ("do the wiki now and tag")
- files: README.md "Documentation" (new), .claude-plugin/plugin.json and scripts/ask.py `VERSION`
- The README now points to the GitHub wiki, which holds every command's output, the lint rules with their messages, recipes and an FAQ, each example run against the 0.1.1 release zip. No behaviour changed.

### C-20261024-3 · 2026-10-24 · `randomized` is a fact about the clip, not a field to fill
- because: T-20261024-2 (outcome-question-quality failed 1 of 3 with the skill), L-005 `randomized-is-a-fact`
- files: skills/askwright/SKILL.md "Step 1: write the set" (Kinds), references/schema.md "A question" (`sides` row)
- The compare kind now says `randomized: true` only when the sides were drawn at random, and that a fixed-order clip gets `false` with the lint warning kept (or the pair remade). The eval cases changed with it: evals/check_set.py checks the sides match the clip instead of demanding `true`.

### C-20261024-2 · 2026-10-24 · Built askwright 0.1.0: ask.py, the page, the skill and both test suites
- because: user request (kickoff session 2), R-20261024-2 to R-20261024-6, the post-mortem's F1 to F12
- files: skills/askwright/SKILL.md, references/schema.md, references/writing-questions.md, scripts/ask.py, scripts/page/ (index.html, app.js, app.css), tests/test_ask.py, tests/test_page.py, tests/fixtures/, README.md, RESEARCH.md, evals/evals.json
- ask.py: lint (the plan's rules plus alt text and title length), serve (127.0.0.1, exclusive bind on Windows, Range, token, Host and Origin checks, self-check, --detach), status (--wait-done), read, close, add, inline, new, stop. The page: one question per screen, compare sides revealed after the pick, guess shown or hidden by confidence, notes with pasted images and timecodes, resume line, overview, check answers, keys. Small calls: ai-docs/decisions/2026-10-24-session2-build-calls.md.

## Release notes

### 0.4.0 (2026-10-26)
- Expandable previews of the next five questions per session.
- Snooze dropdown with timed return and an Unsnooze action.
- Archive list with Unarchive; dashboard organization persists across restarts.

### 0.3.0 (2026-10-26)
- Shared local dashboard for question sessions across projects and agent products.
- Automatic registration, live counts, session metadata and reopening stopped pages.
- Search, product filters and an All sessions view for answered rounds.

### 0.2.0 (2026-10-25)
- Case-by-case image review with Previous/Next, a case selector and full-size links.
- Collapsed, expandable background and guidance for splitting long reviews into the right questions.
- Frame-level Good / Keep / Reject checks and individual picks before aggregate model-policy advice.

### 0.1.1 (2026-10-24)
- The README links the new [wiki](https://github.com/m4bwav/askwright/wiki). No behaviour changed.

### 0.1.0 (2026-10-24)
- First version: question sets as data, the lint, the local page and the read-back. Windows and macOS, served to the local machine only.

### C-20261024-1 · 2026-10-24 · Created as an evergreen unit
- because: user request
- files: README.md, RESEARCH.md, LEARNINGS.md, evergreen.json (skills: also TESTS.md and evals/evals.json)
- Initial version. Tier `moderate`, interval 30d. See R-20261024-1 for the research basis; the first test run, for a skill, is logged in TESTS.md.
