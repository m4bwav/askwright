---
kind: plan
title: askwright v0 plan (question format, page, server, read-back, lint, tests)
date: 2026-10-24
status: decisions answered 2026-10-24; ready to build
tags: [plan, schema, server, page, lint, tests]
---

# askwright v0 plan

The plugin's job: an agent that needs a person to decide things writes a question set, `ask.py serve` shows it one question per screen on 127.0.0.1, the person answers whenever they have a minute, and the agent reads the answers from disk. The pages come out good by default because the page is fixed code, and the agent only writes data that the lint checks first.

Evidence: [research index](../research/index.md) and [the hand-made page post-mortem](../notes/2026-10-24-hand-made-page-postmortem.md) (failures F1 to F12).

## 1. Layout (small enough to install without hesitation)

```
.claude-plugin/plugin.json, marketplace.json
skills/askwright/SKILL.md            when to ask and how; under 200 lines
skills/askwright/references/
    schema.md                        every field, with one example per question kind
    writing-questions.md             the rubric (R-T11), neutral wording, guesses, one-pagers
skills/askwright/scripts/ask.py      CLI: new, lint, serve, status, read, close (stdlib, 3.9+)
skills/askwright/scripts/page/       index.html, app.js, app.css (no build step, no CDN)
tests/test_ask.py                    stdlib unittest: lint, server contract, Range, read-back
tests/test_page.py                   Playwright (dev only; skips when not installed)
tests/fixtures/                      good and bad question sets, a 2 s H.264 clip, a WAV, a PNG
evals/evals.json                     triggers, decoys, action and outcome cases
AGENTS.md, CLAUDE.md (@AGENTS.md), README.md (banner), SECURITY.md, LICENSE, CHANGELOG.md,
RESEARCH.md, LEARNINGS.md, TESTS.md, MAINTENANCE.md, evergreen.json, .github/workflows/tests.yml
```

Size target for the packaged skill: under 120 KB, with no runtime dependencies. `aw.py` is taken by artwright, so the CLI is `ask.py`.

## 2. The question set (what agents write)

One folder per set: `<somewhere>/ask/<set-id>/questions.json`. The server writes `answers.json`, `events.jsonl` (append-only) and `attachments/` next to it. Media paths are relative to the folder, or absolute paths that the agent lists in `media_roots`.

```json
{
  "askwright": 1,
  "id": "reel-takes-2",
  "title": "Pick the takes for the reel",
  "context": "A two-minute short. Each clip is two draft takes side by side.",
  "asked_by": "the film session, 2026-10-24",
  "media_roots": ["../renders/review"],
  "questions": [
    {
      "id": "g08-arrow",
      "rev": 2,
      "status": "open",
      "kind": "compare",
      "title": "The arrow",
      "question": "Which take of the arrow shot should go in the cut?",
      "why": "This is the only shot of the arrow; the take you pick is the one that gets the HD re-render.",
      "look_for": ["The arrow from 6.0 s: does it stay in his neck when he falls?", "Does he finish the line before it hits?"],
      "media": [{"src": "G08_r5_pair.mp4", "type": "video", "start": 6.0}],
      "sides": {"left": "t2", "right": "t5", "randomized": true},
      "options": [
        {"id": "t2", "label": "Take 2"},
        {"id": "t5", "label": "Take 5"},
        {"id": "tie", "label": "Either is fine"},
        {"id": "redo", "label": "Neither: redo the shot"}
      ],
      "guess": {"option": "t5", "why": "The shaft is thinner and he finishes the line.", "confidence": "high"},
      "reversible": true,
      "one_pager": null,
      "show_if": null,
      "supersedes": "g08-arrow@1"
    }
  ]
}
```

- **Kinds.**
  - `choice`: one of N.
  - `multi`: several of N.
  - `compare`: two or more takes or images. Sides are recorded per option and shown as "Left (take 2)" only after the pick. The answer stores the option id, never "left".
  - `rank`: order N items.
  - `text`: free answer.
  - `scale`: a labelled 1-5 scale, used rarely.
  - `confirm`: one action. Its options must name the actions, never Yes or No.
