# Handoff

## Current state
2026-10-31 (owner request, visual and projects session 4): 0.13.0 (PR #32, tagged v0.13.0). Copy continue prompt now ends with `Execute <absolute path>` of the newest `*continue-prompt*.md` / `*next-session-prompt*.md` found in ai-docs/plans/, plans/ or the folder itself (project path, project dirs, set folder and three parents), served as `next_prompt`. Option numbers became key badges. Dashboard restarted from main; restart running question pages to get it. Still next: wider polish of the overview and study review screens, the owner's real projects with `ask.py project`. Install size near the 300 KB ceiling (C-20261031-1 split proposal).

2026-10-31 (owner request): 0.12.0 a single side-by-side image (`sides` set, one image) picks the left or right take by the half clicked; Pick buttons kept. C-20261031-4, T-20261031-4. Restart running question pages to get it.

2026-10-31 (visual and projects session 3): 0.10.1 (PR #28) dark-mode visual test (question, dashboard and project pages, body dark, visible text 4.5:1; it caught the phone Last updated cell at 2:1), one blue-grey dark palette on every page, dashboard plurals. 0.11.0 (PR #29, tagged v0.11.0) on the owner's mid-session request: sortable dashboard columns, Last updated newest first by default, remembered per browser, a sort bar on phones. Dashboard restarted from main. Still next for the continue prompt: wider polish of the question body, overview and study review; adding the owner's real projects with `ask.py project`. Install size 285 KB (yellow, ceiling 300 KB): the split proposal in C-20261031-1 is getting closer to needed.

2026-10-31 (owner request, visual and projects session 2): 0.10.0 dashboard table with expandable rows (Title, Project, Last updated, Action; the expanded row holds everything the old card showed), Copy prompt as the quick action for done sets, and Copy prompt to continue on the finish screen and the study review. C-20261031-1, T-20261031-1. Still next for the continue prompt: wider polish (question body, overview, study review), dark-mode screenshots in test_visual.py, adding the owner's real projects with `ask.py project`; restart the dashboard after pulling main (`ask.py dashboard --stop`, then `--detach`).

2026-10-30 (owner request): 0.9.0 click a picture, clip or sound to pick its option (images on click, video and audio by a Pick button under them, side-by-side clips by left/right buttons). Decisions K1 to K6: [decisions/2026-10-30-click-media-to-pick.md](decisions/2026-10-30-click-media-to-pick.md). Tests T-20261030-3.

2026-10-30 (visual and projects session 1): 0.8.0 on branch feat/projects-and-topbar: project records in the user-wide registry and a project page (name, description, created, last worked on, repos, folders, question sets), links to it from the question page's top bar and from the dashboard (Projects strip and card labels), created/updated on everything shown relative with the exact time on hover, the top bar redesigned to one row, and tests/test_visual.py (screenshots, no wrap or overflow). Decisions P1 to P10: [decisions/2026-10-30-projects-and-top-bar.md](decisions/2026-10-30-projects-and-top-bar.md). Tests T-20261030-2. Continue prompt: [plans/2026-10-30-visual-and-projects-continue-prompt.md](plans/2026-10-30-visual-and-projects-continue-prompt.md). Next for that prompt: wider polish of every page (question body, overview, finish and study review screens, dashboard filters), dark-mode screenshots in test_visual.py, and adding the owner's real projects with `ask.py project` (descriptions and repos) once 0.8.0 is on main and the dashboard restarted.

2026-10-30: 0.7.0 adds `project` and `continue_prompt` set fields (top bar, context line above each question, dashboard cards, a Copy continue prompt button with counts at copy time), the listen bench for audio-only questions (`media_layout: "listen"`, clip `text` and `option`, Shift+1..9, `b` A/B switch) and option sound buttons, plus a clearer question reading order. Design calls: [decisions/2026-10-30-listen-bench-and-page-design.md](decisions/2026-10-30-listen-bench-and-page-design.md). Tests: T-20261030-1. askwright is not installed as a plugin: agents run ask.py from the main clone, so pulling main there updates the runtime; a dashboard or question server started before the pull keeps serving the old page until restarted (`ask.py dashboard --stop`, then `--detach`).

2026-10-26 integration: PR #19 combines the dashboard/gallery work with upstream study mode, figures and header/footer fixes. T-20261026-3 records 86 offline tests (one Windows skip), 34 browser passes and three new cross-feature/HTTP regressions. Questions, answers and study attempts remain independent of dashboard organization.

2026-10-26 follow-up: 0.4.0 adds session-card previews, timed snooze, Snoozed/Archive lists and restore controls. The local user-wide session state is independent of questions and answers. T-20261026-2 records 64 offline tests (one Windows skip) and 28 browser passes. The owner requested a PR including all current askwright changes, including the earlier image-gallery and per-frame work. No release tag was requested.

2026-10-26: shared session dashboard prepares 0.3.0 on the existing branch, without committing or tagging. `new` and `serve` register canonical folders in the user-wide registry; `register` imports existing sets; `dashboard --detach` serves an independent inbox with live counts, search, product filtering, answered-session visibility and reopening stopped question pages. Existing question and answer data are unchanged. C-20261026-1 and T-20261026-1 record the implementation and application checks. The fresh-agent suite remains blocked by its existing case schema and Windows isolation support.

2026-10-25 follow-up: the gallery alone did not fix review granularity. L-014/C-20261025-3 now require individual frame picks with Good / Keep / Reject checks before model-policy advice. The real review has ten active frame questions, a separate ten-question repeat-seed round, and the original policy questions preserved but retired. T-20261025-2 records 52 offline tests (one skip), 22 browser passes and real-page checks; the new fresh-agent outcome case remains blocked on this platform.

2026-10-25: local branch `feat/compact-image-review` prepares 0.2.0 (not committed, published or tagged). Image-heavy questions use case galleries; `media_layout` supports auto/gallery/stack, and background is collapsed with native expand/collapse. L-012, L-013, C-20261025-2 and T-20261025-1 record the design and checks. The owner's live review uses the new layout; its answers were preserved.

2026-10-25 (study-mode session): 0.2.0 study mode and figures merged to main via PR (see log), tagged v0.2.0 on the owner's go, wiki updated. `"mode": "study"` makes a quiz (key kept on the server until submit, neutral option ids `o1`.., per-attempt shuffle, results.json attempts, review page with per-topic scores, `ask.py grade` for written answers); `figure` media draws graphs, force diagrams and shapes. Design: [decisions/2026-10-25-study-mode.md](decisions/2026-10-25-study-mode.md). Tests: T-20261025-3. Guide for authors: skills/askwright/references/study-mode.md.

The upstream study-mode, figures and header/footer fixes are integrated into PR #19 without replacing either implementation.

Session 6 (2026-10-24): v0.1.1 released on the owner's go ("do the wiki now and tag"; README links the wiki, no behaviour change), and the GitHub wiki written for it: https://github.com/m4bwav/askwright/wiki, ten pages, every output from [notes/2026-10-24-wiki-verify.py](notes/2026-10-24-wiki-verify.py) run against the release zip. How to update it: [notes/2026-10-24-github-wiki.md](notes/2026-10-24-github-wiki.md), which also lists four inaccuracies in the shipped README, CHANGELOG and schema.md for the next release. The first real film review was answered earlier in the session (L-008 `pick-without-reason`).

Session 3 (2026-10-24) ran the eval suite, wired the first review workflow and released v0.1.0 on the owner's go (https://github.com/m4bwav/askwright/releases/tag/v0.1.0, askwright-0.1.0.zip).
- Skill: [../skills/askwright/SKILL.md](../skills/askwright/SKILL.md) with `references/schema.md` and `references/writing-questions.md`. One tune this session: `randomized` is a fact about the clip (L-005, C-20261024-3).
- CLI: `skills/askwright/scripts/ask.py` (new, lint, serve, status, read, close, add, inline, stop). Page: `scripts/page/`.
- Repository tests: `tests/test_ask.py` 48/48 (1 skip on Windows), `tests/test_page.py` 15/15 (T-20261024-1). CI 7/7 on the first push.
- Eval suite: 8/8 (T-20261024-2). Triggers 3/3 on all three, decoys 0/3. Value cases run with `worth --ab` from `evals/fixtures/media-review/`, graded by `evals/check_set.py`. worth: KEEP, +67 points at 0.64x the cost. `action-ask-only-the-real-decision` passes without the skill too (kept as hold-out and over-ask guard).
- D5 wired in the owner's private image-generation skill: its pair tool takes `--ask <set>` (adds a compare question through `ask.py add`) and `picks <set>` (reads answers back into the side log). That PR is merged. cinewright has no person-facing review page, so nothing changed there (decision S5).

## In progress
Dashboard implementation and application tests are complete. The master page is running outside the repository. Older installations need the updated script for automatic registration; no installed plugin caches were rewritten. The owner approved a PR including all current changes. No release or tag was requested.

The compact and per-frame review changes are included in the approved PR scope. Both new fresh-agent outcome cases need a supported sandbox runner before claiming model-level verification. Closed PR #2's old commit stays as is (owner ruling, session 3). The existing wiki inaccuracies remain outside this change.

## Decisions made this session
- [decisions/2026-10-24-session3-calls.md](decisions/2026-10-24-session3-calls.md): S1 to S5 (fixture folder, checker script, standalone outcome prompt, the hold-out, D5 wired in the pair tool rather than cinewright).

## Dead ends hit
- `claude plugin eval` cannot run Bash cases on native Windows (no sandbox), so the value cases went through `worth --ab`.
- `--ab` matches `input_match` against JSON-encoded tool input: a quoted path reads `ask.py\" serve`, so patterns must allow a backslash before the quote.
- Eval runs that serve a set leave detached servers in the temp run folders. Stop each with `ask.py stop <set folder>` after a suite.
- `evals/results/` from `claude plugin eval` holds machine paths and is git-ignored. Delete it before `tests/check_skills.py`, or the guard fails on it.

## Next single action
Check PR #19's merge status before further source work. The compact/per-frame fresh-agent outcome cases still need a sandbox-capable runner; do not weaken isolation. Per-frame answer review and the documented figure-scale wiki inaccuracy remain separate follow-ups. Release tags still need approval.
