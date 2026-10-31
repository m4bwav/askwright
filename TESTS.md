# Tests: askwright

Test runs for [README.md](README.md). Cases live in `evals/evals.json`. A failure that taught something is a lesson in [LEARNINGS.md](LEARNINGS.md); a fix it caused is logged in [CHANGELOG.md](CHANGELOG.md) with `because: T-...`; research it triggered is in [RESEARCH.md](RESEARCH.md); counts and the failing list are in `evergreen.json` under `tests`. Rules: MAINTENANCE.md (testing section) and the plugin's `protocol/TESTING.md`.

A test passes on evidence (a tool call in the trace, a file, a marker, a log line), never on the transcript's claim that something was done.

Entry shape: `### T-YYYYMMDD-n · date · harness · env · passed/total`, then one line per failing case (`id · kind · class · what the evidence showed`), then `led to:` (L-, C-, R- ids or none). Newest first. Budget 150 lines; archive older runs to `TESTS-ARCHIVE.md`.

## How to run the repository suites

From the repository root: `python tests/check_skills.py`, `python tests/test_ask.py` and `python scripts/budget.py` (standard library only; CI runs these). The browser suites need `pip install playwright` and an installed Chrome or Edge, and skip with a message without them: `python tests/test_page.py` (behaviour, keyboard, axe) and `python tests/test_visual.py` (top bar, index, question set and project page at 1280, 1000, 390 and 340 px; screenshots in `tests/screenshots/`, git-ignored, or `ASKW_SHOTS=<dir>`). Look at the screenshots after any page change.

## Runs

