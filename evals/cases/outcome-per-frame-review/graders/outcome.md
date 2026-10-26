---
type: llm
name: observations-first
---

Inspect the written question set. PASS only when there are six frame-specific picks rather than one model-policy
question. Each case needs its requested change, source/comparison media, concrete Good / Keep / Reject checks,
and both-usable and neither-usable choices. The agent must defer model/default advice until those answers exist.
The set must lint and pass evals/check_set.py frame-review. Describing this plan without writing the set fails.
