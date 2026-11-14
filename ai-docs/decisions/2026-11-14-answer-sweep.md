# Answer sweep (0.31.0)

2026-11-14. Owner request: answers get lost, either never processed or used and never marked. Measured in
[../research/2026-11-14-unprocessed-answers.md](../research/2026-11-14-unprocessed-answers.md). Small rulings below
were made by the agent and flagged in the reply.

## A1. The command is `ask.py sweep`
Dry run by default. `--apply` marks the `used` pile consumed (note starts `sweep:` and cites the evidence) and moves
dead registry entries to `<state>/sessions-gone/`. `--prompts FILE` writes one section per project for what is left.
`--min-days` (default 1) puts younger sets in a `fresh` pile that is left alone, since a session may be on it.
Output is one JSON object with `warning`, `counts` and the piles. "Processed" is the owner's word; the code keeps
"consumed" (`consume` stays the command). The tab is renamed Unprocessed.

## A2. Piles and evidence
The script sorts by evidence it can read; the agent judges the rest.
- `used`: every answered question is closed, superseded or withdrawn. Of the 41 sets measured, 11 had this, and no
  sampled one had been left closed without the answers being acted on. Strong enough for `--apply` to mark.
- `check`: weaker evidence: a project HANDOFF/log/PROGRESS file that names the set's folder or id and changed after
  the answer (`named`), or a newer answered set beside it (`later_round`). The agent opens it and decides.
- `todo`: no evidence. The agent decides trivial or needs a session.
Commits were left out: the sets mostly live outside repositories, and a git scan per set is slow.

## A3. The edge of trivial
Recording a decision where the project keeps decisions, flipping a setting the answer names, closing a question the
answer makes moot. Anything else needs a session (references/sweep.md lists the exclusions).

## A4. Prompts
One file, one section per project (sets without a project under "(no project)"): the folder, the project's newest
continue prompt as an `Execute` line when one exists, the sets with their read commands, and the read, act, close,
consume, HANDOFF steps. The sweep never starts sessions.

## A5. The warning (over 7 days)
One text, `stale_warning`: the first field of `sweep`, a line in the session-start hook (`pending --hook`, regardless of
the current folder), and a banner at the top of the inbox linking the Unprocessed tab.

## A6. Gap fixes (numbers from the research note)
1. Never-read sets: `use_state` gains `unprocessed` (answered, no consume since, read or not) and `waiting_days`; the
   tab lists `unprocessed`. `unconsumed` keeps its old meaning for callers.
2. `pending` stays narrow (it is the "All done" wake-up); the week warning covers what it misses.
3. `close` records a consume (`by` from `--by`, default `close`) when it closes the last answered open question.
4. The generated continue prompt gains step 5: consume.
5. chainwright's prompt template: same fix in its own pull request (pair named in both changelogs).
6. Age: the Unprocessed tab shows "N days" waiting, sorts oldest first, marks rows over a week.
7. Dead entries: all were sets in session temp folders. `--apply` moves them aside; `new` warns when the set is in a
   temp folder.

## Budget
Install went over 400 KB. The README's feature list, command table and inbox section were cut to short summaries
pointing at the wiki (14.1 KB to 8.4 KB); the ceiling moved to 412 KB for the sweep code itself.
