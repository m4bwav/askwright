---
kind: research
title: How agents ask people questions, and what already exists (creation pass, subject and tooling tracks)
date: 2026-10-24
tags: [research, askuserquestion, mcp-elicitation, codex, cursor, gemini, mcp-apps, prior-art]
---

# How agents ask people questions (creation pass, 2026-10-24)

Subject and tooling tracks. 12 searches, 21 fetches.

## Findings

| R | Date | Source | Finding | Weight |
|---|---|---|---|---|
| R-A01 | 2026-10-23 | [Codex changelog](https://learn.chatgpt.com/docs/changelog), [secondary on v0.154](https://codex.danielvaughan.com/2026/09/05/async-tui-questions-codex-cli-v0154-human-agent-collaboration/) | Codex `request_user_input` questions are now asynchronous: a question stays pending while the agent keeps working, can be skipped, and survives a reconnect. 0.164.0 renders it as Markdown. It is off by default outside Plan mode. Vendors are moving toward "ask, then keep working", which is askwright's model. | med |
| R-A02 | 2026-07-28 | [MCP 2026-07-28 changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog), [2025-11-25 elicitation](https://modelcontextprotocol.io/specification/2025-11-25/client/elicitation) | Elicitation becomes Multi Round-Trip Requests: the server returns `input_required` and the client retries with `inputResponses`. Sessions and the initialize handshake go away. Forms stay flat and primitive (string formats, numbers, booleans, enums), with accept, decline or cancel. URL mode hands over a page but returns no answer in-band. An MCP front-end would chase two spec revisions; files avoid that. | med |
| R-A03 | current | [Agent SDK user input](https://code.claude.com/docs/en/agent-sdk/user-input), [tools reference](https://code.claude.com/docs/en/tools-reference), [hooks](https://code.claude.com/docs/en/hooks) | AskUserQuestion takes 1-4 questions with 2-4 options, a header of at most 12 characters, `multiSelect`, Other and notes. `preview` (markdown or HTML, no script) works through the SDK only. It is not available in subagents. `askUserQuestionTimeout` can auto-continue. A PreToolUse hook can answer it itself (`updatedInput.answers`), and in `-p` mode `defer` ends the turn with `tool_deferred` and no timeout, picked up by `claude -p --resume`. | high |
| R-A04 | 2026-03 to now | [hooks](https://code.claude.com/docs/en/hooks), [issue 65572](https://claudeissues.com/issue/65572-claude-code-does-not-advertise-elicitation-mcp-capability-despite-elicitation-ho) | Claude Code supports elicitation (v2.1.76) with Elicitation and ElicitationResult hooks, and has `agent_needs_input` and `idle_prompt` notifications. An issue says v2.1.163 did not advertise the capability. | low |
| R-A05 | 2026-08-12 | [Cursor forum 165742](https://forum.cursor.com/t/ask-tool-disapear/165742), [161150](https://forum.cursor.com/t/cursor-agent-keeps-skipping-questions-in-plan-mode/161150) | Cursor's AskQuestion is a Plan-mode picker that is switched off for some models, so questions fall back to chat. Users report skipped questions and too many questions. The built-in tools are unreliable across models. | low |
| R-A06 | 2026-06-18 | [Gemini CLI ask_user](https://geminicli.com/docs/tools/ask-user/) | 1-4 questions with a header of at most 16 characters, `type` choice, text or yesno, 2-4 options. Answers are keyed by position. Gemini CLI has been replaced by Antigravity CLI. | low |
| R-A07 | current | [VS Code tools reference](https://code.visualstudio.com/docs/agents/reference/tools-reference), [MCP servers](https://code.visualstudio.com/docs/agent-customization/mcp-servers) | `#vscode/askQuestions` (local harness only). MCP Apps forms are experimental. | low |
| R-A08 | 2026-01-26 | [MCP Apps](https://modelcontextprotocol.io/extensions/apps/overview), [client matrix](https://modelcontextprotocol.io/extensions/client-matrix) | `ui://` HTML in a sandboxed iframe. Supported in Claude web and Desktop, VS Code Copilot, Goose and others, but not Claude Code, Codex or Cursor. It lives inside one conversation, which does not suit answering over hours. A possible later second front-end. | med |
| R-A09 | 2026-08 | [mcp-feedback-enhanced](https://github.com/Minidoracat/mcp-feedback-enhanced) | About 3.8k stars. A web UI with text, image paste and drag, an auto-submit timer, and local history. One feedback box per call, no video or audio in questions, no documented resume. v2.6.1 removed command execution after an unauthenticated WebSocket allowed arbitrary commands, and added an Origin check. The README itself says native elicitation and MCP Apps replaced its original reason to exist. Lessons: 127.0.0.1 only, an Origin and Host check, a token, no command execution. | med |
| R-A10 | 2026-08-13 | [askboard-mcp](https://github.com/qinsehm1128/askboard-mcp) | A form with single, multi and text fields, history in `~/.askboard-mcp`, and editable past answers. `get_updates(revision)` returns what changed since a revision, which is worth copying. Tiny and inactive. | low |
| R-A11 | varies | [interactive-feedback-mcp](https://glama.ai/mcp/servers/wbg9ovxwq4), [gotoHuman](https://glama.ai/mcp/servers/@gotohuman/gotohuman-mcp-server), [HumanLayer](https://github.com/humanlayer/humanlayer) | All narrower than askwright. gotoHuman is hosted and needs an account; HumanLayer moved into agent orchestration. | low |
| R-A12 | current | [LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts), [Agent Inbox](https://docsearch.algolia.com/mcp/docs/repo/langchain-ai/agent-inbox) | Interrupts persist under a `thread_id` and resume with `Command(resume=...)`. Resume values are matched by index, so ordering must be deterministic, and side effects must be idempotent. Agent Inbox's actions are ignore, respond, edit and accept. Key answers by a stable question id, never by position or text: Claude keys answers by text and Gemini by index, and both break when a question is edited. | med |
| R-A13 | current | [deep-interview](https://claudemarketplaces.com/skills/yeachan-heo/oh-my-claudecode/deep-interview), [interrogate](https://claudskills.com/skills/interrogate/) | Interview skills ask in chat or through AskUserQuestion. No skill was found that serves a local page with media. | low |

## Verdict on prior art

Nothing well-used does the whole job. That job is many questions, one per screen, media in the question, pasted images in the answer, and answers on disk that are read over hours, from any harness. mcp-feedback-enhanced is the nearest in use. It is one box per call and MCP-bound, uses FastAPI and WebSocket, and has a security history, so askwright is built new and learns from its guards. Plannotator ([review-tools research](2026-10-24-review-tools-and-testing.md), R-T09) overlaps for plan review and was not read in full; read it in session 2.

## Design consequences

- The question JSON is a superset of the AskUserQuestion shape (question, header, options with label and description, multiSelect), with Gemini-like types added. A set of up to 4 simple text questions can then be put to the native tool instead of a page.
- Answers are keyed by a stable `id`.
- A file is the checkpoint, and a revision counter lets the agent ask "what changed since rev N".
- Later, not in v0: a PreToolUse hook that routes AskUserQuestion to the page, a `defer` + `--resume` mode for headless runs, and an MCP Apps view.

## Open

- Codex `request_user_input` official schema.
- Cursor elicitation support.
- Whether Claude Code now advertises elicitation.
