#!/usr/bin/env python3
"""Checks for the askwright eval cases, run in an eval's run folder: `python evals/check_set.py <mode>`, exit 0 on pass.

  serve       some questions.json under the folder lints with no errors
  quality     that, and a compare question whose sides match the clip (take 3 left, take 7 right, not claimed random)
              and whose option labels are not Left/Right/A/B
  only-asked  no questions.json at all (the agent asked in chat), or one whose only open question is about visibility
"""

import json
import subprocess
import sys
from pathlib import Path

ASK = Path(__file__).resolve().parent.parent / "skills" / "askwright" / "scripts" / "ask.py"
SIDE_WORDS = {"left", "right", "a", "b", "take a", "take b", "left take", "right take"}


def sets(root):
    return [p for p in root.rglob("questions.json") if ".claude" not in p.parts]


def lints(qfile):
    r = subprocess.run([sys.executable, str(ASK), "lint", str(qfile.parent), "--no-probe"], capture_output=True, text=True)
    try:
        return json.loads(r.stdout).get("ok") is True
    except ValueError:
        return False


def load(qfile):
    try:
        return json.loads(qfile.read_text(encoding="utf-8")).get("questions") or []
    except (OSError, ValueError, AttributeError):
        return []


def good_compare(q):
    """The case's clip has take 3 on the left and take 7 on the right in a fixed order: the sides must say so, and
    must not claim the order was drawn at random."""
    opts = {o.get("id"): str(o.get("label", "")) for o in q.get("options") or []}
    labels = [lab.strip().lower() for lab in opts.values()]
    sides = q.get("sides") or {}
    return (q.get("kind") == "compare" and labels and not any(lab in SIDE_WORDS for lab in labels)
            and "3" in opts.get(sides.get("left"), "") and "7" in opts.get(sides.get("right"), "")
            and sides.get("randomized") is not True)


def main(mode):
    found = sets(Path.cwd())
    if mode == "serve":
        return any(lints(f) for f in found)
    if mode == "quality":
        return any(lints(f) and any(good_compare(q) for q in load(f)) for f in found)
    if mode == "only-asked":
        if not found:
            return True
        for f in found:
            live = [q for q in load(f) if q.get("status", "open") == "open"]
            text = json.dumps(live).lower()
            if len(live) != 1 or not any(w in text for w in ("public", "private", "visib")):
                return False
        return True
    raise SystemExit(f"unknown mode {mode}")


if __name__ == "__main__":
    sys.exit(0 if main(sys.argv[1] if len(sys.argv) > 1 else "") else 1)
