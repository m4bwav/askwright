# askwright question set: every field

A set is one folder holding `questions.json`. The server writes `answers.json`, `events.jsonl`, `attachments/`,
`server.json` and `server.log` beside it; never edit those by hand. `ask.py lint` checks everything below.

## The set

| Field | Required | Meaning |
|---|---|---|
| `askwright` | yes | Format version: `1`. |
| `mode` | no | `decide` (default) or `study`: a quiz with an answer key (see "Study sets"). |
| `id` | yes | Letters, digits, `-`, `_`, `.` (64 at most). |
| `title` | yes | What this round decides; shown in the top bar. |
| `context` | no | One or two sentences on the project, for the record. |
| `asked_by` | no | Who is asking and when ("the film session, 2026-10-24"). |
| `product` | no | Agent product name, as text (for example, "Copilot" or "Codex"). Used to filter the shared dashboard. |
| `session` | no | Session name or id, as text, so separate sessions of one product are distinguishable. |
| `back_link` | no | `{"url": "http(s)://...", "label": "..."}`: a link in the top bar back to the project's own review page (a pick page, a contact sheet), beside "All sessions". `ask.py new --back-link URL LABEL` sets it. |
| `media_roots` | no | Folders that hold media, relative to the set folder or absolute. Media outside the set folder and these roots is refused. |
| `questions` | yes | The questions in the order the page walks them. |

## A question

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Unique in the set; same characters as the set id. |
| `kind` | yes | `choice`, `multi`, `compare`, `rank`, `text`, `scale` or `confirm`. |
| `title` | yes | Short label, shown above the question and in lists (80 characters at most). Unique among open questions. |
| `question` | yes | One question, ending in `?`. Unique among open questions. |
| `why` | yes | What the answer changes. Three sentences at most; put more in a `one_pager`. |
| `look_for` | with media or `compare` | List of the concrete things that decide it. `6.0 s` in the text becomes a "Play from 6.0 s" button. |
| `hint` | no | One extra line under the question. |
| `reversible` | no | `false` marks a decision that is hard to undo ("· hard to undo" beside the title); give such questions a `one_pager`. |
| `media` | no | List of media items (below), shown under "What to look for". |
| `media_layout` | no | `auto` (default), `gallery` or `stack`. Auto shows three or more image-only items as one case at a time; one or two remain stacked. Gallery explicitly enables case navigation, including for two tall images, and supports images only. Stack keeps every item visible together; four or more images produce a long-page warning. |
| `options` | all kinds but `text` | At least two `{id, label, consequence?, media?}`. Ids `unsure` and `other` are reserved. |
| `guess` | yes | Your answer: see "Guesses". |
| `sides` | `compare` | `{"left": "<option id>", "right": "<option id>", "randomized": true}`: which take sits where in the side-by-side media. `randomized` is `true` only when the sides were drawn at random; a fixed order is `false` (the lint warns). |
| `one_pager` | no | Background blocks shown above the question (below). |
| `show_if` | no | `{"question": "<id>", "option": ["<option id>", ...]}`: the question joins the line only after that answer. |
| `status` | no | `open` (default), `closed`, `superseded` (needs `superseded_by`) or `withdrawn` (needs `reason`). Only open questions are on the page. |
| `rev` | no | Starts at 1. Raise it when you change a question that may already be answered; answers to an older rev are reported as `stale`. `ask.py add --replace` does it for you. |
| `supersedes` | no | `"<old id>"` (or `"<old id>@<rev>"`). `ask.py add` marks the old question superseded. |

### Media items

`{"src": "G08_pair.mp4", "type": "video", "start": 6.0, "label": "...", "alt": "...", "caption": "..."}`.
A media item can be a drawn **figure** instead of a file: `{"figure": {...}, "alt": "..."}`. ask.py draws it as SVG
and the page shows it as an image (no file is written; `ask.py figure <spec.json> <out.svg>` saves one to look at).
- `graph`: `x_label`, `y_label`, optional `x_max`, `y_max`, `grid`, `ticks`, and `lines`: `[{"label": "A", "points":
  [[0, 0], [5, 40]], "dashed": false, "marks": [{"x": 2, "y": 16, "label": "C"}]}]`. Lines differ by colour and dash.
  Give a curve as many points.
- `forces`: a box (`object` names it) with arrows scaled to `newtons`: `"forces": [{"dir": "right", "newtons": 30,
  "label": "push"}]`; `dir` is right, left, up or down, and several forces one way sit side by side.
- `shapes`: `width`, `height` and `items` of `rect` (x, y, w, h), `circle` (x, y, r), `line` and `arrow` (x1, y1, x2,
  y2) and `text` (x, y, text), each with an optional `label`, `color` and `fill`.

`type` is inferred from the extension (video: mp4, m4v, webm, mov; audio: mp3, m4a, wav, ogg, opus, flac; image:
png, jpg, gif, webp, svg, avif). `start` (seconds) cues a video when it loads. Images need `alt`. `src` is looked
up in the set folder first, then in each media root.

A gallery item is one complete case. Keep a side-by-side comparison in one image so changing cases does not
hide one of its candidates; `scripts/contact.py out.png a.png b.png --labels ... --scale 3` makes one (Pillow).
Moving a project's existing long review page onto sets, with answers synced back to its picks file:
[bridging.md](bridging.md). `label` names a case in the selector; `caption` explains what to compare.
Navigation, a case counter and a full-size link appear around the active image. Galleries do not auto-advance
or record choices. Left/Right arrows inside the gallery change cases, not questions.

### Kinds

