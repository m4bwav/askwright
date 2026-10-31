# Changelog: askwright

Every change to [README.md](README.md) and its companions, newest first, each with the reason. Reasons cite findings in [RESEARCH.md](RESEARCH.md) (`R-`), lessons in [LEARNINGS.md](LEARNINGS.md) (`L-`), and test runs in [TESTS.md](TESTS.md) (`T-`). State in `evergreen.json`. Protocol: MAINTENANCE.md.

Entry shape: `### C-YYYYMMDD-n · date · one-line summary`, then `because:` (IDs or "user request"), `files:` (file and section), and a sentence on what changed. Cite section headings, not line numbers.

### C-20261031-5 · 2026-10-31 · 0.13.0: copied continue prompts end with the next-session prompt's Execute line; option key badges
- because: user request ("make it so that copy able prompt will check for a next session prompt and continue that if its available"; "the copyable prompt usually says continue the next prompt without providing a copyable link"), continue prompt (wider polish), T-20261031-5
- files: ask.py (next_session_prompt finds the newest `*continue-prompt*.md` or `*next-session-prompt*.md` in ai-docs/plans/, plans/ or the folder itself, across the project's path, its registered dirs, and the set's folder and three parents; /api/set and dashboard rows carry it as `next_prompt`), page/app.js and page/dashboard.js (the copied text ends with "Then carry on with the next-session prompt:" and `Execute <absolute path>` on its own line, after the status line), page/app.css (option numbers are small key badges aligned with the label, accent when picked, hidden on touch screens; unpicked options show a hover border), tests/test_ask.py (test_next_prompt_found_in_project_folder), tests/test_page.py (test_project_label_and_copy_prompt checks the last line), plugin.json, ask.py VERSION

### C-20261031-4 · 2026-10-31 · 0.12.0: click either half of a side-by-side image to pick that take
- because: user request ("I'd like to also be able to click on the image in this case to choose between the two"), T-20261031-4
- files: page/app.js (sideClickable: a single side-by-side image with `sides` picks the left or right option by which half is clicked; the hovered half is named in the tooltip), page/app.css (.side-pickable: an accent wash over the hovered half, figure fits the image), tests/test_page.py (test_click_half_of_side_by_side_image_picks_that_side), plugin.json, ask.py VERSION. The left/right Pick buttons stay for keyboard users.

### C-20261031-3 · 2026-10-31 · 0.11.0: sortable dashboard columns, newest first by default
- because: user request ("Make this columns sortable and default to the last updated desc"), T-20261031-3
- files: page/dashboard.js (Title, Project, Last updated and Action headers are sort buttons with aria-sort and an arrow; default Last updated descending; a new column starts newest-first for time, A to Z for text, open before done for Action; ties fall back to title; rows without a value stay last; the choice is remembered in localStorage when available), page/dashboard.css (sort buttons; on phones the header becomes a sort bar without Action), page/dashboard.html (Unavailable sessions count no longer spaced as "( 1 )"), tests/test_page.py (test_columns_sort_newest_first_by_default), plugin.json, ask.py VERSION

