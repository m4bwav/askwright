# Changelog: askwright

Every change to [README.md](README.md) and its companions, newest first, each with the reason. Reasons cite findings in [RESEARCH.md](RESEARCH.md) (`R-`), lessons in [LEARNINGS.md](LEARNINGS.md) (`L-`), and test runs in [TESTS.md](TESTS.md) (`T-`). State in `evergreen.json`. Protocol: MAINTENANCE.md.

Entry shape: `### C-YYYYMMDD-n · date · one-line summary`, then `because:` (IDs or "user request"), `files:` (file and section), and a sentence on what changed. Cite section headings, not line numbers.

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

### 0.1.1 (2026-10-24)
- The README links the new [wiki](https://github.com/m4bwav/askwright/wiki). No behaviour changed.

### 0.1.0 (2026-10-24)
- First version: question sets as data, the lint, the local page and the read-back. Windows and macOS, served to the local machine only.

### C-20261024-1 · 2026-10-24 · Created as an evergreen unit
- because: user request
- files: README.md, RESEARCH.md, LEARNINGS.md, evergreen.json (skills: also TESTS.md and evals/evals.json)
- Initial version. Tier `moderate`, interval 30d. See R-20261024-1 for the research basis; the first test run, for a skill, is logged in TESTS.md.
