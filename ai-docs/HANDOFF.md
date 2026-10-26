# Handoff

## Current state
2026-10-26 follow-up: 0.4.0 adds session-card previews, timed snooze, Snoozed/Archive lists and restore controls. The local user-wide session state is independent of questions and answers. T-20261026-2 records 64 offline tests (one Windows skip) and 28 browser passes. The owner requested a PR including all current askwright changes, including the earlier image-gallery and per-frame work. No release tag was requested.

2026-10-26: shared session dashboard prepares 0.3.0 on the existing branch, without committing or tagging. `new` and `serve` register canonical folders in the user-wide registry; `register` imports existing sets; `dashboard --detach` serves an independent inbox with live counts, search, product filtering, answered-session visibility and reopening stopped question pages. Existing question and answer data are unchanged. C-20261026-1 and T-20261026-1 record the implementation and application checks. The fresh-agent suite remains blocked by its existing case schema and Windows isolation support.

2026-10-25 follow-up: the gallery alone did not fix review granularity. L-014/C-20261025-3 now require individual frame picks with Good / Keep / Reject checks before model-policy advice. The real review has ten active frame questions, a separate ten-question repeat-seed round, and the original policy questions preserved but retired. T-20261025-2 records 52 offline tests (one skip), 22 browser passes and real-page checks; the new fresh-agent outcome case remains blocked on this platform.

2026-10-25: local branch `feat/compact-image-review` prepares 0.2.0 (not committed, published or tagged). Image-heavy questions use case galleries; `media_layout` supports auto/gallery/stack, and background is collapsed with native expand/collapse. L-012, L-013, C-20261025-2 and T-20261025-1 record the design and checks. The owner's live review uses the new layout; its answers were preserved.

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
Read the owner's per-frame picks and notes, summarize usable outputs and failure patterns, then make a qualified model-role recommendation. Review the local changes and run both new outcome cases/baselines on a sandbox-capable runner; do not disable its sandbox requirement. Publish or tag only on the owner's go.
