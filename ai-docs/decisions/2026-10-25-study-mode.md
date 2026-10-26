---
kind: decision
title: Study mode design calls (Q1 to Q10)
date: 2026-10-25
status: active
tags: [study-mode, quiz, schema, page, server]
summary: "how study mode (a quiz) is built: a set-level mode flag, the key kept on the server until submit, neutral option ids, per-attempt shuffle, results.json attempts, ask.py grade for written answers, and what a quiz drops from decision sets"
---

# Study mode design calls

The owner asked for a quiz mode next to decision mode: questions that teach as well as test, instant grading for
multiple choice, a review page (your answer, the right answer, why it is right, why each other option is wrong,
the score), optional written questions graded later by an agent through `ask.py`, retakes that reshuffle and keep
earlier attempts, a per-topic score, and old decision sets unchanged. These are the calls made while building it.

- **Q1 · A set-level `mode`, not new kinds.** `"mode": "study"` (default `"decide"`). Study sets use the existing
  `choice` and `text` kinds; the lint refuses the rest. Every study branch checks `is_study`, so decision sets run
  the same code as before (the 48 earlier tests pass unchanged).
- **Q2 · The key lives in questions.json and stays on the server.** `/api/set` strips `correct`, option `why`,
  `rubric` and `model_answer`, and sends `review` (with the key) only for a submitted attempt. Hiding the key from
  a determined 12-year-old with devtools is not the goal; not shipping it before submit is cheap and complete.
- **Q3 · Neutral option ids (L-015).** The page sees `o1`..`oN` in shown order; the server maps a pick back to the
  real id before validating and storing it. answers.json and results.json hold real ids.
- **Q4 · Shuffle per attempt on the server.** Each attempt gets a random `seed`; `option_order` shuffles with
  `random.Random(f"{seed}:{qid}")`, deterministic across processes, so the review shows the order the student saw.
  `shuffle: false` per question keeps an order. Question order is not shuffled (sets group by topic).
- **Q5 · Attempts in results.json, the live attempt in answers.json.** The page saves answers exactly as in decision
  mode. `POST /api/submit` snapshots answers into the current attempt with its score; `POST /api/retake` (only
  after a submit) starts attempt n+1 and clears answers.json. Earlier attempts stay. Answers to a submitted attempt
  are refused with 409.
- **Q6 · Scoring.** Choice: right or wrong at once; blank counts as unanswered (0). Text: `pending` until graded,
  then `right`, `partial` or `wrong` by points. `points` default 1; `bonus: true` is scored apart and kept out of
  the topic scores. `by_topic` gives earned / max / pending per topic; the page marks a topic "practice this" when
  points were lost.
- **Q7 · `ask.py grade`.** Without `--apply` it prints the ungraded and graded written answers of the latest (or
  `--attempt N`) submitted attempt with rubric, model answer and points. `--apply <file>` takes
  `{"<qid>": {"points", "feedback"}}` (or wrapped in `grades`), validates every entry first and refuses the whole
  file on any error, then rescores. The page picks the grade up at its next poll.
- **Q8 · What a quiz drops.** No guess, no question-level `why`, no `look_for` requirement, no "Not sure" or
  "Something else", no note box, no compare sides. The position-label and double-ask lint rules are off; the
  question-mark rule only needs a `?` somewhere and labels compare case-sensitively (L-016). New lint: one
  `correct`, `why` on every option, rubric on written questions, `topic` warning, two-option warning, and a set
  warning when the right answer is the longest option in more than half the questions.
- **Q9 · `submit` counts as done.** `status --wait-done` returns on a submit as on "All done", and a retake clears
  it, so the agent can wait for a quiz the same way.
- **Q11 · Figures as data URLs (owner request).** A `figure` media item is drawn by ask.py to SVG and sent as a
  `data:image/svg+xml` URL: the CSP already allows `img-src data:`, no file lands in the set folder, the page code
  is unchanged, and option media can be figures too. Three types cover the request (graph, forces, shapes); the
  SVG sits on a white card so it reads in dark mode. `self_check` skips data URLs.
- **Q10 · Docs placement.** SKILL.md gets a 6-line section and the description one trigger phrase; how to write
  distractors and explanations lives in references/study-mode.md to keep the per-use body under the 10 KB budget
  (8.2 KB after the change). Install size went from 133 KB to about 167 KB (yellow; red is 200 KB).
