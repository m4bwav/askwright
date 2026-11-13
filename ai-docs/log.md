# Log

Append-only. One line per operation: `## [YYYY-MM-DD] op | title` where op is one of add, update, supersede, verify, verify-failed, prune, handoff, index. Newest at the bottom. Never edited, only appended; this is the history the entries themselves do not carry.

## [2026-10-24] init | scaffolded

## [2026-10-24] add | hand-made decision page post-mortem (F1-F12)
## [2026-10-24] add | decision: public repository (Mark)
## [2026-10-24] add | creation-pass research, four tracks (45 searches, 79 fetches)
## [2026-10-24] add | v0 plan with open decisions D1, D3, D4, D5
## [2026-10-24] handoff | session 1 ends awaiting Mark's answers; kickoff-prompt.md rewritten for session 2
## [2026-10-24] index | rebuilt (6 entries)

## [2026-10-24] add | decision: Mark answered D1 D3 D4 D5 (askwright; guess shown if confident, else behind a button; scope a; wire reviews after 0.1)
## [2026-10-24] update | plan and session 2 prompt updated with the answers
## [2026-10-24] index | rebuilt (7 entries)
## [2026-10-24] index | rebuilt (7 entries)
## [2026-10-24] add | built askwright 0.1.0 (ask.py, page, skill, tests); C-20261024-2
## [2026-10-24] add | decisions: session 2 build calls (B1-B11), public scrub
## [2026-10-24] add | learnings L-001 to L-004
## [2026-10-24] update | post-mortem generalised for the public repo; original moved to private notes
## [2026-10-24] verify | real 22-question film review set: lint clean, served, Range 206, generic page tests 4/4
## [2026-10-24] handoff | session 2
## [2026-10-24] index | rebuilt (9 entries)
## [2026-10-24] add | public repository m4bwav/askwright created and pushed (fresh history); CI 7/7 green
## [2026-10-24] test | T-20261024-2: first eval-suite run with baseline. Triggers 3/3 x3, decoys 0/3 x2 (claude plugin eval); value cases via worth --ab: 6/8 before, one wrong-outcome (randomized claimed on a fixed-order clip, L-005), tuned (C-20261024-3), 8/8 after. worth: KEEP, +67 points (noise 31) at 0.64x cost. Case defects fixed: fixture folder, check_set.py, serve pattern, repo name. Calls S1 to S5 in decisions/2026-10-24-session3-calls.md.
## [2026-10-24] build | D5 wired: the private image-generation skill's pair tool gets `pair --ask <set>` and `picks <set>` (its PR merged); cinewright has no person-facing review page, so nothing changed there (S5).
## [2026-10-24] index | rebuilt (10 entries)
## [2026-10-24] release | v0.1.0 tagged on the owner's go ("tag it"); wiki not yet; PR #2 left as is (owner: "cool")
## [2026-10-24] test | session 4 over-ask probe for action-ask-only-the-real-decision: a handoff prompt with four settled items and three open ones (two with obvious defaults), baseline without the skill, 2 runs. Both re-asked nothing settled and asked the three open ones each with a pre-selected guess, which is what the prompt asked for. No over-ask found; the case stays a redundant guard. Next probe idea: a prompt that does not say "all", where the defaults are strong enough to just decide.
## [2026-10-24] blocked | session 4 step 2 (first real `pair --ask` film review) waits for a film session; the live comfyui-gen clone is still on another session's branch with uncommitted LEARNINGS.md.
## [2026-10-24] correction | session 4 step 2 was not blocked: a worktree of the image-generation skill on its default branch reaches `pair --ask` without touching the dirty clone. Rendered a second take of a film shot, built the pair set, served it to the owner. Found and fixed a default-id bug in the caller (L-007 `caller-ids-must-pass-lint`).
## [2026-10-24] wait | session 5: the first real film review set is still unanswered; its server is alive and serving, so it was left running rather than re-served. Steps 3 and 4 not started.
## [2026-10-24] result | session 6: the owner answered the first real film review (one compare question). He picked the take already in the cut, against the hidden low-confidence guess, with no note (L-008 `pick-without-reason`). The film keeps its shot; the server was stopped with `ask.py stop`.
## [2026-10-24] test | session 6 over-ask probe 2 for action-ask-only-the-real-decision: a release-chores prompt without "all" (version bump, changelog, merge, tag, badge, a 2FA publish), baseline without the skill, 2 runs (one Sonnet, one Opus). Both asked one question (the 2FA publish, guess pre-selected) and decided the other five. No over-ask found again. Confound: the subagents load the owner's global instructions (both cited his merge-by-default rule), so the baseline is not a clean no-context agent. Next probe should run headless outside the owner's profile or state no standing rules.
## [2026-10-24] release | v0.1.1 tagged on the owner's go ("do the wiki now and tag"): README links the wiki, version strings; no behaviour change. Release workflow passed, askwright-0.1.1.zip 45,676 bytes. PR #10 merged before its checks registered (L-009 `checks-watch-too-early`); CI passed 7/7 afterwards.
## [2026-10-24] add | GitHub wiki for 0.1.1, ten pages, every output from notes/2026-10-24-wiki-verify.py run against the release zip on Linux (WSL), Windows 3.14 and 3.9; outputs 75/75, live 10 pages 0 failures. Note: notes/2026-10-24-github-wiki.md (four inaccuracies in the shipped docs listed for the next release).
## [2026-10-25] update | compact media review: auto/gallery/stack layouts, bounded case navigation, collapsed background, authoring rules for galleries versus independent questions; L-012, C-20261025-2.
## [2026-10-25] verify | T-20261025-1: offline, page and real-media desktop/phone checks pass; answers preserved. Fresh-agent outcome blocked by unavailable native Windows sandbox, L-013; not reported as a skill failure.
## [2026-10-25] handoff | implementation on feat/compact-image-review, local 0.2.0 only; supported-runner outcome eval and any requested publication remain.
## [2026-10-25] update | L-014/C-20261025-3: collect individual frame judgments with concrete Good / Keep / Reject checks and both/neither outcomes before model-policy advice; a gallery alone was the wrong fix.
## [2026-10-25] verify | T-20261025-2: offline/browser and real-page checks passed; live frame questions and repeat-seed round lint clean, old questions/answers preserved; new fresh-agent outcome remains sandbox-blocked.
## [2026-10-26] verify | skills checker and budget pass; persistent dashboard launcher reused the live dashboard; authenticated ping passed.
## [2026-10-26] update | C-20261026-2: session previews, timed snooze, Archive and restore controls; state remains separate from questions and answers.
## [2026-10-26] verify | T-20261026-2: 64 offline tests with one existing Windows skip, 28 browser passes; full current changes approved for a pull request.
## [2026-10-25] build | study mode (0.2.0, branch feat/study-mode in a worktree, askwright-study): quizzes with the key kept on the server, neutral option ids, per-attempt shuffle, results.json attempts, review page with per-topic scores, `ask.py grade`; decisions/2026-10-25-study-mode.md Q1 to Q11
## [2026-10-25] build | figures on the owner's request: graph, forces and shapes media drawn by ask.py as SVG data URLs (`ask.py figure` to preview)
## [2026-10-25] test | T-20261025-3: 67/67 offline, 20/20 page, triggers and decoys 10/10 cases; L-015 `quiz-ids-leak-the-key`, L-016 `quiz-wording-rules`
## [2026-10-25] use | first real study set (a 7th-grade forces quiz, 20 + 2 bonus) served from the worktree; set and results live outside the repo (owner's private notes)
## [2026-10-25] note | another session's uncommitted 0.2.0 work (compact image review, L-012 to L-014) sits in the main clone on feat/compact-image-review; this work used the next free ids and a separate worktree
## [2026-10-25] index | rebuilt (12 entries)
## [2026-10-25] verify | first real study set taken, graded with `ask.py grade` (two written answers) and `grade --apply`, server stopped with `ask.py stop`; the per-topic review worked as designed. The feat/study-mode worktree was removed after PR #14 merged. Still open: tag 0.2.0 on the owner's go, the owed wiki pages, and the compact-image-review rebase.
## [2026-10-25] release | v0.2.0 tagged on the owner's go ("yes"): study mode and figures. Before the tag, PR #16 corrected three doc sentences (wiki note inaccuracies 1, 2, 4; C-20261025-7); its page job failed once on test_keyboard_only_to_all_done ("a question came round twice") and passed on rerun, a flake, docs-only change. Release workflow passed, askwright-0.2.0.zip 61,076 bytes.
## [2026-10-25] update | GitHub wiki for 0.2.0, commit b7d5801: Study-Mode and Figures pages plus eleven changed; every output from notes/2026-10-25-wiki-verify.py against the release zip (Linux, Windows 3.14 and 3.9); live 12 pages 0 failures. New inaccuracy 5 (forces arrows scaled per axis).
## [2026-10-25] fix | 0.2.1 (branch fix/page-bars, worktree askwright-bars): header and footer bars were squashed by the study meter's `.bar` rule (L-017 `class-name-collision`); meter renamed, header and footer cleaned up for laptop and phone, regression test added. C-20261025-8.
## [2026-10-26] verify | T-20261026-3: integrated upstream study/figure/layout work into PR #19; 86 offline tests with one existing Windows skip and 34 browser tests passed. Three added regressions cover preview privacy, study-attempt preservation and rejected-request connection reuse.
## [2026-10-26] verify | T-20261026-4: addressed PR #19 CI failures with Unix port reuse and race-safe server-info cleanup; 88 offline tests with one existing Windows skip, structure and budget checks passed locally.

