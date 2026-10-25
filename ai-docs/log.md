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
