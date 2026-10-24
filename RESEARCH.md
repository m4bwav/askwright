# Research: askwright

Findings that back [README.md](README.md) and the skill in [skills/askwright/](skills/askwright/SKILL.md). Changes they caused are logged in [CHANGELOG.md](CHANGELOG.md); procedural lessons live in [LEARNINGS.md](LEARNINGS.md); test runs and their evidence in [TESTS.md](TESTS.md); schedule and state in `evergreen.json`. Protocol: MAINTENANCE.md. The full tables of the creation pass (ids R-A, R-F, R-T, R-W) are in [ai-docs/research/](ai-docs/research/index.md).

Topic: Agents asking people to decide: question sets served as one-question-per-screen local pages with media, guesses, notes and pasted images, answers read back from disk; question wording, form practice, local media serving and browser testing. Tier `moderate`. Last refresh 2026-10-24; next due 2026-11-23.

## Current understanding

- **No existing tool does the whole job** (R-20261024-2). Built-in question tools are chat pickers with hard caps: AskUserQuestion takes 1-4 questions of 2-4 options with a 12-character header, hides the analysis above it, and is missing in subagents; Gemini's ask_user and Cursor's AskQuestion are similar or less reliable. MCP elicitation forms are flat (strings, numbers, enums) and the 2026-07-28 spec reworks them again. MCP Apps live inside one conversation and are not in Claude Code, Codex or Cursor. The nearest in use, mcp-feedback-enhanced, is one feedback box per call with no media in questions and had an unauthenticated-WebSocket command-execution bug. askwright's niche: many questions, media in the question, images in the answer, answers on disk read over hours, from any harness.
- **Vendors are moving to "ask, then keep working"**: Codex's `request_user_input` is now asynchronous and survives reconnects (R-A01). A file on disk with a revision counter is the portable version of that.
- **Answers must be keyed by a stable id**, never by position or question text; both break when a question is edited (R-A12). Silence is never an answer: AskUserQuestion once auto-continued after 60 s and was walked back (R-T06).
- **Form practice is settled** (R-20261024-3): one question per page with the question as the heading, nothing pre-selected, a check-answers page with Change links and "Not provided", a task list with status, buttons that name the next step, save-and-return (GOV.UK, GDS, NN/g). Survey method adds: split double-barrelled questions, avoid leading words, vary option order (primacy), keep a no-opinion option, and hide model identities until after a pairwise vote (Chatbot Arena). Defaults and visible advice anchor people even after they have judged (R-F11, R-F12), which is why a low-confidence guess waits behind a button.
- **Question quality can be checked, weakly, by a model** (R-20261024-4): LLMs applying QAS-99 agree with experts 63% of the time and under-flag clarity, so the 11-point rubric is a self-review step and an eval with a 3-run majority, not a lint rule.
- **The stdlib server needs three fixes** (R-20261024-5): `SimpleHTTPRequestHandler` never answers Range (Safari will not play video without a 206; Chrome plays but cannot seek), `HTTPServer` sets `SO_REUSEADDR` so on Windows a second server can take a busy port (use `allow_reuse_address = False` plus `SO_EXCLUSIVEADDRUSE`), and the handler follows symlinks out of its folder. `http://127.0.0.1:PORT` is a secure context; use the literal IP. The `paste` event with `clipboardData` needs no permission in any browser. H.264/AAC in MP4 plays everywhere.
- **Browser tests work with branded Chrome or Edge** (R-20261024-6): Playwright drives installed Chrome (H.264 plays), a synthetic `ClipboardEvent` carrying a `DataTransfer` delivers a pasted PNG, and vendored axe-core runs once the context bypasses the page's CSP.

## Open questions

- Plannotator (R-T09) overlaps for plan review; its repository was not read.
- Whether Claude Code now advertises MCP elicitation (R-A04), and Codex's official `request_user_input` schema: both matter only for a later native front-end.
- Synthetic paste under Playwright in Firefox and WebKit (only Chromium-family browsers were tested).
- Safari playback of the served media (Range is implemented and tested at the HTTP level; no Safari run yet).

