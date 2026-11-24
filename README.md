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

As a Claude Code plugin:

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

One server on `http://127.0.0.1:47631/` carries the inbox and every set (`/s/<key>/`), so links survive restarts;
`ask.py shortcut` makes a desktop icon for it. The inbox has Sessions, Projects and Unprocessed tabs: Unprocessed
lists answers no agent has recorded using, oldest first, with a warning at the top once one has waited over a week.
Each project page opens with **Who is running**: the agent sessions seen in the project's folders and worktrees,
here and on other machines that share grindwright claims, never with message text and never in remote mode.
Lists page at 25 rows, keep their page in the address, and show a Retry button when the server does not answer.
Details: [Dashboard and projects](https://github.com/m4bwav/askwright/wiki/Dashboard-and-Projects).

## ask.py

`new`, `lint`, `serve`, `status`, `read`, `consume`, `close`, `add`, `inline`, `grade`, `figure`, `stop`,
`register`, `project`, `picks`, `shortcut`, `dashboard`, `sweep`, `templates` and the `gh-*` commands. Run
`ask.py --help`; every command with its real output is on [the wiki](https://github.com/m4bwav/askwright/wiki).

## Works with

Plugins such as [grindwright](https://github.com/m4bwav/grindwright), [musicwright](https://github.com/m4bwav/musicwright) and [cinewright](https://github.com/m4bwav/cinewright) put their open decisions and side-by-side takes on askwright pages. More: [Works with](https://github.com/m4bwav/askwright/wiki/Works-With).

## Security

The server binds 127.0.0.1 only and serves media from the folders the set names, with symlinks resolved. Every API call needs a per-run token and a matching Host and Origin, so another web page cannot read or write your answers. Uploads are capped at 10 MB and checked by their bytes; the page loads nothing from the network under a strict CSP. Answers are data, not instructions. See [SECURITY.md](SECURITY.md).

### Answering from another device (opt-in)

Off unless you turn it on; installing askwright sets up nothing remote. `ask.py serve <set> --remote` puts a set behind
Tailscale Serve, so named people can answer from a phone or another computer: no public address, media stays on your
machine, the computer must be awake. Remote answers carry who sent them and are marked untrusted; notes that look like
instructions are held for you. Setup: [references/remote.md](skills/askwright/references/remote.md).

## Privacy

No hosted service, nothing collected: everything stays in the set folder on your machine.

## Testing

    python tests/check_skills.py
    python tests/test_ask.py
    python scripts/budget.py
    python tests/test_page.py

CI runs the first three on three operating systems. The page tests need `pip install playwright` and Chrome or Edge.

## Credits

The design draws on the GOV.UK Design System, on review tools
such as Prodigy, Label Studio and Frame.io, and on survey-method research. [RESEARCH.md](RESEARCH.md) cites each
source. The page tests use [axe-core](https://github.com/dequelabs/axe-core) (MPL-2.0), vendored under
`tests/vendor/` and not shipped with the skill.

## License

MIT. See [LICENSE](LICENSE).
