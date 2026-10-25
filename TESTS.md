# Tests: askwright

Test runs for [README.md](README.md). Cases live in `evals/evals.json`. A failure that taught something is a lesson in [LEARNINGS.md](LEARNINGS.md); a fix it caused is logged in [CHANGELOG.md](CHANGELOG.md) with `because: T-...`; research it triggered is in [RESEARCH.md](RESEARCH.md); counts and the failing list are in `evergreen.json` under `tests`. Rules: MAINTENANCE.md (testing section) and the plugin's `protocol/TESTING.md`.

A test passes on evidence (a tool call in the trace, a file, a marker, a log line), never on the transcript's claim that something was done.

Entry shape: `### T-YYYYMMDD-n · date · harness · env · passed/total`, then one line per failing case (`id · kind · class · what the evidence showed`), then `led to:` (L-, C-, R- ids or none). Newest first. Budget 150 lines; archive older runs to `TESTS-ARCHIVE.md`.

## Runs

### T-20261024-2 · 2026-10-24 · claude plugin eval (triggers, decoys) + evergreen `worth --ab` (value cases, `claude -p`) · Windows 11, Claude Code 2.1.281, default model, no judge used · 8/8 after one tune (6/8 before)
- First eval-suite run, baseline arm included. Triggers 3/3 on each of three prompts with the plugin (0/3 without); decoys 0/3 on both, either arm. These are headless runs, a proxy for the main loop.
- Before the tune, re-graded after fixing two case defects (below): action-serve-a-set 3/3 with, 0/3 without (the baseline hand-wrote an HTML page or offered a claude.ai publish); outcome-question-quality 2/3 with, 0/3 without; action-ask-only-the-real-decision 2/3 with, 3/3 without.
- Failing: outcome-question-quality · outcome · wrong-outcome · with-arm run 1 wrote `sides.randomized: true` for a clip the prompt says has take 3 fixed on the left (L-005). Tuned (C-20261024-3), then 3/3.
- Harness defects found and fixed in the cases, not the skill: the serve trace pattern missed `ask.py\" serve` in JSON-encoded tool input (2 runs graded fail that had served); the ask-only prompt never named the repo, so one run reasonably asked for its name; the outcome case demanded `randomized: true`, the same mistake as the failure. Session-2 cases also put media under `tests/fixtures/media/` while the prompt said "this folder"; they now use `evals/fixtures/media-review/` and `evals/check_set.py`.
- After the tune: serve 3/3, outcome 3/3 (with arm re-run; the baseline arm is unchanged by a skill edit); ask-only 3/3 with, 3/3 without on the fixed prompt.
- Redundant: action-ask-only-the-real-decision passes without the skill. Kept as the hold-out and as a guard that the skill does not make the agent over-ask (with the skill: 11 to 17 s and $0.17 a run, against 52 to 66 s and about $0.52 without). The hold-out was opened before the tune edit, to fix its prompt; the edit concerns compare sides, which that case never touches.
- worth: KEEP, +67 points (noise margin 31) at 0.64x the cost.
- Judge: none ran. The outcome case's judge criteria were read by hand on the three after-tune sets: four questions each, named options, a guess with confidence on each, and the render question names the 10-hour cost. No rubric failure was found.
- Side effects: with-arm runs served nine detached servers in temp run folders; all were stopped with `ask.py stop`. Runs wrote `ai-docs/log.md` in their own temp folders only; `git status` of the source showed only this session's edits.
- Second platform: untested elsewhere (the Mac refuses SSH; CI covers the scripts on macOS and Linux, not the eval suite).
- led to: L-005, C-20261024-3

### T-20261024-1 · 2026-10-24 · repository test suites (not the eval suite) · Windows 11, Python 3.14, Playwright 1.63, Chrome 155 · 67/67
- tests/test_ask.py 48/48 (1 skipped: the symlink-escape test needs symlink rights on Windows; it runs on Linux and macOS in CI). tests/test_page.py 15/15 on the fixture set, axe clean in light and dark. GenericPageTests 4/4 against the owner's real 22-question film review set (on a temp copy): one question per screen, keyboard-only to All done through 18 open questions and a show_if branch, a real pair clip plays, axe clean.
- evals/evals.json: 8 cases written (3 triggers, 2 decoys, 2 action, 1 outcome); not yet run. Owed: baseline without the skill, then the run (evergreen-test).
- CI on the first push (2026-10-24): 7/7 jobs green (ubuntu, macos, windows x Python 3.9 and 3.14; the Chrome page job on ubuntu). The symlink-escape test runs on Linux and macOS there.
- led to: L-001, L-002, L-003, C-20261024-2
