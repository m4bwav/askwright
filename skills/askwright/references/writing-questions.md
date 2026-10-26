# Writing questions people can answer in a minute

The person reads one screen, often hours after you wrote it, sometimes on a break. Everything they need to decide
must be on that screen: what is being decided, why it matters, what to look at, and what each option does.

## The 11-point check (run it on the whole set before `ask.py lint`)

Answer each point yes or no for every question; a yes needs a fix and a reason. This is the clarity rubric from
the question-evaluation research (QAS-99 adapted, R-T11); models under-flag point 3, so check it twice.

1. **Two decisions in one.** "Should we cut the intro and change the music?" is two questions. Split it.
2. **Vague term.** Take ids nobody remembers, jargon, or "better" without "better at what". Say what differs.
3. **Missing context.** Could someone answer from this screen alone? If they need a clip, an earlier answer, or
   what an option costs, put it on the screen (media, `why`, `consequence`, a `one_pager`).
4. **Wrong assumption.** The question takes for granted something not yet decided ("Which colour for the new
   logo?" before anyone agreed to a new logo). Ask the earlier question, or use `show_if`.
5. **Leading.** "Obviously", "don't you think", or a guess written as the default. State options neutrally;
   your view goes in `guess`.
6. **Bad options.** Options overlap, the order is odd, a real outcome is missing (tie, neither, redo), or a
   label is vague. Each option is something you would actually do.
7. **Wrong answer type.** Free text where a choice belongs (the person has to invent the options), or a choice
   where the real answer is a sentence.
8. **Recall burden.** The person must remember an earlier clip or answer. Show both takes side by side; quote
   the earlier answer in `why`.
9. **Tangled wording.** Long sentences, double negatives, instructions inside the question. One plain question.
10. **Trivial.** You could have decided this and flagged it in one line. Remove it from the set.
11. **No guess.** Every question carries your labelled guess with a reason and an honest confidence.

## Questions

- Start with the decision, not the background: "Which take of the arrow shot goes in the cut?"
- Put the short label in `title` ("The arrow"), never in `question`.
- `why` answers "what changes if I pick differently?": a render, a cost, an hour of work, what ships.
- Group nothing: one decision per screen. A decision with sub-parts becomes a `show_if` chain.

## Options

- Name the action or the thing: "Re-render tonight (10 to 12 h)", "Keep the drums", "Take 5".
- Never "Left", "Right", "A", "Option 2", "Yes" or "No". For blind takes, use `compare` with `sides`; the page
  shows the side until the pick and reveals the take after it.
- Put cost or effect in `consequence` ("Adds about an hour of renders").
- Order options in a natural order (time, size, the order in the clip), not with your pick first. The lint warns
  when your guess is always the first option.
- Do not add "Not sure" or "Other"; the page adds both to every question.

## Guesses

- Every question gets one, with the reason in a sentence.
- `high` only when you would act on it without asking: it shows under the options. Otherwise `low`: it waits
  behind "Show my guess", so the person forms a view first (default and anchoring effects, R-F11, R-F12).
- A guess is never pre-selected, and the read-back tells you when the pick matched it or followed a reveal.

## Media and review questions

- Choose the unit of judgment first. A batch evaluation normally needs one question per frame, take or edit,
  followed by an agent-written synthesis. Do not ask the person to select a model or default before collecting
  their judgments on the examples.
- For each case, explain the requested change and write Good / Keep / Reject checks. Name the thing and region:
  "Good: both arms hang beside the torso. Keep: the other actor's dagger grip. Reject: a hand still touches the
  head, or a new arm appears." "Check identity and quality" is too vague. Show source references when available.
- Include both-usable and neither-usable outcomes. A relative winner may still fail the brief; "not sure" means
  the reader cannot judge, not that the two versions work equally well.
- Use galleries for supporting views of one judgment, or an explicitly requested aggregate judgment. A
  slideshow does not replace collecting separate case-level picks. Keep each round short and synthesize the
  answers before asking for any overall policy change.
- Keep both sides of a comparison in the same case. Caption the difference, use `media_layout: "gallery"` for
  two tall images (three or more image-only items use a gallery automatically), and leave shared background
  in the collapsed one-pager. A short table can replace repeated detail. Avoid forcing a slideshow where the
  reader needs several images visible together; `media_layout: "stack"` is available.
- Preview real media at desktop and phone widths. Cases should fit the viewing area, with a full-size link for
  details; the reader should not scroll past a wall of images to answer.
- Use H.264/AAC `.mp4` side-by-side pairs for takes; put the takes on random sides and record them in `sides`.
- `look_for` names the moment and the test: "The arrow from 6.0 s: does it stay in his neck when he falls?".
  Each time becomes a jump button; `[` and `]` step through them.
- Cue the clip with `start` when the decision is in the middle.
- A `.vtt` file beside the video becomes captions.
- Tell the person they can type a note while the clip plays: the clip pauses and the note can be tied to that
  time; they can paste or drop a screenshot into the note.

## One-pagers (major decisions only)

Use one when the choice costs real time or money or is hard to undo. Keep it to what decides the choice:
- a two-line summary (`text`),
- the numbers (`facts`),
- an `options_compared` table: for each option, what is for it, what is against it, and what happens next,
- one image or chart when it shows the difference faster than words.

## Rounds

Close what you acted on (`ask.py close`). A rerolled shot is a new question that `supersedes` the old one; never
leave the old one open beside it. Raise `rev` when you edit an open question, so an earlier answer reads as
stale.
