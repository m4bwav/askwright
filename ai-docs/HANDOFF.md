# Handoff

## Current state
Session 3 (2026-10-24) ran the eval suite and wired the first review workflow. 0.1.0 is still untagged.
- Skill: [../skills/askwright/SKILL.md](../skills/askwright/SKILL.md) with `references/schema.md` and `references/writing-questions.md`. One tune this session: `randomized` is a fact about the clip (L-005, C-20261024-3).
- CLI: `skills/askwright/scripts/ask.py` (new, lint, serve, status, read, close, add, inline, stop). Page: `scripts/page/`.
- Repository tests: `tests/test_ask.py` 48/48 (1 skip on Windows), `tests/test_page.py` 15/15 (T-20261024-1). CI 7/7 on the first push.
- Eval suite: 8/8 (T-20261024-2). Triggers 3/3 on all three, decoys 0/3. Value cases run with `worth --ab` from `evals/fixtures/media-review/`, graded by `evals/check_set.py`. worth: KEEP, +67 points at 0.64x the cost. `action-ask-only-the-real-decision` passes without the skill too (kept as hold-out and over-ask guard).
- D5 wired in the owner's private image-generation skill: its pair tool takes `--ask <set>` (adds a compare question through `ask.py add`) and `picks <set>` (reads answers back into the side log). That PR is merged. cinewright has no person-facing review page, so nothing changed there (decision S5).

## In progress
Nothing half-done. Waiting on the owner for the v0.1.0 tag and the wiki question.

## Decisions made this session
- [decisions/2026-10-24-session3-calls.md](decisions/2026-10-24-session3-calls.md): S1 to S5 (fixture folder, checker script, standalone outcome prompt, the hold-out, D5 wired in the pair tool rather than cinewright).

## Dead ends hit
- `claude plugin eval` cannot run Bash cases on native Windows (no sandbox), so the value cases went through `worth --ab`.
- `--ab` matches `input_match` against JSON-encoded tool input: a quoted path reads `ask.py\" serve`, so patterns must allow a backslash before the quote.
- Eval runs that serve a set leave detached servers in the temp run folders. Stop each with `ask.py stop <set folder>` after a suite.
- `evals/results/` from `claude plugin eval` holds machine paths and is git-ignored. Delete it before `tests/check_skills.py`, or the guard fails on it.

## Next single action
Ask the owner for the go to tag v0.1.0 (and whether to write the wiki), then tag. The release workflow checks the tag against `.claude-plugin/plugin.json`.
