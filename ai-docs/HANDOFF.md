# Handoff

## Current state
Session 2 (2026-10-24) built askwright 0.1.0 and proved it on a real set. Not tagged or released.
- Skill: [../skills/askwright/SKILL.md](../skills/askwright/SKILL.md) with `references/schema.md` and `references/writing-questions.md`.
- CLI: `skills/askwright/scripts/ask.py` (new, lint, serve, status, read, close, add, inline, stop). Page: `scripts/page/`.
- Tests: `tests/test_ask.py` 48/48 (1 skip on Windows), `tests/test_page.py` 15/15, generic page tests 4/4 on the owner's real 22-question film review set. Runs in [../TESTS.md](../TESTS.md) (T-20261024-1).
- Evergreen unit at the root (`evergreen.json`, RESEARCH, CHANGELOG, LEARNINGS L-001 to L-004, TESTS, MAINTENANCE). `evals/evals.json` has 8 cases, not run yet.
- Launch set: README with banner, LICENSE, SECURITY.md, AGENTS.md and CLAUDE.md (`@AGENTS.md`), copilot pointer, CI (`tests.yml`: three OSes x Python 3.9/3.14 plus a Chrome page job; `release.yml` on tags), dependabot.
- The real set lives in the owner's private notes (the askwright sidecar), with the generator that rebuilt it.

## In progress
Nothing half-done. See the session log for the push status of the public repository.

## Decisions made this session
- [decisions/2026-10-24-session2-build-calls.md](decisions/2026-10-24-session2-build-calls.md): B1 to B11 (compare sides shown as Left/Right until the pick, `new`/`stop`/`--detach`, the media URL scheme, token on every API route, wider video, install size accepted at 132 KB).
- [decisions/2026-10-24-public-scrub.md](decisions/2026-10-24-public-scrub.md): the post-mortem generalised, examples neutral, the session prompt git-ignored, a fresh single-commit history for the public repository.

## Dead ends hit
- The Mac refuses SSH (port 22, 2026-10-24), so the real-Mac run of `test_ask.py` could not happen; CI's macOS job covers it until Remote Login is on.
- `chrome.exe --version` on Windows talks to the running Chrome (L-004).

## Next single action
Run `evals/evals.json` with evergreen-test (baseline without the skill first), then wire the first real film review through askwright (decision D5) and ask Mark for the go to tag v0.1.0.
