# Remote mode (0.22.0)

The owner's answers to `remote-answers-1`: Tailscale for both people; no notification system for now, agents give links in chat; closed sessions report the start command (`pending` and the SessionStart hook, no unattended starts); the second reviewer accepts one app install. Kept for later: the owner's website as a relay.

Small rulings made without asking, flagged to the owner:

- **Same port on both sides:** Tailscale Serve's HTTPS port equals the local port. The page uses absolute paths, so path mapping would break it.
- **Refuse any proxied request on a local server:** a stale `tailscale serve` entry can point at a port a later local-only set reuses. Forwarding headers also stop a proxied request from posing as local through a forged Host.
- **The owner can open every remote set; others only those named with `--for`:** sharing a device reaches all its ports, so the allowlist decides per set.
- **The dashboard and project pages stay local:** they list all the owner's work. The owner finds remote links in chat. Revisit if that is a pain from a phone.
- **Study sets stay local:** a quiz is not a goal here, and this leaves grading out of the remote surface.
- **A hold covers the whole answer, pick included,** and applies to the owner's remote answers too: a stolen phone looks like the owner. Rules are kept narrow to limit false alarms. No model check.
- **Last answer wins,** with `answered_by` showing whose it is; replays only matter on closed questions, which refuse.
- **Install ceiling raised to 360 KB (345 KB now):** the code is 13 KB in `ask.py`, not worth a separate package since it is off by default and has no dependency.

Limit stated plainly: what a remote answer can trigger rests on the session's own permissions plus written rules. No hook enforces it. `ask.py release` is not technically limited to the owner, though an agent never sees held text before a release.
