# Learnings: askwright

Procedural lessons for [README.md](README.md). Research findings live in [RESEARCH.md](RESEARCH.md); every change is logged in [CHANGELOG.md](CHANGELOG.md); test runs in [TESTS.md](TESTS.md); state in `evergreen.json`. Format and write-time gate: MAINTENANCE.md (LEARNINGS-FORMAT). Retired entries go to LEARNINGS-ARCHIVE.md with a reason.

Write an entry the moment a real signal happens: a user correction, the same error twice, a discovered workaround, an environment fact, a stated preference, a failed test or a failure in use. Check existing entries first, by meaning (`evergreen.py search "<the lesson>" --kinds learnings` finds near-duplicates in every registered unit): add / update / retire / none. Trigger and Hypothesis are required. Promote after three confirmations; retire when harmful > helpful.

## Active

### L-001 · 2026-10-24 · Drain the request body before answering 413 `drain-before-413`
- Trigger: the oversized-upload test got ConnectionAbortedError on Windows instead of a 413: the server replied and closed while the client was still sending.
- Hypothesis: closing a socket with unread data makes Windows reset the connection, so the response is lost.
- Rule: on a too-large request, read and discard the body (bounded at 4x the cap) before sending the error.
- Evidence: tests/test_ask.py test_attachment_size_cap, C-20261024-2, confirmed 2026-10-24
- Scope: skill
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-24

### L-002 · 2026-10-24 · Page tests: CSP blocks injected axe; a disabled fieldset is not "disabled" `playwright-csp-fieldset`
- Trigger: axe injected with add_script_tag is inline script, which the page's CSP refuses; and Playwright's is_disabled() returned False for a `<fieldset disabled>`.
- Hypothesis: add_script_tag(path=) inlines the file; Playwright's disabled check covers controls, not the fieldset element itself.
- Rule: open page-test contexts with bypass_csp=True (keep one test without it for console errors), and assert disabled on a control inside the fieldset.
- Evidence: tests/test_page.py, R-20261024-6, confirmed 2026-10-24
- Scope: skill
- Status: active · helpful 2 · harmful 0 · last_confirmed 2026-10-24

### L-003 · 2026-10-24 · Prove the page on real media, not only fixtures `real-media-check`
- Trigger: every test passed on the 160x90 fixture clip, but the first real side-by-side pair showed each take about 360 px wide in the text column.
- Hypothesis: fixtures check behaviour, not fit; real review media is wide.
- Rule: after a page change, screenshot one real set (ASKW_SET copy) at desktop and phone widths before calling it done.
- Evidence: ai-docs/decisions/2026-10-24-session2-build-calls.md B9, confirmed 2026-10-24
- Scope: skill
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-24

### L-004 · 2026-10-24 · `chrome.exe --version` on Windows opens the running Chrome `chrome-version-windows`
- Trigger: asking for Chrome's version from the command line printed "Opening in existing browser session" and talked to the owner's open browser.
- Hypothesis: on Windows chrome.exe hands any command line to the running instance.
- Rule: read browser versions through Playwright (`browser.version`) or the file's version info, never by running chrome.exe.
- Evidence: session 2 transcript, confirmed 2026-10-24
- Scope: env:windows
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-24

### L-005 · 2026-10-24 · `randomized` states a fact about the clip; never set it to quiet the lint `randomized-is-a-fact`
- Trigger: on a clip the prompt said had take 3 always on the left, 1 of 3 eval runs wrote `sides.randomized: true` (the other two wrote false and kept the lint warning). The session-2 eval case demanded `true` too.
- Hypothesis: SKILL.md said "give `sides` with `randomized: true`", which reads as a field to fill, and the lint warns when it is false.
- Rule: `randomized: true` only when the sides were drawn at random (a pair tool did it); a clip with a known fixed order gets `false`, and the warning stays or the pair is remade in random order.
- Evidence: T-20261024-2 (outcome-question-quality, with run 1), C-20261024-3
- Scope: skill
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-24

