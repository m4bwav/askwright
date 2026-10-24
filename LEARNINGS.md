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

<!-- Example (delete once you have a real entry):
### L-001 · 2026-10-24 · One-line lesson in plain words
- Trigger: what happened, with dates or counts
- Hypothesis: why
- Rule: the shortest instruction that prevents the trigger
- Evidence: C-20261024-1, T-20261024-1, confirmed 2026-10-24
- Scope: skill | repo:<slug> | env:<name> | global
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-24
-->
