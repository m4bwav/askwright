---
kind: decision
title: Keeping private material out of the public repository (scrub before the first push)
date: 2026-10-24
tags: [repo, privacy, public, history]
---

# Keeping private material out of the public repository

Small calls made in session 2 under the public-repo rule ([2026-10-24-public-repo.md](2026-10-24-public-repo.md)); flagged to Mark in the session's final message.

- **The post-mortem is generalised.** The original quoted the owner's notes, named his film project and its characters, and gave paths on his machine. It moved to the owner's private notes; the repository keeps [../notes/2026-10-24-hand-made-page-postmortem.md](../notes/2026-10-24-hand-made-page-postmortem.md) with the same F1 to F12 and no specifics.
- **Examples use a neutral reel.** The schema example, the plan example and the README use "the reel" and "the arrow shot" instead of the film's names.
- **The real question set lives in the owner's private notes**, with the generator script that rebuilt it from the old page. Tests reach it only through `ASKW_SET`.
- **`kickoff-prompt.md` is git-ignored.** The chained session prompt names machine paths and private notes by nature, so it stays on disk at the repository root (where the owner opens it) and never reaches GitHub. `tests/check_skills.py` skips it.
- **The public repository starts from a fresh history.** Commits made before the scrub hold the old post-mortem and the prompt, so the first push is a single new root commit of the scrubbed tree; the local repository keeps its full history in a separate branch that is never pushed.
- **One line in the append-only log was reworded** (the post-mortem entry named the film). Privacy wins over append-only here; this file is the record of the change.
- **`tests/check_skills.py` now flags any absolute path that starts with a drive letter**, not only home folders, after the first version missed the post-mortem's media path.