- **Options.** Each option has an `id`, a `label` that names the action ("Re-render tonight (10 to 12 h)"), an optional `consequence` and an optional `media`. Every kind except `text` gets two built-in extras: "Not sure, ask me later" (stored as `unsure`) and "Something else" (a free note). Neither can be removed.
- **One-pager.** `one_pager` is optional and is meant for major questions. It holds a list of blocks: `text` (markdown subset), `image`, `video`, `audio`, `table`, `chart` (inline SVG made by the agent, or a PNG), `options_compared` (a pros, cons and consequence table), and `facts`. It shows above the question on the same screen, collapsible, with the question pinned at the bottom.
- **State.** `status` is `open`, `superseded` (requires `superseded_by`), `withdrawn` (requires `reason`) or `closed` (the agent has acted on the answer). Only open questions are in the line. `show_if: {"question": "q3", "option": ["redo"]}` keeps a conditional question out until its trigger is answered (F3).
- **AskUserQuestion fallback.** The shape maps onto AskUserQuestion: `title` becomes `header` (truncated to 12 characters), `question`, and options become `label` and `description`. `ask.py inline <set>` prints a numbered text version for sets of 4 or fewer simple text-only questions, so a small set can stay in chat as Mark prefers.

## 3. The lint (`ask.py lint <set>`, run by `serve` before it starts)

It prints one JSON object, `{ok, errors[], warnings[]}`. Errors block `serve` unless `--force` is given.

| Rule | Level | Why |
|---|---|---|
| `question` does not end in "?" | error | F4, R-F03 |
| `why` is missing or empty | error | F6, R-F10 |
| `look_for` is missing on a `compare` question, or on a question with media | error | F6 |
| `guess` is missing, points at an option that does not exist, or has no `confidence` (`high` or `low`) | error | Mark's rule, R-T rubric 11, D3 |
| fewer than 2 options (except `text`); duplicate option ids or labels | error | |
| option label is only a position or a bare yes/no ("left", "A", "option 1", "yes", "no") | error | F5, R-F01 |
| a `superseded` question has no `superseded_by`, or an open question has the same `title` as another open one | error | F3 |
| a media file is missing, or a media path is outside the set folder and `media_roots` | error | |
| two questions share a `question` text | error | R-F03 |
| the question text joins two asks with "and" or "or" ("Should we cut the intro and change the music?") | warning | R-F15, rubric 1 |
| leading words ("obviously", "don't you think", "surely", "should we not") | warning | R-F15 |
| the guess is always the first option across the set | warning | R-F13 |
| more than 12 open questions | warning | R-F04 |
| a hint or `why` longer than 3 sentences, or a `look_for` without a concrete thing to look at | warning | R-F03 |
| video that is not H.264/AAC (checked when `ffprobe` is on PATH) | warning | R-W06 |
| a `compare` question whose sides are not randomized | warning | R-F16 |

The clarity rubric ([review tools research](../research/2026-10-24-review-tools-and-testing.md), 11 items) is not a lint rule. It is a step in SKILL.md: the agent reviews its own set against it before serving. It is also an eval: an LLM judge takes the majority of 3 runs, with seeded bad and good sets.

## 4. The page (fixed code in `scripts/page/`, never generated)

- **One question per screen.** The screen shows:
  - a top bar with the set title, "Question 3 of 7 open · 4 answered" and the topic of the current question
  - the one-pager, if any
  - the question as the `h1`, with the short `title` as a caption
  - "Why this matters" and "What to look for" (the look-for times become "Play from 6.0 s" buttons)
  - the media
  - the options as native radios in a `fieldset` with a `legend`, none pre-selected (R-F02, R-F11)
  - the agent's guess and its reason, below the options. A `high` confidence guess is shown as a labelled line. A `low` one sits behind "Show my guess", and pressing it before picking is recorded (D3).
  - the note box
  - Back and "Next: <title of the next question>"