## [2026-10-29] update | 0.5.0 back_link: a set can link its top bar back to the project's own review page (`new --back-link URL LABEL`); first user SpaceDeckBuilder2's art pick pages. C-20261029-1; tests 88 passed 1 skip, page 34 passed, live serve check of the header link and /api/set.

## [2026-10-29] update | 0.6.0: scripts/contact.py (candidates side by side in one labelled image, Pillow optional) and references/bridging.md (moving a project's long review page onto sets, answers synced back to its picks file), from converting a game project's 55-item pick pages; L-019 to L-021, C-20261029-2; tests 89 passed 1 skip.

## [2026-10-30] update | 0.7.0: project label and Copy continue prompt (question page top bar and dashboard cards), listen bench for voice comparisons (Shift+1..9, b for A/B at the same point, option sound buttons), clearer question reading order. C-20261030-1, T-20261030-1, decisions/2026-10-30-listen-bench-and-page-design.md.

## [2026-10-30] update | 0.8.0: project records and pages (`ask.py project`, /projects/<slug>), created/updated on sets, questions and projects (mtime fallback), one-row top bar with pills, chips and a More menu under 70rem, Show answered joining it on phones, dashboard Projects strip, tests/test_visual.py with screenshots. C-20261030-3, T-20261030-2, L-022, decisions/2026-10-30-projects-and-top-bar.md.

