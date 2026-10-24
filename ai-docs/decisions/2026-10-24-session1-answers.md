---
kind: decision
title: Mark's answers to the session 1 open decisions (name, guess display, scope, wiring)
date: 2026-10-24
tags: [owner-ruling, name, guess, scope]
---

# Mark's answers to the session 1 decisions

Answered in chat on 2026-10-24.

| # | Decision | His words | Ruling |
|---|---|---|---|
| D1 | Name | "askwright sure?" | Keep **askwright**. |
| D3 | When the agent's guess shows | "If you guess is confident then show it automatically, if your not sure then hide it behind a button" | Every guess carries `confidence`, which is `high` or `low`. A `high` guess shows as a labelled line under the options. A `low` guess sits behind a "Show my guess" button, which records whether it was pressed before the pick. It is never pre-selected. |
| D4 | First-release scope | "a, yeah I'm too lazy to b" | **(a)**: plan sections 2 to 7, on Windows and Mac, with the page served to his PC only. LAN serving is out. |
| D5 | Switch the old review workflows to askwright | "yes" | After 0.1, the owner's side-by-side take reviews (a private image-generation skill's pair tool) and cinewright reviews call askwright, starting with the next film review. |

What D3 changes in the build:
- Schema: `guess` is `{option, why, confidence: "high"|"low"}`.
- Lint: a guess without `confidence` is an error.
- Page: the button described above.
- `read` output: `guess_revealed_before_pick` for low-confidence guesses, so the agent can tell an independent pick from one made after seeing the guess (R-F11, R-F12).

Related: [../plans/2026-10-24-askwright-v0-plan.md](../plans/2026-10-24-askwright-v0-plan.md), [2026-10-24-public-repo.md](2026-10-24-public-repo.md).
