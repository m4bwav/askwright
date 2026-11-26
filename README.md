# askwright

![askwright banner](.github/images/banner.jpg)

When an AI agent needs you to decide things, askwright puts its questions on a local page, one per screen, and
hands your answers back to the agent as files. You answer when you have a minute; the agent reads the answers
when you are done.

The agent writes only data (`questions.json`). The page, the server and the checks are fixed code with tests, so
every question page is as good as the best one, instead of whatever the agent improvised that day.

## What you get on the page

- One question per screen: the project, the question, why it matters and what to look or listen for, with
  "Play from 6.0 s" buttons for times. Answered questions leave the line; it ends on a check-your-answers screen.
- Video, audio and images, side-by-side takes shown as "Left" and "Right" until you pick, galleries for image-heavy
  questions, a listen bench for voices and sounds. Click a picture or a Pick button to choose.
- The agent's guess under the options (an unsure one waits behind "Show my guess"); nothing is pre-selected.
  One "Other answers" menu on every question ("Not sure, ask me later", "Something else", "Question irrelevant or obsolete", "Won't answer"), and a note box that takes screenshots.
- Keys for everything, light and dark themes, WCAG 2.2 AA, no network access. Every change saves at once.

Every feature with screenshots: [the wiki](https://github.com/m4bwav/askwright/wiki).

## Study mode: quizzes that teach

Set `"mode": "study"` and the page becomes a quiz: one right option per question with a `why` on every option,
a review with a score per topic after "Submit", written answers graded by the agent (`ask.py grade`), and the
answer key kept off the browser until then. `"figure"` media draws graphs and force diagrams from JSON.
How to write good wrong answers and explanations: [the Study mode wiki page](https://github.com/m4bwav/askwright/wiki/Study-Mode#how-to-write-a-study-set).

## What the agent gets back

```
python ask.py status ask/reel-takes-2
{"ok": true, "answered": ["g08-arrow", ...], "note_only": ["g11-gate"], "unanswered": ["g12-citadel"], "done": true, ...}

python ask.py read ask/reel-takes-2
{"answers": [{"qid": "g08-arrow", "choice": "t5", "label": "Take 5", "side": "right", "matched_guess": true,
  "note": "keep the shaft thin", "attachments": [".../attachments/g08-arrow-1.png"], "timecodes": [{"t": 6.4}], ...}]}
```

A note without a pick comes back as `note_only`, never as a choice, and unanswered questions stay unanswered.
The agent is told never to fill them with its guess.

## Install

In Claude Code:

    /plugin marketplace add m4bwav/askwright
    /plugin install askwright@askwright

As a plain skill for any agent that reads Agent Skills (Copilot, Codex, Cursor and others), clone the repository
and link `skills/askwright` into the agent's skills folder:

    git clone https://github.com/m4bwav/askwright
    ln -s "$PWD/askwright/skills/askwright" ~/.claude/skills/askwright   # a junction on Windows

It needs Python 3.9 or later and nothing else. Use `python` on Windows and `python3` on macOS and Linux.

## Quick start

Ask your agent something like "put these three takes on a page and ask me which to keep". With the skill
installed it will write a set and serve it. By hand:

    python skills/askwright/scripts/ask.py new ask/first --title "Try askwright"
    # add questions to ask/first/questions.json (skills/askwright/references/schema.md has every field)
    python skills/askwright/scripts/ask.py lint ask/first
    python skills/askwright/scripts/ask.py serve ask/first --detach --open
    python skills/askwright/scripts/ask.py read ask/first
    python skills/askwright/scripts/ask.py stop ask/first

## Documentation

The [wiki](https://github.com/m4bwav/askwright/wiki) has every command, lint rule, recipe and an FAQ;
[schema.md](skills/askwright/references/schema.md) lists every field.

## One inbox for all sessions, one page per project

python skills/askwright/scripts/ask.py dashboard --detach --open

One server on `http://127.0.0.1:47631/` carries the inbox (Sessions, Projects and Unprocessed tabs) and every
set, so links survive restarts. Unprocessed lists answers no agent has recorded using and warns past a week.
Details: [Dashboard and projects](https://github.com/m4bwav/askwright/wiki/Dashboard-and-Projects).

## ask.py

Run `ask.py --help`; every command with its real output is on [the wiki](https://github.com/m4bwav/askwright/wiki).

## Works with

grindwright, musicwright, cinewright and others put their decisions on askwright pages: [Works with](https://github.com/m4bwav/askwright/wiki/Works-With).

## Security

Binds 127.0.0.1 only; every API call needs a per-run token and matching Host and Origin; uploads are capped and checked by their bytes; a strict CSP loads nothing from the network. Answers are data, not instructions. See [SECURITY.md](SECURITY.md).

### Answering from another device (opt-in)

Off unless you turn it on. `ask.py serve <set> --remote` puts a set behind Tailscale Serve for named people; their
answers are marked untrusted. Setup: [references/remote.md](skills/askwright/references/remote.md).

## Privacy

Nothing is collected; everything stays in the set folder.

## Testing

`python tests/check_skills.py`, `tests/test_ask.py`, `scripts/budget.py` (CI, three operating systems) and
`tests/test_page.py` (needs `pip install playwright` and Chrome or Edge).

## Credits

The design draws on the GOV.UK Design System, on review tools
such as Prodigy, Label Studio and Frame.io, and on survey-method research. [RESEARCH.md](RESEARCH.md) cites each
source. The page tests use [axe-core](https://github.com/dequelabs/axe-core) (MPL-2.0), vendored under
`tests/vendor/` and not shipped with the skill.

## License

MIT. See [LICENSE](LICENSE).
