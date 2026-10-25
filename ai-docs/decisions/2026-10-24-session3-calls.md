# Session 3 calls (2026-10-24)

Small rulings made without asking, per the owner's standing rule to decide small calls and flag them.

| # | Call | Why |
|---|---|---|
| S1 | The value cases now run from a fixture folder (`evals/fixtures/media-review/`, copies of the three test media files) instead of `files` under `tests/fixtures/media/`. | `worth --ab` lays `files` at their repo paths, so "in this folder" in the prompt pointed at nothing. A fixture lands in the run folder itself. |
| S2 | The cases are graded by `evals/check_set.py` (`serve`, `quality`, `only-asked`) instead of prose checks. | `--ab` can run a command that exits 0; it cannot run pseudo-code. The checker lints whatever set a run wrote with the repo's own `ask.py lint --no-probe`. |
| S3 | `outcome-question-quality` no longer says "same folder as before"; it restates the decisions. Its judge criteria stay, read by hand until a judge is calibrated. | Every run is a fresh context; "as before" refers to nothing. |
| S4 | `action-ask-only-the-real-decision` is the hold-out case. | The suite has three value cases; the protocol wants one held out from tuning. |
| S5 | D5 is wired in the private image-generation skill's pair tool (`pair --ask`, `picks`), not in cinewright. | cinewright-qc has the agent fill the rubric; it never asks the person on a page, so there is nothing there to switch. The hand-written review pages came from the pair step. |
