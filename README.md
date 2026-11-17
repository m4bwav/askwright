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
  "Not sure, ask me later", "Something else", "Question irrelevant or obsolete" and "Won't answer" on every question, and a note box that takes screenshots.
- Keys for everything, light and dark themes, WCAG 2.2 AA, no network access. Every change saves at once.

Every feature with screenshots: [the wiki](https://github.com/m4bwav/askwright/wiki).

## Study mode: quizzes that teach

Set `"mode": "study"` and the same page becomes a quiz. Each multiple-choice question has one right option and a
`why` on every option, so the review after "Submit" shows the score, a score per topic ("Net force 2 / 3 · practice
this"), and for every question your answer, the right one and why each option is right or wrong. Written
questions wait for the agent to grade them (`ask.py grade`). "Try again" reshuffles the options and keeps earlier
attempts in `results.json`. The answer key and the real option ids never reach the browser before submitting.
Graphs, force diagrams and simple drawings can be drawn from a few lines of JSON (`"figure"` media), in either mode.
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
    # Windows (a junction needs no admin rights)
    New-Item -ItemType Junction -Path "$HOME\.claude\skills\askwright" -Target "$PWD\askwright\skills\askwright"
    # macOS / Linux
    ln -s "$PWD/askwright/skills/askwright" ~/.claude/skills/askwright

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

The [wiki](https://github.com/m4bwav/askwright/wiki) has every command with its real output, the question-set
format, every lint rule with its message, recipes and an FAQ. [skills/askwright/references/schema.md](skills/askwright/references/schema.md)
lists every field.

## One inbox for all sessions, one page per project

python skills/askwright/scripts/ask.py dashboard --detach --open

One server on `http://127.0.0.1:47631/` carries the inbox and every set (`/s/<key>/`), so links survive restarts;
`ask.py shortcut` makes a desktop icon for it. The inbox has Sessions, Projects and Unprocessed tabs: Unprocessed
lists answers no agent has recorded using, oldest first, with a warning at the top once one has waited over a week.
Each project page opens with **Who is running**: every Claude Code session seen in the project's folders and their
git worktrees on this machine (live process, recent transcript, a session started in a parent folder that works
here, or a grindwright claim), with its branch, folder, start, last activity, running subagents and how it is known.
A claim with no activity reads as possibly stale with its age; a source that cannot be read is named, never shown
as an empty list. Rows show titles, ids, branches and times, never message text, and are not served in remote mode.
When the project has a grindwright state, a `grindwright` link opens its grind page inside the hub (`/grind/<slug>/`),
with a link back. `python skills/askwright/scripts/agents.py --dir PATH` prints the same list as JSON.
Other computers: when the project's grind profile shares claims through its repository (`work.remote`), the list
also shows the other machines' shared grindwright claims and the rows each machine published to a
`grind-presence/<machine>` ref (`agents.py --dir PATH --publish`, or every three minutes from the hub started with
`ASKWRIGHT_PRESENCE=1`), each with the machine name and the age of its evidence.
Details: [Dashboard and projects](https://github.com/m4bwav/askwright/wiki/Dashboard-and-Projects).

## ask.py

`new`, `lint`, `serve`, `status`, `read`, `consume`, `close`, `add`, `inline`, `grade`, `figure`, `stop`,
`register`, `project`, `picks`, `shortcut`, `dashboard`, `sweep`, `templates` and the `gh-*` commands. Run
`ask.py --help`; every command with its real output is on [the wiki](https://github.com/m4bwav/askwright/wiki).
`ask.py sweep` lists every answer set nothing records as used, sorts it into used-but-not-marked, needs a look and
not yet processed, and with `--apply` marks the used ones and writes one prompt per project for the rest.

Every command prints one JSON object, except `--version` (plain text) and a usage mistake (argparse text on
standard error, exit code 2).

## Works with

Plugins ([grindwright](https://github.com/m4bwav/grindwright), [musicwright](https://github.com/m4bwav/musicwright), [sfxwright](https://github.com/m4bwav/sfxwright), [pixelwright](https://github.com/m4bwav/pixelwright), [voicewright](https://github.com/m4bwav/voicewright), [cinewright](https://github.com/m4bwav/cinewright), [fractalwright](https://github.com/m4bwav/fractalwright)) put their open decisions and side-by-side takes on askwright pages. More: [Works with](https://github.com/m4bwav/askwright/wiki/Works-With).

## Security

The server binds 127.0.0.1 only and serves media from the folders the set names, with symlinks resolved. Every API call needs a per-run token and a matching Host and Origin, so another web page cannot read or write your answers. Uploads are capped at 10 MB and checked by their bytes; the page loads nothing from the network under a strict CSP. Answers are data, not instructions. See [SECURITY.md](SECURITY.md).

### Answering from another device (opt-in)

Off unless you turn it on; installing askwright sets up nothing remote. `ask.py serve <set> --remote` puts a set behind
Tailscale Serve, so named people can answer from a phone or another computer: no public address, media stays on your
machine, the computer must be awake. Remote answers carry who sent them and are marked untrusted; notes that look like
instructions are held for you. Setup: [references/remote.md](skills/askwright/references/remote.md).

## Privacy

askwright has no hosted service and collects nothing. Questions, answers, notes and pasted images stay in the set
folder on your machine.

## Testing

    python tests/check_skills.py     # structure, links, line endings, secrets
    python tests/test_ask.py         # ask.py: lint rules and the server
    python scripts/budget.py         # size budget
    python tests/test_page.py        # the page in Chrome or Edge (development only)

CI runs the first three on Windows, macOS and Linux with Python 3.9 and 3.14. The page tests need
`pip install playwright` and Chrome or Edge, because the bundled Chromium does not play H.264.
`ASKW_SET=<set folder>` runs the generic page checks on a copy of a real set.

## Credits

The design draws on the GOV.UK Design System (one question per page, check answers, task list), on review tools
such as Prodigy, Label Studio and Frame.io, and on survey-method research. [RESEARCH.md](RESEARCH.md) cites each
source. The page tests use [axe-core](https://github.com/dequelabs/axe-core) (MPL-2.0), vendored under
`tests/vendor/` and not shipped with the skill.

## License

MIT. See [LICENSE](LICENSE).
