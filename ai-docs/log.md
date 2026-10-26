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
