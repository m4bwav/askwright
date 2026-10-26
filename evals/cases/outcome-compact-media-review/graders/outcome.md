---
type: llm
name: compact-review
---

Inspect the question set written by the agent. PASS only when it contains one overall decision, six captioned
image cases together in media, media_layout either gallery or omitted/auto, background in one_pager, and the
critical consequence in why. It must pass ask.py lint. A reply describing a gallery without writing a set fails.
The deterministic checker is evals/check_set.py compact-media, run in the output directory.
