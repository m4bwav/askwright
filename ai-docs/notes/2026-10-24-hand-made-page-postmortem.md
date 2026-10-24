---
kind: note
title: What a hand-made decision page got wrong (the page askwright replaces)
date: 2026-10-24
tags: [evidence, failures, design-input]
---

# What a hand-made decision page got wrong

The best agent-made decision page so far was a film review: 22 questions over side-by-side draft takes, a
local Python server, and 18 saved answers when it was read on 2026-10-24. It is the template the owner's agents
copy, so its failures are the ones every page made on the fly repeats. The original files, quotes and paths are
in the owner's private notes; this is the generalised version.

## What it did well (keep)

- A local `ThreadingHTTPServer` on 127.0.0.1 with `allow_reuse_address = False`, serving the clips in place.
  Videos played (an Artifact version of the same page did not).
- Every click and note saved at once (radio `change`, note debounced 800 ms). Nothing was lost across hours of
  context switching.
- Each question had a clip, the options, the agent's guess and a note box, with takes on random sides.
- Saved answers were reloaded, and a count line said "N of 22 answered".
- Colour tokens on `:root`, dark mode, focus outlines on the radio labels.

## What went wrong (design out)

| # | Failure | Evidence | askwright rule |
|---|---|---|---|
| F1 | An answer saved with a note and no choice | One answer had `"choice": null` and a note explaining a visual flaw | A note without a choice is its own state (`note_only`), shown as not answered; the page asks "pick one, or keep it as Something else" before moving on; the read-back lists it. |
| F2 | Skipped questions never flagged | Two questions had no entry; the counter said "18 of 22" but not which | The progress line names what is left; the check-answers screen links every unanswered question; `status` reports them. |
| F3 | Old questions left on the page | A question marked "Superseded" in its text still had radio buttons; a conditional question stayed live | `status` (`open`, `superseded`, `withdrawn`, `closed`); the lint fails on a superseded question without `superseded_by`; conditional questions carry `show_if`. |
| F4 | Headings were not questions | Every title was a label (a quoted line of dialogue, a shot name) | `question` is required and must end in `?`; the label is a separate short `title`. |
| F5 | Option labels that meant something else | One question said "pick left for go tonight, right to wait", reusing the Left/Right pair for a yes/no | Options are written per question and name the action; the lint fails on position-only and bare yes/no labels. |
| F6 | No "what to look for" | Most bodies described the shot; few said what decides it | `look_for` is required for review questions; a time in it becomes a "Play from 6.0 s" button. |
| F7 | Infinite scroll | 22 cards in one column, the newest appended at the bottom | One question per screen; answered ones leave the line; "Show answered" brings them back. |
| F8 | Header text carried state | "Questions 16 to 19 are new ... Question 15 is superseded" | State lives in each question (`status`, `rev`, `supersedes`), not in prose that goes stale. |
| F9 | No resume point | After a break the reader scrolled to find their place | The page opens on the first open question with a welcome-back line naming what is left. |
| F10 | Notes could not hold a picture | Visual flaws were described in words | Paste or drop an image into the note; the server saves it next to the answers. |
| F11 | A web font on a local page | A Google Fonts link | No network dependency; system font stack. |
| F12 | No Range support | `SimpleHTTPRequestHandler` sends the whole file for every request | The server answers single-range requests with 206, so seeking works and Safari plays video. |

Related: [../research/index.md](../research/index.md), [../plans/2026-10-24-askwright-v0-plan.md](../plans/2026-10-24-askwright-v0-plan.md).