## Search plan

Four tracks; every refresh runs at least one query on each (scope each to the period since the last refresh; add the year). Protocol §4 explains the tracks and how tooling, practice and testing findings are judged.

Subject (the goal and the latest thinking on reaching it):

- `AskUserQuestion changelog <month> <year>` on code.claude.com (tools reference, Agent SDK user input) and the claude-code issues mirror (claudeissues.com)
- `MCP elicitation OR "multi round-trip" specification <year>` on modelcontextprotocol.io (changelog first); `"MCP Apps" client matrix`
- `codex "request_user_input" changelog <year>`; `cursor AskQuestion forum <year>`
- `site:design-system.service.gov.uk` question pages, check answers, task list, radios (page updates)
- `python http.server Range OR SO_REUSEADDR changelog <year>` (CPython `Lib/http/server.py` and `Lib/socketserver.py` on main; the docs say nothing)
- Official forums: Claude Code issues (github.com/anthropics/claude-code/issues, mirrored at claudeissues.com), Cursor forum (forum.cursor.com, announcements), MCP specification discussions (github.com/modelcontextprotocol/modelcontextprotocol/discussions). Search announcements first, then known issues, since the last check.

Tooling (skills, plugins, MCP servers, scripts):

- `path:SKILL.md "decision page" OR "ask the user" OR "questions page"` on GitHub code search, recently updated; `npx skills find "ask user"`, skills.sh installs for "interview", "feedback", "review"
- `https://registry.modelcontextprotocol.io/v0/servers?search=feedback` and `?search=human`; fallback `"human in the loop" mcp server site:glama.ai`
- mcp-feedback-enhanced and askboard-mcp releases (security fixes, new answer types); Plannotator releases
- Supersession sweep: `"interactive feedback" mcp deprecated OR archived <year>`

Most discussed and the converged thinking:

- `hn.algolia.com/api/v1/search_by_date?query=AskUserQuestion` and `query=agent%20asks%20too%20many%20questions`
- Reddit r/ClaudeAI and r/ClaudeCode via RSS only (WebFetch is refused): "AskUserQuestion", "decision page"

Practice (how others use agents on this goal):

- `"AskUserQuestion" OR "ask_user" workflow blog <year>`; `"agent asks" clarifying questions too many OR too few <year>`
- `site:arxiv.org clarifying questions agent benchmark <year>` (AskBench, ClarEval and successors, R-T13)
- `site:frame.io OR site:help.frame.io commenting timecode` (review-tool conventions); Prodigy and Label Studio docs for answer keys

Testing (how this is verified):

- `playwright python release notes <year>` (playwright.dev/python/docs/release-notes) and `axe-core release <year>` (github.com/dequelabs/axe-core/releases)
- `"QAS-99" OR "question appraisal" LLM <year>` (Essex Survey Futures and successors)
- `path:SKILL.md "AskUserQuestion" evals OR benchmark` on GitHub

Best sources (primary first): code.claude.com docs and the claude-code issue mirror; modelcontextprotocol.io specification changelogs; CPython source on main; GOV.UK Design System; MDN; W3C WCAG 2.2; playwright.dev; dequelabs/axe-core. Sources that proved noisy: SEO form-builder listicles (swamp NN/g results; fetch nngroup.com URLs directly), Frame.io listicles, pewresearch.org (403 to WebFetch), skills.sh `?q=` (renders nothing).

## Findings log

Newest first. One entry per material finding; a quiet refresh gets one entry saying so. `Track` is subject, tooling, practice, or testing.

### R-20261024-6 · 2026-10-24 · Build verification (session 2)
- Summary: Playwright 1.63.0 with installed Chrome 155 and Edge 156 on Windows 11: H.264 fixture plays (readyState ≥ 2, currentTime advances); `new ClipboardEvent('paste', {clipboardData: dt})` with a `File` in a `DataTransfer` reaches a `document` paste listener and uploads; `set_input_files` covers the file-input fallback; axe-core 4.10.2 injected with `add_script_tag` needs `bypass_csp=True` because the page's CSP allows only same-origin scripts. Answers one open question from R-W14 (Chromium only).
- Track: testing
- Sources: tests/test_page.py runs in [TESTS.md](TESTS.md)
- Magnitude: n/a (initial)
- Applied: C-20261024-2