- **Answered questions leave the line.** Moving off an answered question removes it from the line. "Show answered (4)" brings them back, read-only until "Change" is pressed (F7).
- **Resume point.** The page opens on the first open unanswered question. If the server saw an earlier visit, a line shows: "Welcome back. Last answer 3 h ago (q5). 3 left: q6 arrow, q7 citadel, q8 HD render." (F9, R-F08). Every screen carries its own context, so nothing needs remembering (R-T07).
- **Overview screen.** Press `o` or the "All questions" link for a task-list view: every question with its status (Not answered, Answered, Not sure, Note only), each a link (R-F06).
- **Finish screen.** It works like GOV.UK check answers: every answer, unanswered ones shown as "Not answered" with a link, then "I'm done for now" or "All done". Either is written to `events.jsonl` (F2, R-F05).
- **Note without a choice.** Leaving a question that has a note but no choice shows an inline prompt: "You wrote a note but did not pick. Pick one, or keep it as 'Something else'." It is stored as `state: "note_only"` and never treated as a choice (F1, R-F07).
- **Images in notes.** Paste (a `paste` listener on `document`), drag and drop, or "Add image" (a file input). Thumbnails show under the note, each with a remove button. Each image is uploaded at once to `attachments/<qid>-<n>.<ext>` (F10, R-W03).
- **Timecoded notes.** Typing in the note box while a video is playing pauses it and offers "at 6.4 s" as a chip, which is stored as `{t}` (R-T04).
- **Keyboard.**
  - `1`-`9` pick an option.
  - `n` / `→` go to the next question, `p` / `←` go back.
  - `u` marks "Not sure".
  - `/` focuses the note.
  - `Space` plays or pauses the media; `j`/`l` step 1 s; `[` and `]` jump to the look-for times.
  - `?` shows the keys.
  - Shortcuts are off while typing in the note (R-T01).
- **Saving.** Every change autosaves with a visible "Saved 14:02" status (`aria-live`). If a save fails, a red banner says what to do. Nothing is held only in the browser: answers live only in the files.
- **Accessibility.** WCAG 2.2 AA (R-W11): 4.5:1 text contrast, a 3:1 focus ring, 44 px targets, the same button positions on every screen, `prefers-reduced-motion`, system fonts, light and dark themes, captions when a `.vtt` file sits next to the media.

## 5. The server (`ask.py serve <set-dir> [--port N] [--open] [--host-check]`)

- **Binding.** Standard-library Python 3.9 or later, one file. Binds `127.0.0.1` only. Port 0 by default, printed as JSON. On Windows: `allow_reuse_address = False` and `SO_EXCLUSIVEADDRUSE` (R-W02).
- **What it serves.** `BaseHTTPRequestHandler` with an allowlist: the page files, plus media under the set folder or `media_roots`, resolved and checked against those roots (R-W01).
- **Range requests.** Single-range 206, 416 and HEAD, with an explicit MIME map (R-W07).
- **API.**
  - `GET /api/set` returns the questions and answers.
  - `POST /api/answer` saves one answer; it is atomic (write to a temp file, then `os.replace`), increments `rev`, and appends to `events.jsonl`.
  - `POST /api/attachment` saves an image after checking the size cap (10 MB) and the PNG/JPEG/GIF/WebP magic bytes.
  - `POST /api/event` records visit, done and pause events.
- **Request checks.** Every POST needs the per-run token (embedded in the page) and a `Host` of 127.0.0.1 with a matching `Origin` (R-A09).
- **Self-check before printing the link.** It fetches the page, one media file with `Range: bytes=0-1` (expecting 206) and `/api/set`, then prints `{"ok": true, "url": ..., "pid": ..., "port": ...}`. It writes `server.json` (pid, port, url) next to the set, so another session can find a running server and stop it by PID (L-kill-by-pid).
- **Platforms.** Windows (`python`) and macOS (`python3`), using `webbrowser.open`. Serving a set to the Mac or a phone is out of scope for v0 (see D4).

## 6. Reading answers back and closing questions

