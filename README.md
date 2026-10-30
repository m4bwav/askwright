# askwright

![askwright banner](.github/images/banner.jpg)

When an AI agent needs you to decide things, askwright puts its questions on a local page, one per screen, and
hands your answers back to the agent as files. You answer when you have a minute; the agent reads the answers
when you are done.

The agent writes only data (`questions.json`). The page, the server and the checks are fixed code with tests, so
every question page is as good as the best one, instead of whatever the agent improvised that day.

## What you get on the page

- One question per screen, read top to bottom: the project and set it belongs to, the question as the heading,
  why it matters, and what to look or listen for. Times in "what to look for" turn into "Play from 6.0 s" buttons.
- The project's name in the top bar and a "Copy continue prompt" button: it copies a prompt that tells an agent to
  read the answers (with absolute paths), check them against its guesses and act on them, plus the counts so far.
- A listen bench for voices and sounds: one row per clip with a big play button, the line spoken, a seek bar and
  the time; one clip plays at a time, `b` switches to the next clip at the same point, Shift+1 to Shift+9 play
  clip N. Blind voice picks show "Left"/"Right" until you pick. A sample on an option plays from a small button.
- Video, audio and images in the question. Takes compared side by side show "Left" and "Right" until you pick,
  then reveal which take was where.
- Image-heavy questions show one case at a time, with Previous/Next, a case selector and a full-size image link.
  Three or more images use this automatically; `media_layout` can request a gallery or a simultaneous stack.
- Background starts collapsed, with an expand/collapse control. Independent decisions still get separate
  questions. Batch evaluations collect frame-by-frame picks first, with specific Good / Keep / Reject checks;
  the agent recommends an overall model or workflow afterward.
- The agent's guess under the options. A confident guess is shown; an unsure one waits behind "Show my guess",
  and the agent learns whether you opened it before you picked. Nothing is ever pre-selected.
- "Not sure, ask me later" and "Something else" on every question.
- A note box that takes pasted or dropped screenshots. Typing while a clip plays pauses it and offers to tie the
  note to that moment.
- Answered questions leave the line. The page reopens on the first unanswered one with a "welcome back" line
  naming what is left, and ends on a check-your-answers screen with Change links.
- Keys for everything: `1`-`9` pick, `n`/`p` move, `u` for not sure, `/` for the note, Space, `j`/`l` and `[`/`]`
  for the clip, `?` for the list.
- Every change saves at once to the set folder. Light and dark themes, WCAG 2.2 AA, no network access.

## Study mode: quizzes that teach