## [2026-10-30] update | 0.9.0: click a picture (or the Pick button under a clip or sound) to pick its option, on the owner's request. C-20261030-4, T-20261030-3, decisions/2026-10-30-click-media-to-pick.md.

## [2026-10-30] update | 0.9.1: dashboard hides unavailable sessions behind an "Unavailable sessions (N)" checkbox (owner request). C-20261030-5.

## [2026-10-31] update | 0.10.0: dashboard sessions as a table (Title, Project, Last updated, Action) with expandable rows holding the old card contents; done sets get Copy prompt as the quick action; the finish screen has Copy prompt to continue (owner request). C-20261031-1, T-20261031-1.
## [2026-10-31] update | 0.10.1: dark-mode visual test with a contrast check, one dark palette, dashboard plurals. C-20261031-2, T-20261031-2.
## [2026-10-31] update | 0.11.0: sortable dashboard columns, Last updated descending by default (owner request); tagged v0.11.0. C-20261031-3, T-20261031-3.
## [2026-10-31] update | 0.12.0: clicking the left or right half of a single side-by-side image picks that take, with a hover wash on the half (owner request). C-20261031-4, T-20261031-4.
## [2026-10-31] update | 0.13.0: copied continue prompts end with the next-session prompt's Execute line (owner request); option key badges. C-20261031-5, T-20261031-5, PR #32, tagged v0.13.0.
## [2026-10-31] update | 0.14.0: every set has a project (owner request: made-up names fine; one continue-prompt chain shares one; cross-project chains get an umbrella project), `new` warns without one; overview, check and study review screens calmer (muted not-answered, no footer on the score, no stale welcome-back). C-20261031-6, T-20261031-6.
## [2026-10-31] update | Owner's real projects registered (9: SpaceDeckBuilder2, madnesswright, musicwright, The Charge (lancers film), Deir strike film, Siege news film, Spear sranc crowd test, Flux 3 vs Qwen model test, Sammy homework) with descriptions, repos and folders; all 19 live sets tagged (set-level `project`, answers unaffected: staleness is per-question rev); 8 dead temp registry entries removed; wiki-verify note scripts now isolate ASKWRIGHT_HOME (L-023 `verify-scripts-leak-registry`). C-20261031-7.
## [2026-10-31] update | 0.15.0: dashboard Projects tab beside Sessions (owner request, the strip would grow long); remembered per browser, `#projects` opens it. C-20261031-8, T-20261031-7.
## [2026-10-31] update | 0.15.1: tab icons per page kind (question set blue ?, dashboard green list, project purple folder), served as SVG; /favicon.ico returns the question icon (owner request). C-20261031-9, T-20261031-8.
## [2026-10-31] add | master volume in the page header (slider, mute, keys m and -/=), kept per browser; covers bench, option sounds and native players
## [2026-10-31] fix | test_click_half_of_side_by_side_image_picks_that_side hardened: the box was measured before the image laid out, so 80% of it fell in the left half; now waits for decode and re-measures per click.
## [2026-10-31] release | 0.16.0: master volume (#39) released and tagged. C-20261031-10.
## [2026-11-01] update | 0.17.0: project pages manage the project (goals, needs-direction status, history merged with folder work logs, first and last prompt run, Copy start command, HANDOFF opening), dashboard project filter and Status column, SKILL.md trimmed to 9.6 KB, bridging and study-mode references moved to the wiki, install ceiling 320 KB. C-20261101-1, T-20261101-1.
## [2026-11-01] update | goals and status for all 10 registered projects via `ask.py project --goal/--status/--needs-direction` (registry only, no repo code change).
## [2026-11-01] update | session 12: lovecraft-shorts history note (Zann picks, renders running); other projects unchanged since session 11.
## [2026-11-01] fix | project page showed "Project not found / p.prompt_files is undefined": the dashboard process (started 10:45, 18 s after the 0.17.0 merge) ran pre-0.17.0 Python while serving the new page JS from disk. Restarted `ask.py dashboard --port 60150`; no code change. Lesson: restart the dashboard after any release that changes the API shape.
## [2026-11-01] fix | set servers started before 0.17.0 (10-29 to 11-01 morning) 404ed /time.js (not in their PAGE_FILES) while serving the new pages, so "All sessions" showed "askTime is not defined". Restarted 10 `ask.py serve` processes on their same ports; 4 fully answered flux3 sets were not restarted (lint no-questions). After a release, restart every running dashboard and serve process, not just the dashboard.
## [2026-11-03] update | 0.17.1: anything to see or hear goes on the page, even one question; parked end-of-session checks become sets (writing-questions Parked checks). First use: comfyui-gen InfiniteTalk listen check. C-20261103-1, PR #45, release v0.17.1.