### L-006 · 2026-10-24 · `claude plugin eval` writes machine paths into `evals/results/`; run the guard before every commit, not only before the push `eval-results-leak`
- Trigger: a `git add -A` after a plugin eval run committed `evals/results/<stamp>/` (the repo's local path and temp trace paths), and the branch was pushed to the public repository before `tests/check_skills.py` ran. The branch was squashed clean and deleted; the closed pull request still holds the old commit.
- Hypothesis: the results folder was not ignored, and the guard ran only at the end.
- Rule: `evals/results/` is git-ignored; run `python tests/check_skills.py` before each commit on a branch that will be pushed, and stage paths by name after an eval run.
- Evidence: T-20261024-2, the closed pull request #2
- Scope: repo:askwright
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-24

### L-007 · 2026-10-24 · `caller-ids-must-pass-lint`: an id a caller derives from a filename must pass the id rule
- Trigger: the first real film review through a caller's pair tool: the output named `_pair_r7.mp4` became question id `_pair_r7`, the lint refused it (ids start with a letter or digit), and the set came up empty
- Hypothesis: callers build ids from file stems, and underscore-prefixed scratch names are common
- Rule: callers that derive ids strip leading `_`, `-` and `.`; the failure printed the rule, so keep error messages naming the id pattern
- Evidence: caller fix merged the same day; set served and self-checked after it
- Scope: skill
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-24

### L-008 · 2026-10-24 · `pick-without-reason`: a pick against the guess with an empty note teaches the agent nothing
- Trigger: the first real film review (one compare question, two takes, guess hidden at low confidence). The owner visited, answered 53 s later and left: he picked the take the guess advised against (the one with a lens-look), with no note, no timecode, guess never revealed
- Hypothesis: the pick was unbiased and quick, which is what the page is for, but the page gives no nudge toward a reason, so the agent cannot tell whether lens-looks are acceptable in a wide battle shot or the other take's flaw (spearmen falling, not running) was simply worse
- Rule: when a guess is wrong and the note is empty, record the pick as a fact and do not invent a reason; do not turn a review criterion into a rule from one silent pick. A possible page change (an optional one-line "why?" shown only when the pick differs from the hidden guess) is an open decision for the owner, not a default
- Evidence: the set's answers.json and events.jsonl (visit 21:25:16, answer 21:26:09), kept in the private sidecar
- Scope: skill
- Status: active · helpful 0 · harmful 0 · last_confirmed 2026-10-24

### L-009 · 2026-10-24 · `checks-watch-too-early`: `gh pr checks --watch` right after `gh pr create` returns before CI exists
- Trigger: the 0.1.1 pull request (#10) was created, watched and merged in one command; the watch printed "no checks reported" at once and the merge went through before CI started. CI passed afterwards (7/7 on main, and the release workflow runs the same checks before it publishes), so nothing broke
- Hypothesis: GitHub registers the workflow runs a few seconds after the push; `--watch` with no runs yet exits instead of waiting
- Rule: after creating a pull request, wait until `gh pr checks` lists the jobs (poll for a non-empty list) before `--watch`, and never chain the merge after a watch that printed "no checks reported"
- Evidence: PR #10, runs on 2026-10-25T03:03Z (UTC)
- Scope: repo:askwright
- Status: active · helpful 0 · harmful 0 · last_confirmed 2026-10-24

### L-010 · 2026-10-25 · `double-ask-or-is-either-or`: the double-ask lint flags a one-choice "keep A, or cut B?" question
- Trigger: a film review set (6 questions, a 2G shot's end point). "Should 2G keep the whole fall and him lying on the floor, or cut as he lands?" got the `double-ask` warning. It is one decision between two exclusive end points, and its two options were exactly those two. It was reworded to "Where should 2G end?", which passed
- Hypothesis: `DOUBLE_ASK` matches "or" before a verb ("or cut"), as it does "and" before a verb. "And" joins two asks; "or" usually offers the alternatives of one ask, which the options then list
- Rule: when the warning hits an either/or between the question's own options, reword it as an open question ("Where should it end?", "Which ...?") and let the options carry the alternatives; that wording is clearer anyway. Whether the lint should stop flagging "or" when the two sides match the options is an open decision for the owner, not a default
- Evidence: the set's questions.json before and after the rewording, lint output (1 warning, then 0), kept with the film's files
- Scope: skill
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-25

### L-011 · 2026-10-25 · `add-takes-questions-wrapper`: `ask.py add` read a `{"questions": [...]}` file as one blank question
- Trigger: a film review round (one new question with two clips). The file was written in the shape of questions.json, `{"questions": [ {...} ]}`, as SKILL.md's `ask.py add <set> <questions.json>` suggests; add linted the wrapper itself as a question and failed with seven errors (id None, no kind, no title ...), none of which named the cause
- Hypothesis: cmd_add accepted a list or a single question object only
- Rule: add now also takes an object whose `questions` is a list; when an error lists every field as missing at once, suspect the file's shape before the question
- Evidence: test_ask.py add test (wrapped file adds `music4`); the round was added as a bare list before the fix
- Scope: skill
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-25

### L-015 · 2026-10-25 · `quiz-ids-leak-the-key`: option ids in a quiz page give the answer away
- Trigger: the first real quiz (22 questions) went to a fresh agent for a cold take with the key stripped. It flagged that ids such as `right`, `no-comma` and `double-neg` would sit in the page as radio values, readable in devtools or by anyone who reads the HTML
- Hypothesis: authors name option ids after what the option is, and in a quiz that is the answer; stripping `correct` and `why` was not enough
- Rule: a study page never gets author ids. The server sends `o1`, `o2`... in shown order and maps picks back (`option_aliases`); test that no real id reaches the DOM
- Evidence: T-20261025-3 (test_key_is_hidden_until_submit_then_scored, StudyPageTests ids check)
- Scope: skill
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-25

### L-016 · 2026-10-25 · `quiz-wording-rules`: two decision-set lint rules were wrong for quizzes
- Trigger: the first real quiz failed lint with 7 errors: six questions quoted their sentence after the ask (`Which word is the verb? "..."`), and a capital-letter question had options that differ only by "We"/"we", reported as repeated labels
- Hypothesis: the rules were written for decisions, where a question ends in `?` and labels that differ only by case are duplicates
- Rule: in study mode the question only has to contain a `?`, and labels compare case-sensitively. When a new mode reuses lint, run a real set through it before trusting each rule
- Evidence: lint output before and after; test_quiz_wording_rules
- Scope: skill
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-25

### L-017 · 2026-10-25 · `class-name-collision`: a new component reused the layout class `bar`
- Trigger: after 0.2.0 the header and footer on every set were an 8 px grey pill cutting off the title, progress, Back and Next; the owner saw it on a live quiz at laptop and phone width
- Hypothesis: a browser or screenshot quirk; it was a global `.bar` rule from the study score meter (height .5rem, overflow hidden) landing on the bars' inner rows
- Rule: before adding a class in app.css, grep app.css, app.js and index.html for it; name components by what they are (`meter`, `track`). Every page change gets a viewport screenshot at laptop and phone width, not only full-page shots, which also misplace fixed bars
- Evidence: test_bars_whole_at_laptop_and_phone_width fails at 14 px with the old rule and passes with `.meter`
- Scope: skill
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-25

<!-- Example (delete once you have a real entry):
### L-001 · 2026-10-24 · One-line lesson in plain words
- Trigger: what happened, with dates or counts
- Hypothesis: why
- Rule: the shortest instruction that prevents the trigger
- Evidence: C-20261024-1, T-20261024-1, confirmed 2026-10-24
- Scope: skill | repo:<slug> | env:<name> | global
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-24
-->
