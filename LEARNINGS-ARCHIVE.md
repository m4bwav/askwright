# Learnings archive: askwright

Retired entries from [LEARNINGS.md](LEARNINGS.md), each with its reason. IDs are never reused.

### L-004 · 2026-10-24 · `chrome.exe --version` on Windows opens the running Chrome `chrome-version-windows`
- Trigger: asking for Chrome's version from the command line printed "Opening in existing browser session" and talked to the owner's open browser.
- Hypothesis: on Windows chrome.exe hands any command line to the running instance.
- Rule: read browser versions through Playwright (`browser.version`) or the file's version info, never by running chrome.exe.
- Evidence: session 2 transcript, confirmed 2026-10-24
- Scope: env:windows
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-24
- Retired 2026-11-15: environment fact, not an askwright rule; belongs in the evergreen ENVIRONMENTS profile

### L-009 · 2026-10-24 · `checks-watch-too-early`: `gh pr checks --watch` right after `gh pr create` returns before CI exists
- Trigger: the 0.1.1 pull request (#10) was created, watched and merged in one command; the watch printed "no checks reported" at once and the merge went through before CI started. CI passed afterwards (7/7 on main, and the release workflow runs the same checks before it publishes), so nothing broke
- Hypothesis: GitHub registers the workflow runs a few seconds after the push; `--watch` with no runs yet exits instead of waiting
- Rule: after creating a pull request, wait until `gh pr checks` lists the jobs (poll for a non-empty list) before `--watch`, and never chain the merge after a watch that printed "no checks reported"
- Evidence: PR #10, runs on 2026-10-25T03:03Z (UTC)
- Scope: repo:askwright
- Status: active · helpful 0 · harmful 0 · last_confirmed 2026-10-24
- Retired 2026-11-15: generic gh CLI behaviour, not specific to askwright; releasewright covers PR checks

### L-011 · 2026-10-25 · `add-takes-questions-wrapper`: `ask.py add` read a `{"questions": [...]}` file as one blank question
- Trigger: a film review round (one new question with two clips). The file was written in the shape of questions.json, `{"questions": [ {...} ]}`, as SKILL.md's `ask.py add <set> <questions.json>` suggests; add linted the wrapper itself as a question and failed with seven errors (id None, no kind, no title ...), none of which named the cause
- Hypothesis: cmd_add accepted a list or a single question object only
- Rule: add now also takes an object whose `questions` is a list; when an error lists every field as missing at once, suspect the file's shape before the question
- Evidence: test_ask.py add test (wrapped file adds `music4`); the round was added as a bare list before the fix
- Scope: skill
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-25
- Retired 2026-11-15: fixed in code: ask.py add accepts the {"questions": [...]} wrapper; no rule left to follow

### L-021 · 2026-10-29 · `contact-label-overlap`: fixed-size labels collided over narrow, tall candidates
- Trigger: 26 px labels ("1 (s11)") ran into each other over 80 px wide tower sprites; pixel art at 1x was also too small to judge
- Hypothesis: none needed; the label width did not depend on the cell
- Rule: size labels from the cell width and scale pixel art up (3x, nearest) in the contact image; contact.py does both
- Evidence: test_contact_sheet
- Scope: skill
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-29
- Retired 2026-11-15: fixed in code: contact.py sizes labels from cell width and scales pixel art

### L-014 · 2026-10-25 · Collect frame judgments before asking for a model-policy decision `evidence-before-policy`
- Trigger: after a long image review became a gallery, the owner still lacked per-frame success/failure explanations and asked why the page requested one model decision instead of individual frame picks.
- Hypothesis: the layout was improved without changing the premature decision granularity; general business context displaced concrete visual inspection instructions.
- Rule: review one frame/pair per question with the requested change, source references, and Good / Keep / Reject checks tied to visible objects and locations. Offer both-usable and neither-usable outcomes. Summarize the resulting picks and failure patterns before recommending a model role or asking for policy approval.
- Evidence: user correction, C-20261025-3; frame-review outcome checker and the corrected individual-review rounds.
- Scope: skill
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-25
- Retired 2026-11-15: merged into L-012

### L-022 · 2026-10-30 · `media-query-change-is-async`: a test read the top bar before the menu move ran
- Trigger: test_bars_whole_at_laptop_and_phone_width resized 1100 to 390 px and measured at once; the secondary chips were still in the row (off screen), so it failed although the page was right
- Hypothesis: a matchMedia `change` event fires at the next rendering step, after Playwright's set_viewport_size returns
- Rule: after resizing, wait for the state the media-query handler sets (here `#more` hidden or not) before measuring; layout that JS moves on resize is not there yet
- Evidence: the same test passed with the wait, and tests/test_visual.py (fresh contexts at each width) passed first time
- Scope: repo tests
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-30
- Retired 2026-11-15: merged into L-017

### L-031 · 2026-11-14 · `tool-applies-without-consume`: a tool that acts on answers must record the use itself
The week warning named six steerwright weekly reviews. All six had been applied on 2026-11-09 (`applied.json` in each set), but `sw.py apply-review` never ran `ask.py consume`, so askwright saw unused answers. Any plugin that reads askwright answers and acts on them should run `consume` in the same step; steerwright 0.5.1 does. Check a set's folder for a tool's own marker before calling it unprocessed.
- Retired 2026-11-15: merged into L-028

### L-032 · 2026-11-15 · `read-is-not-consume`: a warning must say what clears it
The session-start week warning named the same three sets for days although sessions were asked to clean them up. Each session ran sweep and `ask.py read` on them (09:12 reads in their uses.jsonl), and reading never clears a set; the only exit was `consume`, which claims the answers were used. Two sets also held a backfilled consume stamped minutes before their answers. A nag must name the command that ends it, and the owner needs a way to drop an item without lying about it: `ask.py dismiss` (0.32.0).
- Retired 2026-11-15: merged into L-028

- 2026-11-13 `hand-edited-set-fails-on-open`: an agent appended questions to questions.json by hand (confidence "medium", no background); nothing linted it until the dashboard refused to open it. Use `ask.py add`, which lints first; "medium" now only warns.
- Retired 2026-11-15: fixed in code (ask.py add lints first; "medium" confidence only warns)
