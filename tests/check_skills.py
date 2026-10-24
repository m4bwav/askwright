"""Structure and public-safety checks for the askwright repository. Standard library only.

Run from the repository root: python tests/check_skills.py
Checks: the plugin manifest; each skill's frontmatter, description length and body length; relative links in every
markdown file; LF line endings; no secrets (token-like strings of 40+ characters outside tests/fixtures), no
home-folder paths, no AI attribution; the evergreen companions; ask.py lint on the fixture set.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT = {".md", ".py", ".json", ".yml", ".yaml", ".txt", ".js", ".css", ".html", ".vtt", ".toml", ".cfg", ".gitignore",
        ".gitattributes"}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "dist", "node_modules"}
SKIP_PREFIXES = ("evals/cases/results/", "tests/vendor/", "kickoff-prompt.md")  # local eval output; vendored axe-core
# (minified); the git-ignored session prompt, which names machine paths and never leaves the disk
DESC_MAX = 700  # this repository's budget; the Agent Skills spec allows 1,024
BODY_MAX = 200
problems = []


def files():
    for p in ROOT.rglob("*"):
        if p.is_file() and not (set(p.relative_to(ROOT).parts) & SKIP_DIRS) and not rel(p).startswith(SKIP_PREFIXES):
            yield p


def rel(p):
    return p.relative_to(ROOT).as_posix()


def check_manifest():
    mp = ROOT / ".claude-plugin" / "plugin.json"
    try:
        m = json.loads(mp.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        problems.append("plugin.json unreadable: %s" % e)
        return
    for k in ("name", "version", "description", "skills", "license", "repository"):
        if not m.get(k):
            problems.append("plugin.json missing %s" % k)
    if not re.fullmatch(r"\d+\.\d+\.\d+", m.get("version", "")):
        problems.append("plugin.json version is not X.Y.Z")


def check_skills():
    for sk in sorted((ROOT / "skills").iterdir()):
        if not sk.is_dir():
            continue
        f = sk / "SKILL.md"
        if not f.exists():
            problems.append("%s has no SKILL.md" % rel(sk))
            continue
        t = f.read_text(encoding="utf-8")
        m = re.match(r"---\n(.*?)\n---\n", t, re.S)
        if not m:
            problems.append("%s: no frontmatter" % rel(f))
            continue
        fm = m.group(1)
        name = re.search(r"(?m)^name:\s*(.+)$", fm)
        desc = re.search(r'(?m)^description:\s*"?(.*?)"?\s*$', fm)
        if not name or name.group(1).strip() != sk.name:
            problems.append("%s: name must be %s" % (rel(f), sk.name))
        if not desc:
            problems.append("%s: no description" % rel(f))
        elif len(desc.group(1)) > DESC_MAX:
            problems.append("%s: description is %d characters (budget %d)" % (rel(f), len(desc.group(1)), DESC_MAX))
        body = t[m.end():].count("\n")
        if body > BODY_MAX:
            problems.append("%s: body is %d lines (budget %d)" % (rel(f), body, BODY_MAX))
        if "## Maintenance" not in t:
            problems.append("%s: no Maintenance section" % rel(f))


LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def check_links():
    for p in files():
        if p.suffix != ".md" or "tests/fixtures" in rel(p):
            continue
        text = p.read_text(encoding="utf-8")
        text = re.sub(r"```.*?```", "", text, flags=re.S)
        for target in LINK.findall(text):
            if re.match(r"[a-z]+:", target) or target.startswith("#"):
                continue
            path = target.split("#")[0]
            if path and not (p.parent / path).resolve().exists():
                problems.append("%s: broken link %s" % (rel(p), target))


TOKEN = re.compile(r"[A-Za-z0-9_\-]{40,}")
HOME = re.compile(r"(?i)(\b[a-z]:[\\/]+[a-z]|[a-z]:[\\/]+users[\\/]+\w+|/users/[a-z0-9_]+/|/home/[a-z0-9_]+/|[a-z]:[\\/]+m4bwa)")
ATTRIB = re.compile(r"(?i)(co-authored-by:\s*claude|generated with \[?claude|🤖 generated)")


def looks_like_token(s, line):
    if not (re.search(r"[0-9]", s) and re.search(r"[A-Za-z]", s)):
        return False
    if re.fullmatch(r"[0-9a-f]{40,64}", s):  # git and sha256 hashes
        return False
    if re.fullmatch(r"[A-Za-z0-9]+([-_][A-Za-z0-9]+){3,}", s) and not re.search(r"[A-Za-z0-9]{24,}", s):
        return False  # kebab or snake names and dated file names, not secrets
    i = line.find(s)
    word_start = max(line.rfind(" ", 0, i), line.rfind("(", 0, i), line.rfind('"', 0, i), line.rfind("<", 0, i))
    if "://" in line[word_start + 1:i] or line[max(0, i - 1):i] in ("/", "=", "."):
        return False  # part of a URL path or query
    return True


def check_text():
    for p in files():
        if p.suffix not in TEXT and p.name not in (".gitignore", ".gitattributes"):
            continue
        r = rel(p)
        data = p.read_bytes()
        if b"\r\n" in data:
            problems.append("%s: CRLF line endings (use LF)" % r)
        text = data.decode("utf-8", "replace")
        in_fixtures = r.startswith("tests/fixtures/")
        for n, line in enumerate(text.splitlines(), 1):
            if not in_fixtures and r != "tests/check_skills.py":
                for tok in TOKEN.findall(line):
                    if looks_like_token(tok, line):
                        problems.append("%s:%d: token-like string (%d chars); keys never go in the repository" % (r, n, len(tok)))
                if HOME.search(line):
                    problems.append("%s:%d: home-folder or owner path; generalise it" % (r, n))
            if ATTRIB.search(line) and r != "tests/check_skills.py":
                problems.append("%s:%d: AI attribution line" % (r, n))


def check_evergreen():
    for f in ("evergreen.json", "RESEARCH.md", "CHANGELOG.md", "LEARNINGS.md", "TESTS.md", "MAINTENANCE.md",
              "evals/evals.json"):
        p = ROOT / f
        if not p.exists():
            problems.append("evergreen companion missing: %s" % f)
        elif p.suffix == ".json":
            try:
                json.loads(p.read_text(encoding="utf-8"))
            except ValueError as e:
                problems.append("%s: %s" % (f, e))


def check_lint():
    ask = ROOT / "skills" / "askwright" / "scripts" / "ask.py"
    good = ROOT / "tests" / "fixtures" / "good"
    r = subprocess.run([sys.executable, str(ask), "lint", str(good), "--no-probe"], capture_output=True, text=True,
                       encoding="utf-8")
    try:
        d = json.loads(r.stdout)
    except ValueError:
        problems.append("ask.py lint printed no JSON: %s" % (r.stderr or r.stdout)[:300])
        return
    for p in d.get("errors", []) + d.get("warnings", []):
        problems.append("fixture set: %s" % p)


if __name__ == "__main__":
    check_manifest()
    check_skills()
    check_links()
    check_text()
    check_evergreen()
    check_lint()
    for p in problems:
        print("FAIL", p)
    print("check_skills: %d problem(s)" % len(problems))
    sys.exit(1 if problems else 0)
