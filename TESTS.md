# Tests: askwright

Test runs for [README.md](README.md). Cases live in `evals/evals.json`. A failure that taught something is a lesson in [LEARNINGS.md](LEARNINGS.md); a fix it caused is logged in [CHANGELOG.md](CHANGELOG.md) with `because: T-...`; research it triggered is in [RESEARCH.md](RESEARCH.md); counts and the failing list are in `evergreen.json` under `tests`. Rules: MAINTENANCE.md (testing section) and the plugin's `protocol/TESTING.md`.

A test passes on evidence (a tool call in the trace, a file, a marker, a log line), never on the transcript's claim that something was done.

Entry shape: `### T-YYYYMMDD-n · date · harness · env · passed/total`, then one line per failing case (`id · kind · class · what the evidence showed`), then `led to:` (L-, C-, R- ids or none). Newest first. Budget 150 lines; archive older runs to `TESTS-ARCHIVE.md`.

## Runs

### T-20261024-1 · 2026-10-24 · repository test suites (not the eval suite) · Windows 11, Python 3.14, Playwright 1.63, Chrome 155 · 67/67
- tests/test_ask.py 48/48 (1 skipped: the symlink-escape test needs symlink rights on Windows; it runs on Linux and macOS in CI). tests/test_page.py 15/15 on the fixture set, axe clean in light and dark. GenericPageTests 4/4 against the owner's real 22-question film review set (on a temp copy): one question per screen, keyboard-only to All done through 18 open questions and a show_if branch, a real pair clip plays, axe clean.
- evals/evals.json: 8 cases written (3 triggers, 2 decoys, 2 action, 1 outcome); not yet run. Owed: baseline without the skill, then the run (evergreen-test).
- CI on the first push (2026-10-24): 7/7 jobs green (ubuntu, macos, windows x Python 3.9 and 3.14; the Chrome page job on ubuntu). The symlink-escape test runs on Linux and macOS there.
- led to: L-001, L-002, L-003, C-20261024-2
