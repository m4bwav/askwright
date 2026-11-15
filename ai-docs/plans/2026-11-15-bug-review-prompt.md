# askwright bug review

Work from `<full path to the repository>`. Make your own worktree and branch off `origin/main` (`git worktree add ../askwright-bug-review -b bug-review origin/master`); never switch the shared clone's branch. State goes in `ai-docs/HANDOFF.md`, never in this file.

## Goal

Find and fix real bugs in askwright: `ask.py`, the served page, and the session-start hook. Bugs mean wrong behaviour Mark or an agent hits, not style.

## Known bug to start with

The session-start hook keeps reporting answer sets as "waited over 7 days unprocessed" (for example "Blind pairs", "ACE-Step model tests", "Spear and Sranc") even though Mark has asked sessions to clean them up many times. Find out why `ask.py sweep` or `consume` does not make them stop showing up. Possible causes: a set consumed in a different folder from the one the hook scans, a revision or fingerprint mismatch, consume never written, or sets with "not sure" or open questions counted as unprocessed. Reproduce it on the real sets read-only first, then with a copy in a temp folder. Fix the cause, not the message, and give the hook a way for Mark to dismiss a set for good.

## Then review

1. Read `AGENTS.md`, `ai-docs/INDEX.md`, `ai-docs/HANDOFF.md`, the end of `ai-docs/log.md`, and `skills/askwright/SKILL.md`.
2. Run the test suite and note any failures before changing anything.
3. Hand each area to its own subagent and keep only its short report: (a) answer read, consume and sweep paths, plus revisions and concurrent writes; (b) the page and server (127.0.0.1 binding, ports in use, one question per screen, media and full paths, quizzes); (c) the hooks and lint; (d) Windows quirks (CRLF, cp1252, path case, long paths; use the quirkwright skill).
4. Each finding needs a failing reproduction before it counts. Write it as a test, fix it, and keep the test.
5. Open a PR. Merge it yourself once checks pass, under the standing rules in the owner's global agent instructions (askwright is public, so treat a change to a hook or a release as needing Mark unless it is a plain bug fix). Tag and release once checks pass, then update the installed plugin.

## Questions

Small rulings: decide and flag them in the log. Anything that needs Mark goes on an askwright set named `askwright-bug-review`, in plain words with no internal labels, any file he should open given by its full path.

## Stop and hand over

Stop when every finding is fixed or waits on Mark. Then run the evergreen-wrapup skill, update `ai-docs/HANDOFF.md` and the log, and end with this start command if work is left:

`Execute <full path to the repository>/ai-docs/plans/2026-11-15-bug-review-prompt.md`