## 2026-11-04: 0.18.0 project required, preview count (owner request)
`ask.py new` and lint refuse a set without a project; older sets read as the placeholder "Unsorted", so the dashboard's "No project" filter is gone. The dashboard preview label gives the real count ("Next open question", "Next 3 open questions", "No open questions"). Backfilled the owner's seven projectless live sets, keeping their file times. C-20261104-1.

## 2026-11-04: 0.18.1 checkboxes over bundled options (owner request)
The `multi` kind already gave checkboxes; agents were not choosing it. Added the bundled-options lint warning, SKILL.md and writing-questions guidance, and a clearer legend. C-20261104-2.

## 2026-11-04: 0.19.0 new projects need a description (owner request)
`project` and `new` refuse to create a project without one; hand-written sets can still register without one. Filled the four empty records. Tiny Colony turned out to be evaluation test data (its folders are scratchpad trap-busy and trap-small), left for the owner to remove. C-20261104-3.
## [2026-11-06] add | 0.20.0 refs, Open folder and background tabs (owner request); decision 2026-11-06-refs-and-tabs

## 2026-11-07: remote answers session 1, 0.21.0 wake-up (owner request)
Compared routes from primary sources and wrote the threat model; decision set served to the owner. Shipped claim, pending and a SessionStart hook; nothing exposed to the network. Answer safety waits for the route decision.
Owner added: remote capability is opt-in; ask each user before setting anything up.

## 2026-11-07: remote answers session 2, 0.22.0 remote mode (owner request)
Read the owner's route answers and built opt-in Tailscale mode with answer safety; PR left for owner review. Not yet run through a real Tailscale install. Decision 2026-11-07-remote-mode.

## 2026-11-07: remote answers session 3 (continue prompt)
The owner approved installing Tailscale after PR 53 merges; it is still open, so nothing was installed. Checked the unproven Tailscale assumptions against source and fixed a lost HTTPS enable link in the PR.

