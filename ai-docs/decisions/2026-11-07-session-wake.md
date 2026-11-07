# Session wake-up (0.21.0)

Small rulings made without asking, flagged to the owner:

- **One continuation per All done:** a claim is an exclusively created file in the set's `wake/` folder. A later All done can be claimed again, since it means new answers.
- **`read` counts as picking up:** otherwise every set handled the usual way would stay in `pending`.
- **`pending` covers only sets with `working_dir`, for 30 days:** older sets were handled by hand and must not nag.
- **"Done for now" wakes nobody:** a partial answer is not a signal. A timeout returns the counts.
- **The hook prints `{}` when nothing waits:** that keeps the one-JSON-object rule and adds no context to ordinary sessions. It lists titles and paths only, never answer text.
- **No unattended starts:** that waits on the owner's decision. Channels are not used: they are a research preview limited to an allowlist of plugins.

The start command is a hint for a person or a new session; nothing runs it automatically.
