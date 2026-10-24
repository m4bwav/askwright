---
kind: research
title: Review tools, agent-asking practice and testing (creation pass, practice and testing tracks)
date: 2026-10-24
tags: [research, labelling, prodigy, frame-io, askuserquestion, testing, qas-99, llm-judge]
---

# Review tools, agent-asking practice and testing (creation pass, 2026-10-24)

Practice and testing tracks. 13 searches, 15 fetches. Thin spots: Argilla's key bindings come from a search snippet only, and Scale and Surge rubrics, Q-Bank, cognitive interviewing and Reddit were not reached. The QAS-99 codes come from the July 2026 Essex paper; codes 7f, 7g and 8 are from memory, not read.

## Findings

| R | Date | Source | Finding | Weight |
|---|---|---|---|---|
| R-T01 | current | [Prodigy web app docs](https://prodi.gy/docs/api-web-app) | One task at a time, with three answers: accept `a`, reject `x`, ignore `space`. Undo with `backspace`, flag `f`, help `h`. Choice screens use `1`-`9`, and keys can be remapped. A side panel shows progress and the last 10 decisions; clicking one brings that task back to the front. Skip and undo are first-class answers with their own keys. | high |
| R-T02 | current | [Label Studio Pairwise](https://labelstud.io/tags/pairwise), [Choice](https://labelstud.io/tags/choice) | Pairwise works over any media but has no tie (the docs suggest a separate Choices tag). Each choice can have a hotkey, and Ctrl/Cmd+Enter submits. A comparison needs an explicit tie and "neither". | med |
| R-T03 | 2024-03-07 | [Chatbot Arena](https://arxiv.org/abs/2403.04132) | Votes are A, B, tie and both bad. The paper does not state how sides are randomized. Randomizing sides and recording them is our own inference. | med |
| R-T04 | 2026-09-09 | [Frame.io commenting](https://help.frame.io/en/articles/9105251-commenting-on-your-media) | Typing a comment pauses playback and pins the comment to the current timecode; a toggle removes the timecode for a whole-clip note. `I`/`O` set a range, and clicking the note replays it. Drawings go on the paused frame. Store a note as `{t, t_end?, text, image?}`. | high |
| R-T05 | current | [Agent SDK, AskUserQuestion](https://code.claude.com/docs/en/agent-sdk/approvals) | 1-4 questions, 2-4 options, a header of at most 12 characters, and not available in subagents. `preview` is TypeScript-only and strips scripts. Answers are keyed by question text, with Other as free text. The docs send forms, wizards and review UIs to custom tools: that gap is askwright's reason to exist. | high |
| R-T06 | 2026-07-02 | [claude-code #73125](https://claudeissues.com/issue/73125-bug-askuserquestion-no-response-after-60s-continued-without-an-answer) | v2.1.198 auto-continued after 60 s without an answer and was made configurable after complaints. "No answer" must never count as an answer; it stays "unanswered, still waiting". | med |
| R-T07 | 2026-08-25 | [#89644](https://claudeissues.com/issue/89644-ux-askuserquestion-modal-hides-upstream-context-forcing-decisions-on-option-summ), [#12420](https://claudeissues.com/issue/12420-bug-askuserquestion-tool-limited-to-4-options-is-too-restrictive), [#62304](https://claudeissues.com/issue/62304-verbosity-fix-gate-on-decision-load-per-response-not-line-count) | The AskUserQuestion modal hides the analysis above it, so people decide from option summaries. Users also complain about the four-option cap and about option fatigue. Every screen must carry its own context. | med |
| R-T08 | 2026-05 | [Thariq Shihipar, The Unreasonable Effectiveness of HTML](https://thariqs.github.io/html-effectiveness/) | Agent-made HTML pages for comparisons and triage, with the rule "always end with an export button". Critics note that a script-bearing page can carry injected prompts. Keep a "copy answers" fallback and treat what comes back as data. | med |
| R-T09 | 2026-07-27 | [Plannotator docs](https://docs.plannotator.ai/open-source/reference/keyboard-shortcuts) | Open-source plan, document and code review for coding agents, with image annotation; feedback goes back to the calling agent. It has an "interview answers" flow. This is the nearest existing tool. Its repo was not read; see [the tooling track](2026-10-24-agent-question-tools.md). | med |
| R-T10 | current | [Argilla annotate](https://docs.argilla.io/dev/how_to_guides/annotate/) | Records one at a time (Focus) or as a list (Bulk), with Submit, Save as draft and Discard on keys. Partial sets survive closing the browser. | low |
| R-T11 | 2026-07 | [Essex Survey Futures WP22, LLM applying QAS-99](https://www.iser.essex.ac.uk/wp-content/uploads/files/working-papers/survey-futures/sf-wp-22-survey-question-evaluation-scale-applying-llm-to-qas-99.pdf) | QAS-99 is 27 yes/no codes in 8 steps. LLMs agree with experts 63% of the time (AC1 0.36) and with each other 83%. They under-flag, with clarity (step 3) weakest, and miss social desirability. One yes/no per code, a reason for every "yes", and codes reworded as questions worked; Tao et al. 2024 add few-shot examples and a vote over several runs. | high |
| R-T12 | current | [Playwright accessibility testing](https://playwright.dev/docs/accessibility-testing) | Scan with axe-core under the WCAG 2.x A/AA tags. Scan each screen after it is revealed, and snapshot rule ids with their selectors. Many problems still need manual checks. | med |
| R-T13 | 2026 | [AskBench](https://arxiv.org/abs/2602.11199), [ClarEval](https://arxiv.org/pdf/2603.00187), [Ask Early, Ask Late](https://arxiv.org/pdf/2605.07937) | Agents ask too rarely or too much: on underspecified tasks GPT-5.2 asked in 52% of sessions, Sonnet 4.5 in 23% and Gemini 3 Flash never. Evals should test both directions: ask on real decisions, decide trivial ones. | med |

## Question-clarity rubric (yes/no flags, a reason required for each yes)

1. Double-barrelled: two decisions in one question (QAS 4c).
2. Vague or undefined term: jargon, take ids, or "better" without "better at what" (3b, 3c).
3. Missing context: the screen alone does not let you answer, because the media, the why, or what each option changes is missing (1b, R-T07).
4. Inappropriate assumption: it presumes something not yet decided (4a).
5. Leading: it signals an answer, or the guess is presented as a default (6b, 6c).
6. Bad options: options overlap, tie, neither, other or skip is missing, the order is illogical, or labels are vague (7c-7g).
7. Answer-type mismatch: free text where a choice belongs, or the reverse (7b).
8. Recall burden: the reader must remember an earlier clip instead of seeing both (5c, 5d).
9. Complex syntax or tangled instructions (3a, 2a, 2b).
10. Trivial: the agent should have decided and flagged it (R-T13, Mark's rule).
11. No labelled agent guess.

## Harness

- **Playwright (dev only):**
  - exactly one `[data-q]:visible`
  - the whole set can be finished by keyboard (number keys, space to skip, backspace to undo, Enter for next)
  - the progress text updates
  - typing a note pauses the video and records `currentTime` to within ±0.1 s
  - a pasted image is stored by the server
  - axe runs on each screen
- **Server contract (stdlib unittest):**
  - every answer is saved at once
  - after a kill, the next start resumes
  - unanswered questions stay unanswered
  - the server binds to 127.0.0.1 only
- **Question-quality eval:** the rubric above as an LLM judge, majority of 3 runs, with seeded bad and good sets.
- **Ask-behaviour eval:** a real decision must be asked; a trivial one must not be.

## Open

- Read Plannotator's repo: installs, how answers return, evals.
- Label Studio and Argilla skip and draft key bindings, from the live UI.
- The original QAS-99 manual text (try https://www.cdc.gov/healthyyouth/evaluation/pdf/brief15.pdf).

## Search notes

The claudeissues.com mirror of anthropics/claude-code issues works. For Hacker News use hn.algolia.com directly. WebFetch is blocked on Reddit (RSS route only). The Essex PDF reads through Read with page ranges. Frame.io listicles are noise.