### T-20261031-1 · 2026-10-31 · 0.10.0 repository suites · Windows, Python 3.14, Chrome · passed
- tests/test_page.py 47 passed (dashboard tests moved to the table with row expansion; new test_done_set_quick_action_copies_prompt; keyboard walk checks the finish screen's Copy prompt to continue).
- tests/test_ask.py 99 run, one Windows skip; tests/test_visual.py 4 passed (index screenshots at desktop and phone inspected by eye); check_skills 0 problems.
- led to: C-20261031-1

### T-20261030-3 · 2026-10-30 · 0.9.0 repository suites · Windows, Python 3.14, Chrome · passed
- tests/test_page.py 46 passed (4 new ClickMediaTests: clicking the right picture of a two-image compare picks sides.right and outlines it, then the left one switches the pick; a side-by-side clip gets left and right Pick buttons; `option` on bench clips picks from the row's button and reopens an answered question; plain media gets no pick target).
- tests/test_ask.py 98 passed, one Windows skip; tests/test_visual.py 4 passed; check_skills 0 problems; budget yellow (unchanged).
- led to: C-20261030-4

### T-20261030-2 · 2026-10-30 · 0.8.0 repository suites · Windows, Python 3.14, Chrome · passed
- tests/test_ask.py 99 tests, 98 passed and one existing Windows symlink skip (4 new ProjectAndTimeTests: `ask.py project` create, update, remove and list keeping `created`; a registered set creates its project record and shows on the project page with mtime-fallback times; new, add and close stamp times and add keeps `created`; /projects/<slug>, /api/projects and /api/project routes, 404 for unknown and traversal slugs).
- tests/test_page.py 42 passed (the bars test now waits for the More-menu move, L-022 `media-query-change-is-async`).
- tests/test_visual.py 4 passed (new): top bar at 1280, 1000, 390 and 340 px with a long title and one answer given (CI's first run failed test_review_fits_a_phone: Show answered pushed the phone row past the edge under Linux fonts, so it joins the More menu on phones; title one line with the full title on hover, pills one line, chips one baseline and height, nothing past the edge, no page scroll, one row on desktop); More menu on a phone holds Copy continue prompt and All sessions inside the screen; dashboard Projects strip and times, project page name, repos, sets and times at desktop and phone; project link from the question page. Screenshots inspected by eye.
- check_skills 0 problems; budget: SKILL.md body yellow (10,215 bytes), install yellow.
- led to: L-022, C-20261030-3

### T-20261030-1 · 2026-10-30 · 0.7.0 repository suites · Windows, Python 3.14, Chrome · passed
- tests/test_ask.py 95 tests, 94 passed and one existing Windows symlink skip (5 new: project and continue_prompt lint, default prompt with absolute paths, listen layout and clip fields, `new` flags, /api/set and dashboard rows).
- tests/test_page.py 42 passed (8 new ListenPageTests: one clip at a time, Shift+N and the A/B switch keeping position, seek bar, option sound without picking, compare clips hidden as Left/Right until the pick, project line and clipboard copy with counts, execCommand fallback, dashboard card copy, axe and no horizontal scroll at 1100 and 390 px).
- check_skills 0 problems; budget: install 247 KB (yellow, ceiling now 280 KB), SKILL.md body about 10.2 KB (yellow), description about 164 tokens.
- led to: C-20261030-1

### T-20261026-4 · 2026-10-26 · cross-platform CI follow-up · Windows, Python · local regressions passed
- PR #19 CI found that Linux and macOS could not reopen the bookmarked port after closing a connection. Ubuntu Python 3.9 also exposed concurrent server-info cleanup.
- Allow address reuse on Unix only; retain Windows exclusive binding and refusal of simultaneous listeners everywhere. Server-info cleanup tolerates another process already removing the file.
- Added regressions for immediate same-port restart while refusing a second live listener, and for removal of server.json between the stop command's existence check and unlink.
- Offline suite: 88 tests, 87 passed and one existing Windows symlink-rights skip. Structure and budget checks passed. The integrated browser suite's 34 passes are unchanged; cross-platform confirmation remains with CI.
- led to: C-20261026-4

### T-20261026-3 · 2026-10-26 · upstream integration and added regressions · Windows, Python, Chrome · application checks passed
- Combined offline suite: 86 tests, 85 passed and one existing Windows symlink-rights skip. All upstream study-mode, grading, retake and figure tests are retained.
- Added three regressions: study preview payloads omit answer keys, dashboard organization leaves quiz attempts unchanged, and unsupported POST bodies are consumed before another request on the same connection. The last case covers a Windows connection reset found during integration.
- Combined browser suite: 34 passed, retaining study review, figure, header/footer, gallery and dashboard checks. Both JavaScript syntax checks and the repository structure check passed.
- Budget: 222 KB install, 10,103-byte skill body and description about 164 tokens. Install ceiling is 240 KB for the combined features; the skill body still fits the unchanged 10 KB ceiling.
- Fresh-agent evaluation remains blocked as previously recorded. Local application checks do not replace model-level evaluation.
- led to: C-20261026-3

### T-20261026-2 · 2026-10-26 · session previews and organization · Windows, Python, Chrome · application checks passed
- Offline suite: 64 tests, 63 passed and one existing Windows symlink-rights skip. Previews contain at most five visible pending questions in set order, including stale answers and excluding answered, closed and conditional questions that are not shown.
- Snooze tests verify all five durations, the instant before expiry and the exact expiry boundary. Archive and restore persist through registration and server restarts, including missing sets. Auth, invalid durations, unknown sessions, corrupt state and write failures are covered. Questions and answers remain byte-for-byte unchanged.
- Browser suite: 28 passed. Added keyboard-accessible previews that remain expanded during refresh, snooze dropdown and Escape, separate lists, restore actions, persistence through reload, automatic expiry and explicit save failures. Dashboard accessibility checks pass for snoozed and archived views.
- JavaScript syntax, size budget and README prose checks passed. Install size: 172 KB; skill body unchanged at 9,897 bytes. An appended log line had CRLF endings; normalized the log to LF before the final structure check.
- Fresh-agent evaluation remains blocked as recorded in T-20261026-1. These additions change the application, not the skill's trigger or question-authoring guidance.
- led to: C-20261026-2

### T-20261026-1 · 2026-10-26 · shared session dashboard · Windows, Python, Chrome · application checks passed
- Offline suite: 60 tests, 59 passed and one existing Windows symlink-rights skip. Dashboard cases cover concurrent registration, deduplication, metadata, live counts, stale answers, missing sets, guarded routes, lint failures, process reuse and bookmark preservation.
- Browser suite: 25 passed. Dashboard cases cover search, product filtering, answered-session visibility, automatic refresh, reopening a stopped page, error messages, phone overflow and accessibility in both themes.
- The answer-preservation case passed again after adding an exact comparison of the answer file before and after restarting a question server.
- Structure and JavaScript syntax checks passed. Budget: 162 KB install, 9,897-byte skill body, description about 167 tokens. README prose check: zero strong findings.
- Fresh-agent suite attempted with three runs and without weakening isolation. The harness rejected an existing case definition with `invalid case.yaml: graders: Required` and reported that its temporary directory could not be sealed on Windows. Agent-level validation is blocked; application tests do not prove future skill invocation.
- A real dashboard served registered sets and returned authenticated ping and session responses. Registration did not modify question or answer files.
- led to: C-20261026-1

### T-20261025-2 · 2026-10-25 · per-frame review correction · repository and real-page checks passed
- Observed wrong outcome in use: the live page collected four model-policy decisions, even after its images became a gallery. The user needed per-frame picks and concrete success/failure guidance instead.
- Replaced the repaint question with ten individual comparisons and prepared a separate ten-question repeat-seed round. Both sets lint with zero errors or warnings. Each case has its own Good / Keep / Reject checks, source references and both/neither choices. Previous questions and answer data are preserved.
- Offline suite: 52 tests, 51 passed and one existing Windows symlink-rights skip. Browser suite: 22 passed. The frame-review data checker rejects one aggregate question and vague inspection guidance.
- Real-page checks on a temporary copy passed at desktop and phone sizes: one comparison per question, concrete criteria visible, no horizontal overflow, Next changes the frame question, background starts collapsed, and no answers were written. The live page was also checked for its new title, question and criteria.
- Structure, JavaScript syntax and budget checks passed. The new outcome-per-frame-review fresh-agent case is recorded but not run through the native Windows sandbox-blocked harness; it remains pending on a supported runner. Deterministic and real-page checks do not prove future agent behavior.
- led to: L-014, C-20261025-3

### T-20261025-1 · 2026-10-25 · repository and real-media browser checks · Windows, Python, Chrome · passed; fresh-agent outcome blocked
- Offline suite: 51 tests, 50 passed and one existing Windows symlink-rights skip. Includes media_layout validation, long-stack warning and the generated-data checker for compact reviews.
- Full page suite: 21 passed. After the phone-layout adjustment, all seven focused gallery/background tests passed again. The synthetic cases now include long selector labels.
- Real image-review set on a temporary copy: GenericPageTests passed three checks and skipped the video-only check. A separate desktop/phone run verified case navigation, background expansion/collapse, no answer writes and no horizontal overflow at 1440x1000 and 390x844. Screenshots stayed outside the public repository.
- Structure and JavaScript syntax checks passed. Budget: 141 KB install, 8,306-byte skill body, description about 167 tokens.
- The first phone check exposed tall media; a real long-caption case also exposed grid-track overflow. Reduced the phone image-height bound and used shrinkable grid tracks, then repeated the measurements successfully.
- New outcome-compact-media-review case and deterministic checker added. The initial model run lacked write/shell grants and was stopped. Retrying with declared grants refused all three runs before execution because the native Windows sandbox backend was unavailable. This is an infrastructure block, not a measured skill failure; no sandbox requirement was disabled. Fresh-agent baseline and outcome validation remain open on a supported runner.
- led to: L-012, L-013, C-20261025-2

### T-20261025-3 · 2026-10-25 · repository suites + claude plugin eval (triggers, decoys) · Windows 11, Python 3.14, Playwright, Chrome · all passed
- tests/test_ask.py 67/67 (1 skip, the Windows symlink test): the 48 earlier tests unchanged, plus StudyLintTests, StudyScoreTests, StudyServerTests (key hidden until submit, neutral option ids, submit, 409 after submit, retake keeps attempts, grade round trip, read/status, decision sets refuse study routes) and FigureTests.
- tests/test_page.py 20/20: the 15 earlier plus StudyPageTests (no key, extras, guess or note before submit; real ids never in the DOM; submit, review, missed-only filter, axe light and dark on the review, reload keeps the review, a grade written to results.json shows at the next poll, try again; review fits a 375 px phone; figure draws under the real CSP; no console errors). `ASKW_SET=tests/fixtures/study` GenericPageTests 3/3 + 1 skip (no video; the media test now skips instead of looping when a set has none).
- Real set: the owner's 22-question forces quiz lints clean and served; figures load under the real CSP on laptop and phone with no horizontal scroll. Two cold takes by fresh agents found no question with two defensible answers after fixes (findings: option ids leaking the key, L-015; giveaways by length, form and "only" wording; loose physics wording), all fixed.
- Eval: trigger-study-quiz 3/3 with the skill, 0/3 without; decoy-explain-mistakes quiet 3/3 in both arms; the five earlier trigger and decoy cases 3/3 each with the new description. Value cases (action, outcome) not re-run: they concern decision sets, whose behaviour did not change.
- led to: L-015, L-016, C-20261025-5

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