### C-20261031-2 · 2026-10-31 · 0.10.1: dark-mode visual tests; one dark palette; dashboard plurals
- because: continue prompt (dark-mode screenshots, wider polish), T-20261031-2
- files: tests/test_visual.py (test_dark_mode_pages_are_dark_and_readable: question, dashboard and project pages at desktop and phone in dark mode, body must be dark and visible text at least 4.5:1), page/dashboard.css (the phone Last updated cell was 2.0:1 in dark mode, found by the new test), page/app.css (question page dark palette moved from neutral grey to the dashboard's blue-grey so every page matches), page/dashboard.js (summary says "1 question needs ... 1 session"), TESTS.md, plugin.json, ask.py VERSION

### C-20261031-1 · 2026-10-31 · 0.10.0: dashboard table with expandable rows; copy-to-continue on the finish screen
- because: user request ("each item is too large... a table with expandable rows... Title, Project, last updated, and quick link action button"; "the last page of the quiz... should have a button to copy a prompt to process the answers and continue"), T-20261031-1
- files: page/dashboard.js and dashboard.css (sessions table: Title with an open/done badge, Project, Last updated, Action; a row toggle expands the old card contents: product, context, times, counts, next five questions, Open, Copy continue prompt, Snooze, Archive, path; a done set's quick action is Copy prompt; phone layout stacks each row), page/app.js and app.css (finish screen "Hand the answers back" box with Copy prompt to continue, primary when nothing is left open; study review gets the button too), tests/test_page.py (dashboard tests on the table, test_done_set_quick_action_copies_prompt, finish-copy check), tests/test_visual.py, plugin.json, ask.py VERSION
- Install budget: 0.10.0 measured 283 KB on CI, past the 280 KB yellow ceiling; the unused card `.project` rules were cut and scripts/budget.py's ceiling raised to 300 KB (owner warned; split proposal: move the study-mode and bridging references to the wiki).
- Done means nothing needs attention and at least one answer was given; a set closed with no answers keeps Open questions.

### C-20261030-5 · 2026-10-30 · 0.9.1: the dashboard hides unavailable sessions by default
- because: user request ("hide Unavailable Sessions by default")
- files: page/dashboard.html and dashboard.js (an "Unavailable sessions (N)" checkbox, off by default, shown only when there are some), tests/test_page.py (test_empty_missing_and_failed_requests), README.md, plugin.json, ask.py VERSION
- Sessions whose set cannot be read (moved, deleted or broken questions.json) no longer fill the lists; they stay registered and appear when the box is ticked.

### C-20261030-4 · 2026-10-30 · 0.9.0: click a picture, clip or sound to pick its option
- because: user request ("when I have to choose between different images/videos/sounds I can click on the picture or resource as a means of selecting left, right or whatever"), T-20261030-3
- files: page/app.js (mediaOption, sidePicks, pickFromMedia, pickable, markPicks; question media, gallery slides and listen-bench rows), page/app.css (pickable outline, Pick buttons, two to four pictures side by side), references/schema.md (Media items), tests/test_page.py (ClickMediaTests), plugin.json, ask.py VERSION
- Images pick on click; video and audio get a Pick button so their own click still plays and seeks. Design calls: ai-docs/decisions/2026-10-30-click-media-to-pick.md.

### C-20261030-3 · 2026-10-30 · 0.8.0: project pages, timestamps, a one-row top bar, visual tests
- because: user request (the top bar looked janky: truncated title, wrapped counter, uneven links; project pages with repos, folders and question sets; created/updated on everything; Playwright screenshots), T-20261030-2
- files: ask.py (project records and `ask.py project`, /projects/<slug>, /api/projects, /api/project, created/updated stamped by new/add/close with an mtime fallback, project slug in /api/set and /api/sessions), page/index.html, app.js, app.css (one-row top bar: project link over an ellipsised title, position and count pills, chips on one baseline, a More menu under 70rem, Show answered joining it on phones; question time in the caption; calmer Welcome back notice), page/time.js (new: relative times, exact on hover), page/project.html and project.js (new), page/dashboard.* (projects strip, project links, worked-on and created times), references/schema.md (The set, Projects), SKILL.md (Step 1), tests/test_ask.py (ProjectAndTimeTests), tests/test_visual.py (new), tests/test_page.py (bars test waits for the menu move), TESTS.md, plugin.json
- Design calls: ai-docs/decisions/2026-10-30-projects-and-top-bar.md.

### C-20261030-2 · 2026-10-30 · 0.7.1: no stray "null" on the Check your answers screen
- because: user request (the word "null" showed under the answers once every question was answered)
- files: scripts/page/app.js (kept() filter for the two Check your answers screens), tests/test_page.py (keyboard run asserts no "null"), plugin.json
- The hint for unanswered questions is left out as null, and the DOM's own replaceChildren writes null as text; h() already skipped it. The test failed first, passes now.

### C-20261030-1 · 2026-10-30 · 0.7.0: project label, copy continue prompt, listen bench, clearer question pages
- because: user request ("make a special area for playing sounds for voice comparison ... list what project this is for and a button to copy a prompt to continue the project and evaluate the answers ... clean up the design"), T-20261030-1
- files: ask.py (lint rules project, continue-prompt, media-text, media-option, media_layout listen; /api/set and /api/sessions carry project and continue_prompt; `new --project --project-path --continue-prompt --continue-prompt-file`), page/index.html, app.js, app.css (project line, copy button and toast, listen bench, option sound buttons, Shift+1..9 and b keys, question reading order), page/dashboard.* (project and copy button per card), references/schema.md, references/writing-questions.md (Voice comparisons), SKILL.md (Step 1, compact reviews), README.md, scripts/budget.py (install ceiling 280 KB), tests, plugin.json
- Design calls: ai-docs/decisions/2026-10-30-listen-bench-and-page-design.md.

### C-20261029-2 · 2026-10-29 · 0.6.0: contact.py and moving an existing review page onto sets
- because: user request (turn long pick pages into askwright screens), L-019, L-020, L-021
- files: scripts/contact.py (new), references/bridging.md (new), references/schema.md (Media items), tests/test_ask.py (ContactTests), LEARNINGS.md, plugin.json, ask.py VERSION
- contact.py puts candidates side by side in one labelled image (Pillow, optional); bridging.md says how to move a project's long review page onto sets and sync answers back to its picks file.

### C-20261029-1 · 2026-10-29 · back_link: a top-bar link back to the project's own review page
- because: user request (askwright pages opened from a project's pick page should lead back to it)
- files: ask.py (lint, /api/set, `new --back-link`), page/index.html and app.js (top bar), references/schema.md (The set), SKILL.md (Step 1), tests/test_ask.py (test_back_link), plugin.json 0.5.0
- A set may carry `back_link: {url, label}`; the page shows it beside "All sessions". The lint accepts only http(s) URLs with a label.

### C-20261026-4 · 2026-10-26 · Reopen bookmarked ports on Unix and tolerate stop cleanup races
- because: PR #19 CI on Linux and macOS
- files: ask.py (Server binding and server-info cleanup), tests/test_ask.py (exclusive bind and immediate restart)
- Unix servers can reuse their port after a connection closes, while Windows keeps exclusive address use. Neither platform permits two active listeners on one port. Concurrent stop and server cleanup tolerate an already-removed server.json.

### C-20261026-3 · 2026-10-26 · Integrate upstream study mode and add cross-feature regressions
- because: user request (tests and completing the pull-request workflow), upstream PRs #14 to #18
- files: ask.py (study routes, figures in self-check, rejected request bodies), page/app.js, SKILL.md, plugin.json, tests/test_ask.py, scripts/budget.py, merged documentation and metadata
- Preserve quiz grading and retakes, figure media, study captions and header/footer fixes alongside galleries and the dashboard. Added tests for quiz-key privacy in previews, preserving study attempts through dashboard actions, and rejecting unsupported POST routes without resetting the connection. Condensed the skill while preserving both workflows. The combined install is about 223 KB, so the install ceiling grows from 200 to 240 KB; the per-use skill ceiling stays 10 KB.

### C-20261026-2 · 2026-10-26 · 0.4.0: previews, snooze and archive for session cards
- because: user request
- files: ask.py (five-question previews and persistent session-state API), page/dashboard.html, dashboard.js, dashboard.css, README.md, plugin.json, tests/test_ask.py, tests/test_page.py
- Each session card previews up to five questions needing attention. Snooze hides the session for a chosen duration and returns it automatically. Snoozed and Archive lists have restore controls. State lives outside question sets, survives registration and restarts, and leaves answers untouched.

### C-20261026-1 · 2026-10-26 · 0.3.0: shared question-session inbox
- because: user request
- files: ask.py (registry, dashboard, register, session metadata and reopen API), page/dashboard.html, dashboard.js, dashboard.css, index.html, SKILL.md, schema.md, README.md, plugin.json, tests/test_ask.py, tests/test_page.py
- A master page lists registered sessions across local projects and agent products, with live attention counts, search, product filtering and an All sessions view. Creating or serving a set registers its canonical folder atomically. Stopped question pages reopen with their answers intact. The independent dashboard retains its port for bookmarks and uses the same loopback, Host, Origin and token protections as question pages.

### C-20261025-3 · 2026-10-25 · Review individual cases before deciding model policy
- because: user correction, L-014 `evidence-before-policy`
- files: SKILL.md (review granularity and synthesis), writing-questions.md, README.md, LEARNINGS.md, page/app.js, evals/evals.json, evals/check_set.py, tests/test_ask.py, tests/test_page.py
- Batch reviews now call for one question per frame/pair with Good / Keep / Reject checks and both/neither outcomes. Galleries remain available for supporting views or explicit aggregate judgments. Single-image comparisons retain a full-size link. The agent synthesizes per-case picks before recommending a model/default change.

### C-20261025-2 · 2026-10-25 · Compact image galleries and collapsed background
- because: user request, L-012 `compact-review-cases`
- files: page/app.js and app.css (case navigation, bounded images, native background disclosure), ask.py (media_layout and long-media lint), schema.md, writing-questions.md, SKILL.md, tests/test_ask.py, tests/test_page.py, evals/evals.json, README.md, plugin.json
- Three or more question images use a gallery automatically. Authors can request a gallery for two images or keep a simultaneous stack. Keyboard case navigation does not answer or change questions. Background starts collapsed and remembers expansion during page navigation. Authoring guidance distinguishes examples supporting one decision from independent questions.

### C-20261025-8 · 2026-10-25 · Header and footer bars whole again; cleaner header on laptop and phone
- because: user request (2026-10-25: the bars were cut off, "hard to see what question you're on and click the next button"), L-017 `class-name-collision`
- files: skills/askwright/scripts/page/app.css (header grid, track, notice, footer, phone rules, `.meter`), app.js (`topbar`, `showNotice`, the score meter), index.html (track), tests/test_page.py `test_bars_whole_at_laptop_and_phone_width`, .claude-plugin/plugin.json 0.2.1
- 0.2.0's per-topic score meter used the class `bar`, which the header and footer already used for their inner row, so both rows became an 8 px grey pill that clipped the title, progress, Back and Next on every set. The meter is now `.meter`. The header keeps the title to one line (full title on hover), puts the progress under it, and adds a thin track showing how much is answered; on a phone the counts and keyboard hints drop and the links share the progress line. The notice's Dismiss button sits at its right, `[hidden]` always hides, and the save status wraps instead of clipping.

### C-20261025-7 · 2026-10-25 · Three sentences in the shipped docs corrected before the 0.2.0 tag
- because: ai-docs/notes/2026-10-24-github-wiki.md "Inaccuracies found in the shipped docs" (1, 2 and 4)
- files: README.md "ask.py" and "Security", skills/askwright/references/schema.md "What comes back"
- `--version` and usage errors do not print JSON; the Origin is checked only on POST and only when sent (ask.py `origin_ok`); `read --all` gives unanswered questions the state `unanswered`. No behaviour changed.

### C-20261025-6 · 2026-10-25 · Figures: graphs, force diagrams and shapes drawn from JSON
- because: user request (2026-10-25: "askwright should be able to generate graphs or other images and shapes for questions")
- files: skills/askwright/scripts/ask.py (figure section, `check_media`, `page_set`, `self_check`, `figure` command), SKILL.md "Step 1", references/schema.md "Media items", references/study-mode.md, README.md, tests/fixtures/study, tests/test_ask.py FigureTests, tests/test_page.py `test_figure_draws_under_the_csp`
- A media item may hold `figure` (graph, forces or shapes) instead of `src`; ask.py lints it and sends the page an SVG data URL, which the existing CSP allows, so the page code is unchanged. `ask.py figure` saves one to look at.

### C-20261025-5 · 2026-10-25 · Study mode: option ids are aliased, two lint rules relaxed for quizzes
- because: L-015 `quiz-ids-leak-the-key`, L-016 `quiz-wording-rules`, T-20261025-3
- files: skills/askwright/scripts/ask.py `option_aliases`, `page_study`, `Handler.answer`, `lint_set` (question-mark, option-label), references/study-mode.md, references/schema.md "Study sets", tests/test_ask.py, tests/test_page.py
- The page now sees `o1`..`o4` in shown order instead of the author's option ids, and the server maps picks back. In a study set the question only has to contain a `?` (it may quote its sentence after the ask) and option labels are compared case-sensitively.

### C-20261025-4 · 2026-10-25 · 0.2.0: study mode, a quiz that teaches and grades
- because: user request (study-mode kickoff, 2026-10-25), decisions/2026-10-25-study-mode.md
- files: skills/askwright/scripts/ask.py (study lint, `study_score`, `study_review`, `/api/submit`, `/api/retake`, `grade`, study `read`/`status`, `inline` refusal), scripts/page/app.js and app.css (no extras, guess or note in a quiz; submit; review view; try again), SKILL.md "A quiz instead: study mode" and the description, references/study-mode.md (new), references/schema.md, tests/fixtures/study/, tests/test_ask.py (study classes), tests/test_page.py (StudyPageTests), evals/evals.json and evals/cases (trigger-study-quiz, decoy-explain-mistakes)
- `"mode": "study"` turns a set into a quiz: one `correct` option and a `why` on every option, a `topic` per question, optional written questions with a `rubric`. The server keeps the key until submit, shuffles options per attempt, scores on submit and keeps every attempt in results.json; `ask.py grade` lists written answers and writes grades back. Decision sets are unchanged.

### C-20261025-1 · 2026-10-25 · `ask.py add` takes a questions.json-shaped file
- because: L-011 `add-takes-questions-wrapper`
- files: skills/askwright/scripts/ask.py `cmd_add`, tests/test_ask.py `test_close_and_add`
- `add` now accepts `{"questions": [...]}` as well as a list or one question; before, the wrapper was linted as one blank question with seven errors that did not name the cause.

### C-20261024-4 · 2026-10-24 · 0.1.1: a link to the new wiki
- because: user request ("do the wiki now and tag")
- files: README.md "Documentation" (new), .claude-plugin/plugin.json and scripts/ask.py `VERSION`
- The README now points to the GitHub wiki, which holds every command's output, the lint rules with their messages, recipes and an FAQ, each example run against the 0.1.1 release zip. No behaviour changed.

### C-20261024-3 · 2026-10-24 · `randomized` is a fact about the clip, not a field to fill
- because: T-20261024-2 (outcome-question-quality failed 1 of 3 with the skill), L-005 `randomized-is-a-fact`
- files: skills/askwright/SKILL.md "Step 1: write the set" (Kinds), references/schema.md "A question" (`sides` row)
- The compare kind now says `randomized: true` only when the sides were drawn at random, and that a fixed-order clip gets `false` with the lint warning kept (or the pair remade). The eval cases changed with it: evals/check_set.py checks the sides match the clip instead of demanding `true`.

### C-20261024-2 · 2026-10-24 · Built askwright 0.1.0: ask.py, the page, the skill and both test suites
- because: user request (kickoff session 2), R-20261024-2 to R-20261024-6, the post-mortem's F1 to F12
- files: skills/askwright/SKILL.md, references/schema.md, references/writing-questions.md, scripts/ask.py, scripts/page/ (index.html, app.js, app.css), tests/test_ask.py, tests/test_page.py, tests/fixtures/, README.md, RESEARCH.md, evals/evals.json
- ask.py: lint (the plan's rules plus alt text and title length), serve (127.0.0.1, exclusive bind on Windows, Range, token, Host and Origin checks, self-check, --detach), status (--wait-done), read, close, add, inline, new, stop. The page: one question per screen, compare sides revealed after the pick, guess shown or hidden by confidence, notes with pasted images and timecodes, resume line, overview, check answers, keys. Small calls: ai-docs/decisions/2026-10-24-session2-build-calls.md.

## Release notes

### 0.4.0 (2026-10-26)
- Expandable previews of the next five questions per session.
- Snooze dropdown with timed return and an Unsnooze action.
- Archive list with Unarchive; dashboard organization persists across restarts.

### 0.3.0 (2026-10-26)
- Shared local dashboard for question sessions across projects and agent products.
- Automatic registration, live counts, session metadata and reopening stopped pages.
- Search, product filters and an All sessions view for answered rounds.

- Case-by-case image review with Previous/Next, a case selector and full-size links.
- Collapsed, expandable background and guidance for splitting long reviews into the right questions.
- Frame-level Good / Keep / Reject checks and individual picks before aggregate model-policy advice.

### 0.2.1 (2026-10-25)
- Fix: the header and footer were squashed into a thin grey strip in 0.2.0, cutting off the question number, Back and Next. The header is also tidier: the title stays on one line, a thin track shows progress, and phones lose the keyboard hints.

### 0.2.0 (2026-10-25)
- Study mode: `"mode": "study"` makes a quiz. Multiple-choice questions score on submit; the review shows the score, a score per topic, and for each question your answer, the right one and why each option is right or wrong. Written questions wait for `ask.py grade`. "Try again" reshuffles and keeps earlier attempts. The answer key never reaches the page before submit.
- Figures: graphs, force diagrams and simple shapes drawn from a few lines of JSON in any question (`"figure"` media).

### 0.1.1 (2026-10-24)
- The README links the new [wiki](https://github.com/m4bwav/askwright/wiki). No behaviour changed.

### 0.1.0 (2026-10-24)
- First version: question sets as data, the lint, the local page and the read-back. Windows and macOS, served to the local machine only.

### C-20261024-1 · 2026-10-24 · Created as an evergreen unit
- because: user request
- files: README.md, RESEARCH.md, LEARNINGS.md, evergreen.json (skills: also TESTS.md and evals/evals.json)
- Initial version. Tier `moderate`, interval 30d. See R-20261024-1 for the research basis; the first test run, for a skill, is logged in TESTS.md.
