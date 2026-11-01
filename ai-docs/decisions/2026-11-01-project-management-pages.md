# 2026-11-01: project pages for managing a project (0.17.0)

Owner request: "a history of the project, what its goals are, does it need direction, last prompt run, first prompt run, dates and whatever else would help manage the project", plus a dashboard project filter, a SKILL.md trim and the install-size split.

- D1. **The record grows, it does not split.** `goals`, `status` (active, needs-direction, paused, done), `direction` (the open question) and `history` (notes, status changes, prompt runs; last 500) sit in the same `projects/<slug>.json`. Older records read as active with no goals.
- D2. **Prompt runs are recorded, not guessed.** File times cannot tell when a prompt was run, so `ask.py project NAME --prompt-run FILE` records a run; SKILL.md tells agents to do it when they run a continue prompt. First and last run come from those entries.
- D3. **The folders speak for themselves.** The page reads each project dir's `ai-docs/HANDOFF.md` (its opening, 1,500 chars), the dated `## [YYYY-MM-DD] kind | text` lines of `ai-docs/log.md` (last 256 KB) and the newest continue or next-session prompts, at page load only (the dashboard's 5 s poll uses the light list). Log entries merge into the history; a checkbox hides them.
- D4. **Needs you box** on top: the direction question and how many questions wait, with one Open button. The same direction re-sent adds no history entry.
- D5. **Copy start command** copies `Execute <absolute path>` of the newest prompt file.
- D6. **Dashboard project filter** beside Product: `?project=SLUG` wins, else the last choice per browser; "No project" lists sets without one. The Projects tab gets a Status column.
- D7. **Install split**: references/bridging.md and study-mode.md moved to the wiki (Dashboard and Projects, Study Mode); README's long dashboard section moved to the wiki. Install still 306 KB after the new pages, so the yellow ceiling went from 300 to 320 KB (flagged to the owner).
