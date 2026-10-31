# Continue prompt: askwright visual polish + project pages

Repeating prompt. State lives in `ai-docs/HANDOFF.md`, never here.

## Load state
1. Read `AGENTS.md`, `ai-docs/HANDOFF.md`, the tail of `ai-docs/log.md`, `ai-docs/plans/index.md`.
2. Read `skills/` (the askwright SKILL.md), `scripts/` (ask.py and the fixed page) and `tests/test_page.py`.
3. The clone is shared: make your own worktree/branch before editing (Mark, 2026-10-25).

## Goals (Mark, 2026-10-30)
1. **Top bar looks janky.** Screenshot that prompted this: the title "Director 0...." truncates, the counter wraps ("5 answered · 0 ..."), links (All sessions, Copy continue prompt, Show answered (5), All questions `o`, Keys `?`) sit on uneven baselines with key badges misaligned. Redesign: one clean row, title ellipsis with full title on hover, counters that never wrap, consistent link/button styling, a sensible collapse at narrow widths. Then keep improving the overall look of every askwright page (index, question set, banners like "Welcome back").
2. **Project pages.** A question set attaches to a project. Each project page shows: name, description, created, last worked on, its repos (GitHub URLs) and local directories, and its question sets. Projects live in ask.py's data store (pick the shape, record the decision in `ai-docs/decisions/`).
3. **Links.** The main page and every question set link to the project page; the main page groups or labels sets by project.
4. **Timestamps.** Projects, question sets and individual questions carry `created` and `updated` (ISO 8601), migrated for existing data (fall back to file mtime), shown on the pages in a relative form with the exact time on hover.
5. **Playwright tests** for visual work: a small suite that serves fixture data, takes screenshots of the top bar, index, question set and project page at desktop and phone widths, and asserts no overflow/wrap in the top bar. Keep it optional (skips if Playwright is absent) so the stdlib tests still run alone; document how to run it in `TESTS.md`.

## Order of work
Timestamps + project data model → project page + links → Playwright harness → top bar redesign (iterate with screenshots) → wider polish.

## Stop points / rules
- Decide small design calls yourself and record them; only ask Mark about big ones (via an askwright page).
- Run the existing tests plus the new Playwright suite before each commit.
- PR, then merge yourself once checks pass (Mark's default); tag a release if the version is bumped.
- Do not publish to any registry.

## Hand-over
Update `ai-docs/HANDOFF.md` and `ai-docs/log.md`, add new learnings to `LEARNINGS.md`, then print the same start command:
`Execute ai-docs/plans/2026-10-30-visual-and-projects-continue-prompt.md` (start in the askwright clone).
