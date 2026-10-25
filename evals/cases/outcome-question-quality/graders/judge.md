---
type: llm
name: 'expectations'
---

PASS if the reply meets every one of these:
- deterministic: `ask.py lint <set> --no-probe` prints ok: true (evals/check_set.py quality)
- deterministic: the compare question's sides match the clip (take 3 left, take 7 right), it does not claim randomized: true for a fixed-order clip, and its option labels are not Left or Right
- judge (read by hand until a judge is calibrated): no question fails any of the 11 rubric points in skills/askwright/references/writing-questions.md
- judge: the final-render question names the actions and says what it costs
FAIL if any is missing or contradicted.
Length, detail, tone and confidence are not criteria: judge only whether each requirement is met.
Reference answer (a correct reply says this; its wording may differ):
A set of four questions: a compare of take 3 against take 7 with sides that match the clip (take 3 left, take 7 right, randomized false or absent since the order is fixed) and options named for the takes, a choice on the music, a choice or scale on the grade, and a confirm or choice on the render that names the 10-hour cost; each with why, look_for on media questions, and a guess with confidence.
