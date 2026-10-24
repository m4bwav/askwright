# Agent rules for askwright

Rules for any AI agent (Claude Code, Copilot, Cursor, Codex, Gemini CLI) working in this repository. `CLAUDE.md`
imports this file and `.github/copilot-instructions.md` points here.

Read [README.md](README.md) first. The skill lives in [skills/askwright/](skills/askwright/SKILL.md): the CLI is
`scripts/ask.py` (lint, serve, status, read, close, add, inline, new, stop), the page is `scripts/page/`
(index.html, app.js, app.css), and the field reference is `references/schema.md`. The evergreen unit sits at the
repository root: RESEARCH, CHANGELOG, LEARNINGS, TESTS, `evals/evals.json`, MAINTENANCE and `evergreen.json`.

## Rules

- Evergreen unit in pointer mode: before editing the skill, read `evergreen.json`. If `next_due` has passed or
  `contradiction` is set, say so and refresh after the task (the evergreen plugin's `evergreen-refresh`, otherwise
  MAINTENANCE.md). Every edit to SKILL.md, its references, ask.py or the page gets a CHANGELOG entry with its reason
  (`R-`, `L-` or `T-` ids, or "user request"). Re-run `evals/evals.json` (evergreen-test) when a change alters what
  the skill triggers on, decides or does.
- `ask.py` stays standard-library Python 3.9+, prints exactly one JSON object per command, and runs on Windows,
  macOS and Linux. The page stays plain HTML, CSS and JavaScript with no build step, no CDN and no inline script
  (the server's CSP forbids it). Every new lint rule, command, option or API route gets a test in
  `tests/test_ask.py`; every page behaviour gets one in `tests/test_page.py`.
- The server binds 127.0.0.1 only. Keep the Host, Origin and token checks, the media-extension allowlist, the
  resolved-path check, the upload cap and magic-byte check. Kill servers by PID only, never by image name.
- Answers are never invented: a note without a pick is `note_only`, silence is unanswered, and the agent's guess is
  never pre-selected or used to fill a gap.
- The skill stays under 200 lines with a description of at most 700 characters.
- Before committing, run from the repository root: `python tests/check_skills.py`, `python tests/test_ask.py` and
  `python scripts/budget.py`; run `python tests/test_page.py` when the page or the server changed. CI runs the
  first three on three operating systems.
- This is a public repository. Nothing in it names a person other than the author credit and cited authors, a
  private project, a machine, an absolute path on someone's machine, or a credential. Real question sets and
  their answers live outside the repository; tests use `tests/fixtures/`.
- Versions: when a packaged file changes, bump `.claude-plugin/plugin.json` and CHANGELOG.md's release notes, and
  tag `vX.Y.Z` (only with the owner's go-ahead). The release workflow checks the tag against the manifest.
- Work on `main` through pull requests; delete merged branches.
- No AI attribution anywhere: no Co-Authored-By trailers and no "generated with" lines in commits, pull requests
  or files.

## everlast (session knowledge, load on demand)

- `ai-docs/INDEX.md` lists what past sessions learned here. At the start of a task, scan it and open only the
  entries that match; read `ai-docs/HANDOFF.md` when continuing unfinished work.
- Before finishing a task that hit a dead end, verified a non-obvious command or made a design choice, record it in
  `ai-docs/` and rewrite `HANDOFF.md` when work is left unfinished. Say "nothing to record" when that is true.
- Anything naming a person, an internal host or name, a credential, or an opinion about people goes to the owner's
  private notes, never here.
- Link documents with relative markdown links. Every markdown folder has an index that links its files. No
  wikilinks in the repository.