- `choice`: one of N. `confirm`: one action out of two or three; labels name the actions ("Render tonight",
  "Wait until Saturday"), never "Yes"/"No". `scale`: a short labelled scale shown in a row; every point has words.
- `compare`: takes or images side by side. With `sides`, the options in `sides` read "Left"/"Right" until the
  person picks, then "Left (Take 2)"; the stored answer is the option id. Add "Either is fine" and "Neither: redo"
  options when they are real outcomes.
- `multi`: any number of N.
- `rank`: the person orders every option and presses "Use this order".
- `text`: a free answer. Use it only when choices cannot cover the answer.

Every kind except `text` gets "Not sure, ask me later" (`unsure`) and "Something else" (`other`, explained in the
note); `text` gets "Not sure".

### Guesses

| Kind | Guess |
|---|---|
| `choice`, `compare`, `scale`, `confirm` | `{"option": "<id>", "why": "...", "confidence": "high"}` |
| `multi` | `{"options": ["<id>", ...], "why": "...", "confidence": "low"}` |
| `rank` | `{"order": ["<id>", ...every option...], "why": "...", "confidence": "low"}` |
| `text` | `{"text": "...", "why": "...", "confidence": "low"}` |

`high`: shown as "My guess: ..." under the options. `low`: behind "Show my guess"; the read-back reports
`guess_revealed_before_pick`. Choose `high` only when you would act on the guess without asking.

### One-pager blocks

Background starts collapsed. The reader can expand or collapse it using its summary; the choice is remembered
while navigating the current page session. Critical consequences still belong in the question's `why`.

| `type` | Fields |
|---|---|
| `text` | `text`: paragraphs, `- ` lists, `1. ` lists, `**bold**`, `*italic*`, `` `code` ``, `[link](https://...)` |
| `facts` | `items`: `[{"label": "Disk needed", "value": "40 GB"}]` |
| `options_compared` | `rows`: `[{"option", "pros", "cons", "consequence"}]` |
| `table` | `columns`, `rows` (lists of cells), `caption` |
| `image`, `chart` | `src`, `alt`, `caption` (a chart is an SVG or PNG file you made) |
| `video`, `audio` | as a media item |

## A whole example

```json
{
  "askwright": 1,
  "id": "reel-takes-2",
  "title": "Pick the takes for the reel",
  "context": "A two-minute short. Each clip is two draft takes side by side.",
  "asked_by": "the edit session, 2026-10-24",
  "media_roots": ["../renders/review"],
  "questions": [
    {
      "id": "arrow", "rev": 2, "kind": "compare",
      "title": "The arrow",
      "question": "Which take of the arrow shot should go in the cut?",
      "why": "This is the only shot of the arrow; the take you pick gets the HD re-render.",
      "look_for": ["The arrow from 6.0 s: does it stay in place when he falls?"],
      "media": [{"src": "arrow_r5_pair.mp4", "start": 6.0}],
      "sides": {"left": "t2", "right": "t5", "randomized": true},
      "options": [
        {"id": "t2", "label": "Take 2"},
        {"id": "t5", "label": "Take 5"},
        {"id": "tie", "label": "Either is fine"},
        {"id": "redo", "label": "Neither: redo the shot", "consequence": "About 40 minutes of renders."}
      ],
      "guess": {"option": "t5", "why": "The shaft is thinner and he finishes the line.", "confidence": "high"},
      "supersedes": "arrow@1"
    }
  ]
}
```

## Study sets (quizzes)

`"mode": "study"` on the set (default `"decide"`) makes it a quiz; [study-mode.md](study-mode.md) says how to write
one. Kinds are `choice` and `text` only; `guess`, the question's `why` and `look_for` are not needed, and a question
may quote its sentence after the `?`.

| Field | Where | Meaning |
|---|---|---|
| `topic` | question | The topic the review scores it under (warned when missing). |
| `correct` | option | `true` on exactly one option of a `choice` question. |
| `why` | option | Required on every option: why it is right, or the mistake it stands for. |
| `points` | question | Default 1. |
| `bonus` | question | `true`: scored apart from the main score and the topics. |
| `shuffle` | question | `false` keeps the option order; otherwise each attempt shuffles it. |
| `rubric`, `model_answer` | `text` question | For the grader; one of them is required. A rubric is a string or a list. |

The server writes `results.json`: `{"attempts": [{"n", "seed", "started", "submitted", "answers", "grades", "score"}]}`.
The page never sees `correct`, option `why`s, `rubric` or `model_answer` before the attempt is submitted.
`ask.py read <set>` on a study set prints `attempts` (each with `earned`, `max`, `pending_points`, `bonus_earned`),
the chosen attempt's `score` with `by_topic`, and per question `status` (`right`, `wrong`, `partial`,
`unanswered`, `pending`), `picked` and `right` labels or the written `text` and `grade`. `ask.py grade <set>` lists
`ungraded` and `graded` written answers; `--apply <file>` takes `{"<qid>": {"points", "feedback"}}`.

## What comes back

`ask.py read <set>` prints, per answered question: `state` (`answered`, `unsure`, `note_only`), `choice` and
`label` (or `choices`, `order`, `text`), `side` for compare takes, `note`, `attachments` (absolute paths),
`timecodes` (`[{"t": 6.4}]`, seconds into the first video), `matched_guess`, `guess_revealed_before_pick`,
`q_rev`, `current_rev`, `stale` and the answer `rev`. `--since <rev>` returns only newer answers; `--all` adds the
unanswered ones, with state `unanswered`. `ask.py status <set>` lists `answered`, `unsure`, `note_only`, `unanswered`, `waiting` (behind a
`show_if`), `not_applicable`, `stale`, and `done` / `paused` from the page's finish buttons.
