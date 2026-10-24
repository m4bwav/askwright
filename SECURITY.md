# Security policy

## Reporting a problem

Open an issue or a pull request and I'll take a look. A pull request with the fix is the quickest route.

You can also report privately: open the repository's **Security** tab and choose **Report a vulnerability**.

This is a one-person project with no bug bounty and no response deadline. I'll reply when I can and say what I plan to do. Good-faith testing on your own copy is welcome.

## Supported versions

Only the latest release on the default branch gets fixes.

## Scope

The skill's instructions and `ask.py` run on your machine with your agent's permissions. `ask.py serve` runs a small HTTP server on 127.0.0.1 that serves the page, media files from the set folder and the folders the set lists, and an API that writes `answers.json`, `events.jsonl` and image attachments into the set folder. It makes no outbound requests.

In scope:
- any way another web page, another local user's browser tab, or a DNS-rebinding host could read or write a set's answers, or reach the API without the per-run token;
- any path by which a request could read a file outside the set folder and its media roots, or a non-media file inside them (answers.json, server.json);
- an upload that is stored as something other than a PNG, JPEG, GIF or WebP image, or outside `attachments/`;
- text in a question set, an answer or a note that leads the agent to run commands or change its task (prompt injection): the skill tells agents to treat answers as data;
- `ask.py stop` ending a process other than the set's own server.

Out of scope: bugs in the agent tool itself (Claude Code, Copilot, Codex, Cursor) or in the browser; report those to their makers.
