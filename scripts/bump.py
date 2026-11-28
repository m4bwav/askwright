"""Set the version everywhere it lives: python scripts/bump.py 0.51.0

Writes .claude-plugin/plugin.json and VERSION in ask.py, and opens a
'## X.Y.Z' heading under '## Unreleased' in CHANGELOG.md if none exists.
Run with no argument to check the copies agree (exit 1 when they do not).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / ".claude-plugin" / "plugin.json"
ASK = ROOT / "skills" / "askwright" / "scripts" / "ask.py"
CHANGELOG = ROOT / "CHANGELOG.md"
ASK_RE = re.compile(r'^VERSION = "([^"]+)"', re.M)


def read(path):
    return path.read_text(encoding="utf-8")


def write(path, text):
    path.write_bytes(text.encode("utf-8"))


def current():
    return json.loads(read(MANIFEST))["version"], ASK_RE.search(read(ASK)).group(1)


def main(argv):
    if not argv:
        manifest, ask = current()
        if manifest != ask:
            print(f"version mismatch: plugin.json {manifest}, ask.py {ask}")
            return 1
        print(f"versions agree: {manifest}")
        return 0
    new = argv[0]
    if not re.fullmatch(r"\d+\.\d+\.\d+", new):
        print("usage: bump.py X.Y.Z")
        return 2
    text = read(MANIFEST)
    write(MANIFEST, re.sub(r'("version":\s*")[^"]+(")', rf"\g<1>{new}\g<2>", text, count=1))
    write(ASK, ASK_RE.sub(f'VERSION = "{new}"', read(ASK), count=1))
    log = read(CHANGELOG)
    if f"\n## {new}\n" not in log:
        log = log.replace("## Unreleased\n", f"## Unreleased\n\n## {new}\n", 1)
        write(CHANGELOG, log)
    print(f"bumped to {new}: plugin.json, ask.py, CHANGELOG.md heading")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