Set `"mode": "study"` and the same page becomes a quiz. Each multiple-choice question has one right option and a
`why` on every option, so the review after "Submit" shows the score, a score per topic ("Net force 2 / 3 · practice
this"), and for every question your answer, the right one and why each option is right or wrong. Written
questions wait for the agent to grade them (`ask.py grade`). "Try again" reshuffles the options and keeps earlier
attempts in `results.json`. The answer key and the real option ids never reach the browser before submitting.
Graphs, force diagrams and simple drawings can be drawn from a few lines of JSON (`"figure"` media), in either mode.
How to write good wrong answers and explanations: [references/study-mode.md](skills/askwright/references/study-mode.md).

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

## One inbox for all sessions

Open a master page for every registered question set on this computer:

    python skills/askwright/scripts/ask.py dashboard --detach --open

The command returns a local URL you can bookmark. Calling it again reuses the running dashboard.
After a restart it reuses its previous port, unless you pass `--port`. Restart the command after rebooting.
If that port is occupied, the command reports an error rather than changing your bookmark.

Sets register automatically when agents create or serve them, across projects and agent products.
The default view shows sessions needing attention. Use All sessions to include answered rounds, or filter
by product and search by title, folder or agent. Counts refresh every five seconds from the answer files.
Notes without a pick, "not sure" and answers to changed questions still count as needing attention.
Conditional questions waiting on another answer are counted separately.

Each card names its project and has "Open questions" and "Copy continue prompt" buttons.
Each session card has an expandable preview of its next five questions needing attention, in question order.
The Snooze dropdown hides that session for 1 hour, 4 hours, 1 day, 3 days or 1 week.
It returns to the inbox when that time expires. Open Snoozed to bring it back early with Unsnooze.
Archive moves a session to the Archive list until you choose Unarchive.
All sessions includes answered sessions in the inbox; snoozed and archived sessions remain in their own lists.
These choices survive page and server restarts, and agents registering a set again do not reset them.
They change only dashboard organization, never questions, answers or server processes.

Open questions reuses a running question page or starts it again if it stopped. Existing answers stay in place.
Each question page also has an All sessions link, and `serve` returns its `dashboard_url`.
The independent master page stays up when individual question servers stop.

For older sets, run `ask.py register <set>`. Registration does not move or change the set.
Set `product`, `session` and `asked_by` in the question data to identify the originating agent, or pass
`--product`, `--session` and `--asked-by` when using `new`. Unknown metadata stays blank.
Older askwright installations must be updated to register automatically.

The registry and dashboard server details live in `~/.askwright`, outside your repositories.
All products running under the same user share it; `ASKWRIGHT_HOME` selects a different location.
Missing or unreadable sets show an error on the dashboard. askwright does not scan your disk for question sets.
Stop the independent dashboard with `ask.py dashboard --stop`; this leaves question pages running.

## ask.py

| Command | What it does |
|---|---|
| `new <dir> --title T` | Writes an empty set. `--project NAME`, `--project-path DIR`, `--continue-prompt TEXT` (or `--continue-prompt-file FILE`), `--back-link URL LABEL`, `--product`, `--session`, `--asked-by`. |
| `lint <set>` | Checks the set: questions end in `?`, every question says why, review questions say what to look for, options name actions rather than "left" or "yes", every question carries a guess with a confidence, media exists and sits inside the allowed folders, superseded questions are not left open. Warnings for two asks in one, leading words, a guess that is always the first option, over 12 open questions, and video that is not H.264/AAC (when ffprobe is installed). |
| `serve <set>` | Lints, then serves the page on 127.0.0.1 after fetching the page, the API and a clip with a Range request itself. `--detach` returns at once; `--open` opens your browser. |
| `status <set>` | Counts and lists; `--wait-done --timeout S` waits for "All done". |
| `read <set>` | Every answer; `--since REV` only newer ones. |
| `close <set> <qid>...` | Closes questions, or marks them `--superseded-by X` or `--withdrawn "reason"`. |
| `add <set> <file>` | Adds questions (a new round); a question with `supersedes` retires the old one. Refuses anything that fails the lint. |
| `inline <set>` | A chat version of a small set (4 or fewer plain questions), plus an AskUserQuestion mapping. |
| `grade <set>` | Study sets: lists written answers with their rubric; `--apply <file>` writes grades back. |
| `figure <spec> <out.svg>` | Draws a figure spec (graph, forces, shapes) to an SVG file to look at. |
| `stop <set>` | Stops the set's server by its PID, after the server answers a ping proving it owns that PID. |
| `register <set>` | Adds an existing set to the shared local dashboard, deduplicated by its resolved folder. |
| `dashboard` | Serves the shared session inbox. Supports `--detach`, `--open`, `--port N` and `--stop`. |

Every command prints one JSON object, except `--version` (plain text) and a usage mistake (argparse text on
standard error, exit code 2).

## Security

The server binds 127.0.0.1 only, on a free port. It serves the page files and media files (by extension) from the
set folder and the folders the set names, with symlinks resolved and checked. Every API call needs a per-run token
from the page and a matching Host header; a POST that sends an Origin header must send the page's own. Another web page, or a DNS-rebinding trick, cannot read or
write your answers. Uploads are capped at 10 MB and must be PNG, JPEG, GIF or
WebP by their bytes. The page runs under a strict Content Security Policy and loads nothing from the network.
Answers are data for the agent, not instructions; the skill says so. See [SECURITY.md](SECURITY.md).

## Privacy

askwright has no hosted service and collects nothing. Questions, answers, notes and pasted images stay in the set
folder on your machine.

## Testing

    python tests/check_skills.py     # structure, links, line endings, no secrets or home paths
    python tests/test_ask.py         # lint rules, server contract, Range, traversal, tokens, status and read
    python scripts/budget.py         # install size and description budget
    python tests/test_page.py        # the page in Chrome or Edge with Playwright and axe-core (development only)

CI runs the first three on Windows, macOS and Linux with Python 3.9 and 3.14. The page tests need
`pip install playwright` and an installed Chrome or Edge, because the bundled Chromium does not play H.264.
`ASKW_SET=<set folder> python tests/test_page.py GenericPageTests` runs the generic page checks against a real
set, on a temporary copy so its answers are untouched.

## Credits

The design draws on the GOV.UK Design System (one question per page, check answers, task list), on review tools
such as Prodigy, Label Studio and Frame.io, and on survey-method research. [RESEARCH.md](RESEARCH.md) cites each
source. The page tests use [axe-core](https://github.com/dequelabs/axe-core) (MPL-2.0), vendored under
`tests/vendor/` and not shipped with the skill.

## License

MIT. See [LICENSE](LICENSE).
