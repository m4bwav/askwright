# Learnings: askwright

Procedural lessons for [README.md](README.md). Research findings live in [RESEARCH.md](RESEARCH.md); every change is logged in [CHANGELOG.md](CHANGELOG.md); test runs in [TESTS.md](TESTS.md); state in `evergreen.json`. Format and write-time gate: MAINTENANCE.md (LEARNINGS-FORMAT). Retired entries go to LEARNINGS-ARCHIVE.md with a reason.

Write an entry the moment a real signal happens: a user correction, the same error twice, a discovered workaround, an environment fact, a stated preference, a failed test or a failure in use. Check existing entries first, by meaning (`evergreen.py search "<the lesson>" --kinds learnings` finds near-duplicates in every registered unit): add / update / retire / none. Trigger and Hypothesis are required. Promote after three confirmations; retire when harmful > helpful.

## Active

### L-012 · 2026-10-25 · Keep image reviews compact and split decisions at their real boundaries `compact-review-cases`
- Trigger: a real review question stacked ten comparison sheets vertically; the owner asked for case-by-case slides and collapsible background.
- Hypothesis: one question per page still demands excessive scrolling when every example and all background are expanded together.
- Rule: choose the unit of judgment before using a gallery (L-014). A gallery is for supporting views or an explicitly requested aggregate judgment, not a substitute for individual review picks. Keep comparisons together, start background collapsed, and check desktop and phone layouts with real media.
- Evidence: user request, C-20261025-2; page and lint regression tests cover gallery navigation and background disclosure.
- Scope: skill
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-25

### L-014 · 2026-10-25 · Collect frame judgments before asking for a model-policy decision `evidence-before-policy`
- Trigger: after a long image review became a gallery, the owner still lacked per-frame success/failure explanations and asked why the page requested one model decision instead of individual frame picks.
- Hypothesis: the layout was improved without changing the premature decision granularity; general business context displaced concrete visual inspection instructions.
- Rule: review one frame/pair per question with the requested change, source references, and Good / Keep / Reject checks tied to visible objects and locations. Offer both-usable and neither-usable outcomes. Summarize the resulting picks and failure patterns before recommending a model role or asking for policy approval.
- Evidence: user correction, C-20261025-3; frame-review outcome checker and the corrected individual-review rounds.
- Scope: skill
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-25

### L-013 · 2026-10-25 · A refused eval sandbox is a harness block, not a skill verdict `eval-sandbox-required`
- Trigger: the compact-review eval initially lacked tool grants; granting its declared shell tool caused the Windows runner to refuse all three runs because its sandbox backend was unavailable.
- Hypothesis: model-level outcomes cannot be measured when the runner cannot safely grant the tools the case requires.
- Rule: grant declared tools explicitly, keep the sandbox requirement, and report unavailable-backend runs as blocked. Do not weaken sandbox settings or count infrastructure refusals as measured skill failures. Run deterministic repository and browser checks separately.
- Evidence: T-20261025-1; the eval runner reported sandbox required but unavailable before execution.
- Scope: repo:askwright
- Status: active · helpful 0 · harmful 0 · last_confirmed 2026-10-25

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

### L-018 · 2026-10-29 · `skill-body-budget`: a two-line SKILL.md addition failed CI on every OS
- Trigger: PR #20 failed the size budget on all six jobs; two lines on `--back-link` put the SKILL.md body at 10279 bytes (red). Python 3.9 on ubuntu-latest also failed: the image is Ubuntu 26.04 and has no 3.9 build
- Hypothesis: the tests were broken; the body is already at the budget edge, and the runner image moved
- Rule: run `python scripts/budget.py` before pushing a SKILL.md change and put detail in references/schema.md, not SKILL.md. Python 3.9 runs on ubuntu-24.04 (matrix exclude/include, as pixelwright does)
- Evidence: budget 10164 bytes (yellow) after a one-line version; CI 7/7 on PR #20
- Scope: repo:askwright
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-29

### L-019 · 2026-10-29 · `long-pick-page`: a scrolling page of every candidate is too long to answer
- Trigger: the owner opened a 26-item pick page and a 30-card review sheet (each item 4 to 8 candidate images, one long scroll), answered one item in six days, and asked for them to become askwright screens
- Hypothesis: the items were hard to judge; the page length was the blocker, since nothing showed progress or let the owner stop and come back on the same item
- Rule: when a project already has a long review page, move its items onto sets (references/bridging.md): one item per screen, candidates in one labelled image (scripts/contact.py), sets of about 10, answers synced back to the project's picks file so its tools are unchanged
- Evidence: 5 sets from 55 items, round trip tested on a copy of the picks file; the owner's request on 2026-10-29
- Scope: skill
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-29

### L-020 · 2026-10-29 · `placeholder-guess`: a converted set first shipped "no guess made" on every question
- Trigger: a bridge script filled the required guess with a placeholder for every item that had no earlier pick
- Hypothesis: guessing 40 image picks was too costly; one montage per 10 items took three image reads and gave real guesses, and showed two items where every candidate missed the owner's earlier note
- Rule: look at the candidates and write real low-confidence guesses (a qid -> guess file); put the owner's earlier notes in `hint`; a re-roll that still misses the note gets the "re-render" guess
- Evidence: 42 guesses from three montages; two re-roll rounds found against the owner's notes
- Scope: skill
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-29

### L-021 · 2026-10-29 · `contact-label-overlap`: fixed-size labels collided over narrow, tall candidates
- Trigger: 26 px labels ("1 (s11)") ran into each other over 80 px wide tower sprites; pixel art at 1x was also too small to judge
- Hypothesis: none needed; the label width did not depend on the cell
- Rule: size labels from the cell width and scale pixel art up (3x, nearest) in the contact image; contact.py does both
- Evidence: test_contact_sheet
- Scope: skill
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-29

### L-022 · 2026-10-30 · `media-query-change-is-async`: a test read the top bar before the menu move ran
- Trigger: test_bars_whole_at_laptop_and_phone_width resized 1100 to 390 px and measured at once; the secondary chips were still in the row (off screen), so it failed although the page was right
- Hypothesis: a matchMedia `change` event fires at the next rendering step, after Playwright's set_viewport_size returns
- Rule: after resizing, wait for the state the media-query handler sets (here `#more` hidden or not) before measuring; layout that JS moves on resize is not there yet
- Evidence: the same test passed with the wait, and tests/test_visual.py (fresh contexts at each width) passed first time
- Scope: repo tests
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-30

### L-023 · 2026-10-31 · `verify-scripts-leak-registry`: wiki-verify scripts registered temp sets on the real dashboard
- Trigger: 8 of 27 entries in ~/.askwright/sessions pointed at deleted AppData Temp folders (`ask/takes`, `set`), dated 10-26 to 10-31.
- Hypothesis: ai-docs/notes/*-wiki-verify.py run `ask.py serve` (which registers) without setting ASKWRIGHT_HOME; the unit tests already isolate it.
- Rule: any script that runs ask.py against throwaway sets sets ASKWRIGHT_HOME to a temp folder first.
- Evidence: C-20261031-7, entries removed 2026-10-31, both verify scripts now set it.
- Scope: repo:askwright
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-31

<!-- Example (delete once you have a real entry):
### L-001 · 2026-10-24 · One-line lesson in plain words
- Trigger: what happened, with dates or counts
- Hypothesis: why
- Rule: the shortest instruction that prevents the trigger
- Evidence: C-20261024-1, T-20261024-1, confirmed 2026-10-24
- Scope: skill | repo:<slug> | env:<name> | global
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-24
-->