### R-20261024-5 · 2026-10-24 · Web platform and media (creation pass)
- Summary: http.server has no Range support and follows symlinks; `HTTPServer` sets SO_REUSEADDR (Windows port theft); Safari needs 206 for `bytes=0-1`; 127.0.0.1 is a secure context; the `paste` event is the dependable image route; H.264/AAC everywhere, HEVC and AV1 not; WCAG 2.2 AA targets. Entries R-W01 to R-W14.
- Track: subject
- Sources: [ai-docs/research/2026-10-24-web-platform-and-media.md](ai-docs/research/2026-10-24-web-platform-and-media.md) (CPython server.py and socketserver.py, MDN Clipboard API, WebKit bug 221622, WCAG 2.2)
- Magnitude: n/a (initial)
- Applied: C-20261024-2

### R-20261024-4 · 2026-10-24 · Review tools and testing (creation pass)
- Summary: review tools converge on one task per screen with keys for each answer, explicit tie and neither, and timecoded notes that pause playback (Prodigy, Label Studio, Chatbot Arena, Frame.io). AskUserQuestion's limits and its auto-continue incident. LLM question checkers under-flag clarity (QAS-99, 63% agreement); the 11-point rubric and the harness (Playwright, axe, judge with 3-run majority). Entries R-T01 to R-T13.
- Track: testing
- Sources: [ai-docs/research/2026-10-24-review-tools-and-testing.md](ai-docs/research/2026-10-24-review-tools-and-testing.md)
- Magnitude: n/a (initial)
- Applied: C-20261024-2

### R-20261024-3 · 2026-10-24 · Forms and survey practice (creation pass)
- Summary: GOV.UK one-thing-per-page, radios never pre-selected, check answers, task list, save progress; NN/g wizards name the next step; survey method on double-barrelled and leading questions, primacy, no-opinion options; default and advice anchoring; pairwise comparison with hidden identities; MADR and two-way-door decisions shape the one-pager. Entries R-F01 to R-F19.
- Track: practice
- Sources: [ai-docs/research/2026-10-24-forms-practice.md](ai-docs/research/2026-10-24-forms-practice.md)
- Magnitude: n/a (initial)
- Applied: C-20261024-2

### R-20261024-2 · 2026-10-24 · Agent question tools and prior art (creation pass)
- Summary: AskUserQuestion, MCP elicitation and Apps, Codex, Cursor, Gemini and VS Code question tools, and the human-in-the-loop MCP servers. Nothing in wide use covers many questions with media, images in answers and answers read over hours; mcp-feedback-enhanced's security history sets the server's guards (127.0.0.1, Host and Origin checks, a token, no command execution). Entries R-A01 to R-A13.
- Track: tooling
- Sources: [ai-docs/research/2026-10-24-agent-question-tools.md](ai-docs/research/2026-10-24-agent-question-tools.md)
- Magnitude: n/a (initial)
- Applied: C-20261024-2

### R-20261024-1 · 2026-10-24 · Creation pass
- Summary: four researchers in parallel on 2026-10-24 (subject, tooling, practice, testing) plus a post-mortem of the best hand-made decision page so far (failures F1 to F12, [ai-docs/notes/2026-10-24-hand-made-page-postmortem.md](ai-docs/notes/2026-10-24-hand-made-page-postmortem.md)). The plan built from them is [ai-docs/plans/2026-10-24-askwright-v0-plan.md](ai-docs/plans/2026-10-24-askwright-v0-plan.md). cost: searches 45 · fetches 79 · tool calls not recorded.
- Track: subject
- Sources: entries R-20261024-2 to R-20261024-5
- Magnitude: n/a (initial)
- Applied: C-20261024-1
