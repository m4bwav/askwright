"""Size budget for askwright: what every session loads (the skill description) and what an install weighs.

Run from the repository root: python scripts/budget.py   (red fails; yellow is reported)
Bands: install green under 120 KB, yellow to 240 KB; SKILL.md body green under 6 KB, yellow to 10 KB;
description green under 175 tokens, yellow to 250.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INSTALLED = ["skills", ".claude-plugin", "README.md", "LICENSE", "SECURITY.md"]


def band(v, green, yellow):
    return "green" if v < green else ("yellow" if v <= yellow else "red")


def size(p):
    if p.is_file():
        return p.stat().st_size
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file() and "__pycache__" not in f.parts)


def main():
    rows = []
    inst = sum(size(ROOT / p) for p in INSTALLED if (ROOT / p).exists())
    rows.append(("install size", "%d KB" % (inst // 1024), band(inst, 120 * 1024, 240 * 1024)))
    skill = (ROOT / "skills" / "askwright" / "SKILL.md").read_text(encoding="utf-8")
    body = len(skill.split("\n---\n", 1)[-1].encode("utf-8"))
    rows.append(("SKILL.md body (per use)", "%d bytes" % body, band(body, 6 * 1024, 10 * 1024)))
    m = re.search(r'(?m)^description:\s*"?(.*?)"?\s*$', skill)
    tokens = len(m.group(1)) // 4 if m else 0
    rows.append(("description (every session)", "~%d tokens" % tokens, band(tokens, 175, 250)))
    for name, val, b in rows:
        print("%-30s %-14s %s" % (name, val, b))
    reds = [r for r in rows if r[2] == "red"]
    if reds:
        print("RED: %s" % ", ".join(r[0] for r in reds))
    return 1 if reds else 0


if __name__ == "__main__":
    sys.exit(main())