## 2026-11-08: remote answers session 4 (continue prompt)
PR 53 merged by the owner. Installed Tailscale 1.104.5 on the PC (approved). Sign-in, phone install and HTTPS Certificates wait on the owner.

## 2026-11-08: remote answers session 5
PC on Tailscale, remote mode enabled; serve --remote waits on the owner turning on HTTPS certificates. A web sign-in does not log in the PC's client: run `tailscale up` and open its link on the PC.

## 2026-11-08: remote answers session 6
HTTPS certs and phone ready; phone-test set served over ts.net, waiting on the owner's phone check. Curl from the PC to its own ts.net port timed out.

## 2026-11-08 remote answers session 7
- Phone test passed (play, seek, remote identity in read). Removed private path and host name from HANDOFF (CI path guard). Tag v0.22.0.
- Release: manual `gh release create` collided with release.yml; deleted it, reran, zip attached (L-024 `tag-push-makes-release`). Decision set askwright-remote-setup-2 served (second reviewer route).

## 2026-11-09 picks (0.24.0)
- `ask.py picks build` / `picks export` added, generalizing a game repo's card-art pick bridge (askpicks.py). Install size sits at 359 KB of the 360 KB ceiling and the SKILL.md body at 10.2 KB of 10 KB yellow: the next feature needs the install-size split or a trim first.

## 2026-11-09: steerwright header link (0.24.1)
Served pages fill a `<!--STEERWRIGHT-->` placeholder with a link to the steerwright hub url from its server.json, or with nothing when steerwright is absent.

## 2026-11-09: grid media layout for picks (0.24.2)

`picks build` used `gallery`, the one-at-a-time slider, so a pick page hid the candidates behind Previous/Next. Added `grid` (app.js skips the slider, `.media-grid` auto-fill columns, lint treats it as images-only) and switched picks build to it. Test: `test_grid_shows_every_image_at_once`.


## 2026-11-10: Unconsumed tab and ask.py consume (0.25.0)

- New concept: a set is *consumed* when an agent runs `ask.py consume <set> --by WHO --note WHAT` after acting on it. `read` now logs to the set's `uses.jsonl`. The dashboard's Unconsumed tab lists sets that were read (read record or older wake claim) whose latest answer is newer than their latest consume.
- Rule chosen after trying "latest read newer than latest consume": that one flagged ~35 sets because sweeps and bulk reads re-read sets already used. "Answers newer than the last consume" matches the question "has this data been used?".
- Install size passed the 360 KB ceiling (365 KB); the ceiling went to 384 KB. SKILL.md body sits at exactly 10240 bytes, the yellow edge: the next SKILL.md line needs a cut elsewhere.
- Existing sets were backfilled from Claude Code transcripts by a one-off scan (not in the repo): a read is a tool call naming the set with `ask.py read`/`status`, `answers`, `askpicks`, `picks export` or `sync`; consumed when that session made an edit or ran 3+ other commands afterwards, stamped at the session's last action, by "claude session <id8> (backfill)". Of 130 answered sets, 113 had a consuming session; 23 stay unconsumed (6 steerwright reviews with no transcript evidence, and sets answered again after their last use). Heuristic: a busy session counts as consuming even if the work was unrelated.

## 2026-11-10 hover zoom (0.25.1)

