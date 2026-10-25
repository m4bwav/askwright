# askwright

![askwright banner](.github/images/banner.jpg)

When an AI agent needs you to decide things, askwright puts its questions on a local page, one per screen, and
hands your answers back to the agent as files. You answer when you have a minute; the agent reads the answers
when you are done.

The agent writes only data (`questions.json`). The page, the server and the checks are fixed code with tests, so
every question page is as good as the best one, instead of whatever the agent improvised that day.

## What you get on the page

- One question per screen, with the question as the heading, why it matters, and what to look for. Times in
  "what to look for" turn into "Play from 6.0 s" buttons.
- Video, audio and images in the question. Takes compared side by side show "Left" and "Right" until you pick,
  then reveal which take was where.
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

## ask.py

| Command | What it does |
|---|---|
| `new <dir> --title T` | Writes an empty set. |
| `lint <set>` | Checks the set: questions end in `?`, every question says why, review questions say what to look for, options name actions rather than "left" or "yes", every question carries a guess with a confidence, media exists and sits inside the allowed folders, superseded questions are not left open. Warnings for two asks in one, leading words, a guess that is always the first option, over 12 open questions, and video that is not H.264/AAC (when ffprobe is installed). |
| `serve <set>` | Lints, then serves the page on 127.0.0.1 after fetching the page, the API and a clip with a Range request itself. `--detach` returns at once; `--open` opens your browser. |
| `status <set>` | Counts and lists; `--wait-done --timeout S` waits for "All done". |
| `read <set>` | Every answer; `--since REV` only newer ones. |
| `close <set> <qid>...` | Closes questions, or marks them `--superseded-by X` or `--withdrawn "reason"`. |
| `add <set> <file>` | Adds questions (a new round); a question with `supersedes` retires the old one. Refuses anything that fails the lint. |
| `inline <set>` | A chat version of a small set (4 or fewer plain questions), plus an AskUserQuestion mapping. |
| `stop <set>` | Stops the set's server by its PID, after the server answers a ping proving it owns that PID. |

Every command prints one JSON object.

## Security

The server binds 127.0.0.1 only, on a free port. It serves the page files and media files (by extension) from the
set folder and the folders the set names, with symlinks resolved and checked. Every API call needs a per-run token
from the page and a matching Host header and Origin. Another web page, or a DNS-rebinding trick, cannot read or
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
