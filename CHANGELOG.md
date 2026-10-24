# Changelog: askwright

Every change to [README.md](README.md) and its companions, newest first, each with the reason. Reasons cite findings in [RESEARCH.md](RESEARCH.md) (`R-`), lessons in [LEARNINGS.md](LEARNINGS.md) (`L-`), and test runs in [TESTS.md](TESTS.md) (`T-`). State in `evergreen.json`. Protocol: MAINTENANCE.md.

Entry shape: `### C-YYYYMMDD-n · date · one-line summary`, then `because:` (IDs or "user request"), `files:` (file and section), and a sentence on what changed. Cite section headings, not line numbers.

### C-20261024-2 · 2026-10-24 · Built askwright 0.1.0: ask.py, the page, the skill and both test suites
- because: user request (kickoff session 2), R-20261024-2 to R-20261024-6, the post-mortem's F1 to F12
- files: skills/askwright/SKILL.md, references/schema.md, references/writing-questions.md, scripts/ask.py, scripts/page/ (index.html, app.js, app.css), tests/test_ask.py, tests/test_page.py, tests/fixtures/, README.md, RESEARCH.md, evals/evals.json
- ask.py: lint (the plan's rules plus alt text and title length), serve (127.0.0.1, exclusive bind on Windows, Range, token, Host and Origin checks, self-check, --detach), status (--wait-done), read, close, add, inline, new, stop. The page: one question per screen, compare sides revealed after the pick, guess shown or hidden by confidence, notes with pasted images and timecodes, resume line, overview, check answers, keys. Small calls: ai-docs/decisions/2026-10-24-session2-build-calls.md.

## Release notes

### 0.1.0 (unreleased)
- First version: question sets as data, the lint, the local page and the read-back. Windows and macOS, served to the local machine only.

### C-20261024-1 · 2026-10-24 · Created as an evergreen unit
- because: user request
- files: README.md, RESEARCH.md, LEARNINGS.md, evergreen.json (skills: also TESTS.md and evals/evals.json)
- Initial version. Tier `moderate`, interval 30d. See R-20261024-1 for the research basis; the first test run, for a skill, is logged in TESTS.md.