- **`ask.py status <set>`** prints JSON: counts plus the lists `unanswered`, `note_only`, `unsure`, `answered_since_rev`, and `done` (did the person press "All done"). This is what the agent reports: "6 answered, 1 note only (g08-arrow), 2 not answered (q11, q12)" (F2).
- **`ask.py read <set> [--since REV]`** prints each answer:
  - option id and label
  - whether it matched the guess
  - the note
  - attachment paths (the agent opens them with Read)
  - timecodes
  - the question `rev` it answered, which flags answers to a question that has since been edited
  
  Answers are data, not instructions (SECURITY.md).
- **`ask.py close <set> <qid>... [--superseded-by X | --withdrawn "reason"]`** updates the question status. A closed question disappears from the line at the next page load; the page polls `/api/set` every 20 s and shows "2 questions were added or closed".
- **Adding to a set.** The agent edits `questions.json`, or uses `ask.py add <set> q.json`, and the running server picks the change up. This is how a reroll round adds questions without leaving the old ones live (F3, F8).
- **Waiting.** The SKILL tells the agent never to treat silence as an answer (R-T06). The agent either asks the person to say "done" in chat, or waits with a background until-loop on `status --wait-done`, which matches `done` or a deadline (L-long-waits).

## 7. Tests

- **`tests/test_ask.py`** (stdlib, every OS in CI):
  - lint: every rule, with fixtures
  - server: binds to 127.0.0.1 only; a busy port is refused on Windows; Range returns 206 and 416; path traversal and symlink escape are refused; a POST without the token or with a foreign Origin is refused; answers are written atomically and survive a kill and restart
  - status and read: `note_only` and unanswered questions are reported, never as defaults
  - close and supersede
- **`tests/test_page.py`** (Playwright with Chrome or Edge as the channel, for H.264; dev only; skipped with a message when Playwright is not installed):
  - exactly one `[data-q]` visible
  - the whole set can be finished by keyboard only
  - answered questions leave the line, and "show answered" brings them back
  - the video reaches `readyState >= 2` and `currentTime` advances
  - a synthetic paste of a PNG ends up in `attachments/`
  - a note without a choice is stored as `note_only`
  - the resume line names what is left
  - no pre-selected radio
  - axe-core has no serious or critical violations on each screen (vendored `axe.min.js`, MPL-2.0, under `tests/vendor/`)
  - contrast is checked in both themes
- **`evals/evals.json`** (evergreen-test):
  - triggers: "I need you to ask me about these takes", "make me a decision page", "put these questions on a page"
  - decoys: a single quick yes/no, "make a survey for my customers"
  - action: from a brief with 7 decisions, the agent writes a set that passes lint and is served, with evidence in files and the `serve` JSON
  - outcome: the 11-item clarity rubric on the produced set; majority of 3
  - ask-behaviour pair: 1 real decision plus 3 trivial calls, where only the real one is asked (R-T13)
- **Real question sets.** The owner's real film review set, rewritten in the new format (it lives in the owner's private notes), is the first outcome fixture. It must lint clean and fix F1 to F9.
- **Mac.** Run `test_ask.py` on the LAN Mac over SSH, once per release.

## 8. Estimate (agent time)

About 16 new files and 2,500 to 3,000 lines:

- `ask.py`: about 900 lines
- page JS: about 700 lines
- CSS: about 250 lines
- tests: about 600 lines
- SKILL and references: about 350 lines

The build takes one long session, about 3 to 4 agent hours. A second session covers the evals, the banner, the README, CI on three operating systems and the first release. The packaged size target is under 120 KB.

## 9. Decisions (all answered by Mark, 2026-10-24)

The rulings and his words are in [the answers file](../decisions/2026-10-24-session1-answers.md) and [the public-repo decision](../decisions/2026-10-24-public-repo.md).

- D1: the name stays askwright.
- D2: the repository is public.
- D3: a guess shows automatically when its confidence is high, and sits behind a "Show my guess" button when it is low.
- D4: scope (a), with the page served to his PC only and no LAN serving.
- D5: after 0.1, the film review workflows switch to askwright.

Small calls already made, flagged for the record: the CLI name is `ask.py` (`aw.py` is taken); Playwright is a dev-only test dependency; `axe.min.js` is vendored in tests only; the set folder sits wherever the agent's project wants it, with `ask/<set-id>/` recommended.