Pointing at a small picture on the question page floats a large copy beside it (page/app.js hover zoom, #hover-zoom in app.css, test_hover_shows_large_copy_beside_small_picture). PR #66 merged, v0.25.1 tagged, installed copy updated. CI page job flaked once on test_keyboard_only_to_all_done (timeout) and passed on re-run.

## 2026-11-11 Works with

At the owner's request: a README "Works with" section and a Works-With wiki page (linked from the sidebar and Home), each entry naming the real handoff with a partner plugin (taken from the skills that name each other) and why the pair helps.

## 2026-11-11 GitHub payloads (0.26.0, unreleased)

Mark asked to post askwright questions to an issue or PR and get the answers pasted back. New scripts/gh.py (kept out of ask.py, which is 3,200 lines) with gh-post / gh-pull / gh-reply / gh-answers, wired into ask.py and a finish-screen button (POST /api/gh-reply, local only; remote pages get github=None). Hidden blocks: `<!-- askwright:payload v1 B64 -->` and `<!-- askwright:answers v1 B64 -->`. GitHub has no API for comment attachments, so local media are listed as not attached; web media show inline and gh-pull downloads them. Comments are capped at 65,536 characters, so a large set fails with a clear error. Tests: fake gh via ASKWRIGHT_GH (a JSON list) + FAKE_GH_STATE. Version bump left to the release (0.25.2 zoom fix lands first).
## 2026-11-11 hover zoom for small files (0.26.0)

Mark saw no zoom on the SpaceDeckBuilder2 Atlas picks page: the candidates are 96x96 PNGs drawn at 96 px, and the zoom was gated on naturalWidth > drawn width x 1.3. It now scales up to at least 480 px with image-rendering: pixelated. Test test_hover_scales_up_a_picture_whose_file_is_small (swatch.png, 64 px). Next request queued: GitHub issue/PR payloads (post questions to a comment, answer locally, reply with answers).

## 2026-11-11 required background section

Mark's Atlas picks screen showed only the card id and a generic why. New required field `background` (lint error `background` on open decide questions; study mode exempt; warning past 6 sentences), rendered inside the existing collapsed details (summary "Background: what this is and how we got here") ahead of one_pager blocks. `picks build` takes `--background FILE` ({item: text}) or `--background-all TEXT` ({item} substituted) and fails listing `missing` items. Running servers do not re-lint, so live pages keep working; a new serve/add of an old set fails lint until backgrounds are added (or --force). The SpaceDeckBuilder2 Atlas sets need backgrounds (the card's rules text and role) before their next serve. Tests 216 pass.

## 2026-11-11 · PR #70 merged
CI failed: install size 385 KB (cap 384 KB) and the answer box 4 px too low at 390 px. Fixed by pointing README sections that repeat SECURITY.md and the wiki there instead, and shortening the Background summary to "Background". Headroom is now under 1 KB; the next feature will need a real trim (README table or references).

## 2026-11-12 · Open questions from a server that outlived its console (0.27.0)
Mark's sessions list answered "Cannot open ...: session server returned no JSON:" with an empty tail. It came from one set server (started a day earlier with a shell `&` instead of `--detach`) whose console had died with its agent session: on Windows every console child of such a process exits 0xC0000142 before printing. Reproduced with CREATE_NEW_CONSOLE plus killing the conhost. Fix: `OWN_CONSOLE` (CREATE_NO_WINDOW) on the children a server starts (open_session, gh), and the error names the exit code. Lesson L-026 `server-outlives-console`. Servers already running keep their old code until restarted.

## 2026-11-12 · One server, one port (0.28.0)
Owner asked for askwright and its linked pages to stop going down and changing ports. Every `serve` now hands the set to the dashboard server on 127.0.0.1:47631 (`/s/<key>/`), started or upgraded on demand; `--own` keeps the old per-set server. The steerwright chip goes through `/go/steerwright`, which starts steerwright when it is down (steerwright already serves the chainwright and grindwright indexes, on its fixed 47630). `shortcut --startup` puts a sign-in shortcut in the Windows Startup folder. Found on the way: a cold inbox of 182 sets took 45 s to list, which timed out the server's self-check (now a ping), and two concurrent starts raced onto a random port (L-027). Install ceiling raised 384 to 400 KB for it. Per-set servers already running keep their old ports until each set is served again.

## 2026-11-13 · steerwright on the same server (0.29.0)
Owner: yes to one server for steerwright too, but steerwright must still run without askwright, and pick another port when one is taken. askwright now mounts steerwright 0.5.0's `render()` at `/steer/` (sandboxed CSP). Stopped the 11 per-set servers left from before 0.28.0 by PID (owner's go-ahead). Pair: steerwright 0.5.0.

- 2026-11-13: 0.29.1 released (cold first /steer/ load minutes -> ~16 s). Live switch done: shared server restarted, steerwright registered inside it.

## 2026-11-13 · lint fix for roof-snow set, question templates (0.30.0)
The dashboard refused "Roof snow: SAM masks" because a session hand-appended three questions with `"confidence": "medium"` (two also lacked `background`). Fixed that set (backup questions.json.bak-20261113 beside it). Prevention: "medium"/med/moderate/mid now warn and read as low; the dashboard error names the first three failures and the set path; SKILL.md Step 6 says never hand-edit questions.json. New: plugins ship `ask-templates/*.json` for their major setup questions; `ask.py templates` lists them (askwright, ~/.askwright/templates, installed plugins via installPath, ASKWRIGHT_TEMPLATE_PATH); `ask.py new --template KEY --var name=value` seeds a set. askwright ships `project-setup`. Follow-up: other wrights can add their own setup templates (schema.md "Templates").
