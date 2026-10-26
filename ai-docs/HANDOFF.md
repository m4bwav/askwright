# Handoff

## Current state
2026-10-25 (study-mode session): 0.2.0 study mode and figures merged to main via PR (see log), tagged v0.2.0 on the owner's go, wiki updated. `"mode": "study"` makes a quiz (key kept on the server until submit, neutral option ids `o1`.., per-attempt shuffle, results.json attempts, review page with per-topic scores, `ask.py grade` for written answers); `figure` media draws graphs, force diagrams and shapes. Design: [decisions/2026-10-25-study-mode.md](decisions/2026-10-25-study-mode.md). Tests: T-20261025-3. Guide for authors: skills/askwright/references/study-mode.md.

Collision to resolve: another session's uncommitted 0.2.0 work (compact image review: `media_layout`, galleries, L-012 to L-014, C-20261025-2/-3, T-20261025-1/-2) sits in the main clone on `feat/compact-image-review`. This session used L-015/L-016, C-20261025-4 to -6 and T-20261025-3 so the ids do not clash. That branch must rebase onto main (conflicts expected in ask.py, app.js, app.css, CHANGELOG, TESTS, HANDOFF, log, schema.md, SKILL.md) and either join the 0.2.0 release notes (nothing is tagged yet) or become 0.3.0.

Session 6 (2026-10-24): v0.1.1 released on the owner's go ("do the wiki now and tag"; README links the wiki, no behaviour change), and the GitHub wiki written for it: https://github.com/m4bwav/askwright/wiki, ten pages, every output from [notes/2026-10-24-wiki-verify.py](notes/2026-10-24-wiki-verify.py) run against the release zip. How to update it: [notes/2026-10-24-github-wiki.md](notes/2026-10-24-github-wiki.md), which also lists four inaccuracies in the shipped README, CHANGELOG and schema.md for the next release. The first real film review was answered earlier in the session (L-008 `pick-without-reason`).

Session 3 (2026-10-24) ran the eval suite, wired the first review workflow and released v0.1.0 on the owner's go (https://github.com/m4bwav/askwright/releases/tag/v0.1.0, askwright-0.1.0.zip).
- Skill: [../skills/askwright/SKILL.md](../skills/askwright/SKILL.md) with `references/schema.md` and `references/writing-questions.md`. One tune this session: `randomized` is a fact about the clip (L-005, C-20261024-3).
- CLI: `skills/askwright/scripts/ask.py` (new, lint, serve, status, read, close, add, inline, stop). Page: `scripts/page/`.
- Repository tests: `tests/test_ask.py` 48/48 (1 skip on Windows), `tests/test_page.py` 15/15 (T-20261024-1). CI 7/7 on the first push.
- Eval suite: 8/8 (T-20261024-2). Triggers 3/3 on all three, decoys 0/3. Value cases run with `worth --ab` from `evals/fixtures/media-review/`, graded by `evals/check_set.py`. worth: KEEP, +67 points at 0.64x the cost. `action-ask-only-the-real-decision` passes without the skill too (kept as hold-out and over-ask guard).
- D5 wired in the owner's private image-generation skill: its pair tool takes `--ask <set>` (adds a compare question through `ask.py add`) and `picks <set>` (reads answers back into the side log). That PR is merged. cinewright has no person-facing review page, so nothing changed there (decision S5).

## In progress
Nothing half-done. Closed PR #2's old commit stays as is (owner ruling, session 3). The wiki inaccuracies wait for the next release.

## Decisions made this session
- [decisions/2026-10-24-session3-calls.md](decisions/2026-10-24-session3-calls.md): S1 to S5 (fixture folder, checker script, standalone outcome prompt, the hold-out, D5 wired in the pair tool rather than cinewright).

## Dead ends hit
- `claude plugin eval` cannot run Bash cases on native Windows (no sandbox), so the value cases went through `worth --ab`.
- `--ab` matches `input_match` against JSON-encoded tool input: a quoted path reads `ask.py\" serve`, so patterns must allow a backslash before the quote.
- Eval runs that serve a set leave detached servers in the temp run folders. Stop each with `ask.py stop <set folder>` after a suite.
- `evals/results/` from `claude plugin eval` holds machine paths and is git-ignored. Delete it before `tests/check_skills.py`, or the guard fails on it.

## Next single action
v0.2.0 is released (2026-10-25, askwright-0.2.0.zip 61,076 bytes) and the wiki updated for it (notes/2026-10-24-github-wiki.md, "0.2.0 update"). Next: settle the compact-image-review branch (rebase onto main as 0.3.0 work), and fix inaccuracy 5 (forces arrow scale per axis) in the next release.
