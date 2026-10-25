"""Runs every example on the GitHub wiki against a published askwright release and prints the output the pages show.

    python 2026-10-24-wiki-verify.py <unpacked release>/skills/askwright/scripts/ask.py > out.txt

Each case builds its sets in a fresh scratch folder (shown as /work/proj), never in a repository. Times, PIDs,
ports and the scratch path are masked so two runs can be diffed: `wikiwright.py diffout old.txt new.txt`.
ask.py prints each JSON object on one line; transcripts here print it indented, as the pages show it, except the
`raw` case, which prints one line as ask.py does.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ASK = str(Path(sys.argv[1]).resolve())
FIXTURES = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "media"
ROOT = Path(tempfile.mkdtemp(prefix="askw-wiki-")).resolve()
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def mask(s):
    for form in (json.dumps(str(ROOT))[1:-1], str(ROOT)):
        s = s.replace(form, "/work/proj")
    s = re.sub(r"(/work/proj[^\"\s]*)", lambda m: m.group(1).replace("\\\\", "/").replace("\\", "/"), s)
    s = re.sub(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[+-][0-9]{2}:[0-9]{2}", "<time>", s)
    s = re.sub(r'"pid": \d+', '"pid": <pid>', s)
    s = re.sub(r'"port": \d+', '"port": <port>', s)
    s = re.sub(r"127\.0\.0\.1:\d+", "127.0.0.1:<port>", s)
    s = re.sub(r'"waited": [\d.]+', '"waited": <s>', s)
    return s


def section(name):
    print(f"\n## {name}")


def ask(*args, pretty=True, show=None):
    """Runs ask.py like `python ask.py ...` in the scratch folder and prints a transcript with the exit code."""
    r = subprocess.run([sys.executable, ASK, *args], cwd=ROOT, capture_output=True, text=True)
    shown = " ".join(a if re.fullmatch(r"[\w./@=-]+", a) else json.dumps(a) for a in args)
    print(f"$ python ask.py {show or shown}")
    out = r.stdout.strip()
    if out and pretty:
        try:
            out = json.dumps(json.loads(out), indent=2)
        except ValueError:
            pass
    if out:
        print(mask(out))
    if r.stderr.strip():
        print(mask(r.stderr.strip()))
    print("$ echo $?")
    print(r.returncode)
    try:
        return json.loads(r.stdout)
    except ValueError:
        return None


def write(rel, text):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:  # write_text has no newline before Python 3.10
        f.write(text)
    return p


def server(rel):
    return json.loads((ROOT / rel / "server.json").read_text(encoding="utf-8"))


def http(rel, method, path, body=None, headers=None, show=True):
    info = server(rel)
    h = {"X-Ask-Token": info["token"]}
    h.update(headers or {})
    h = {k: v for k, v in h.items() if v is not None}
    data = None
    if body is not None:
        data = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
        h.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(f"http://127.0.0.1:{info['port']}{path}", data=data, method=method, headers=h)
    try:
        with OPENER.open(req, timeout=10) as r:
            code, text, hdrs = r.status, r.read(), r.headers
    except urllib.error.HTTPError as e:
        code, text, hdrs = e.code, e.read(), e.headers
    if show:
        print(f"{method} {path} -> {code}")
        if hdrs.get("Content-Range"):
            print(f"Content-Range: {hdrs['Content-Range']}")
        if hdrs.get("Content-Type", "").startswith("application/json"):
            print(mask(json.dumps(json.loads(text), indent=2)))
    return code, text


# The set the Home and Getting started pages build.
FIRST = """{
  "askwright": 1,
  "id": "first",
  "title": "Try askwright",
  "questions": [
    {
      "id": "render",
      "kind": "confirm",
      "title": "Tonight's render",
      "question": "When should the final render run?",
      "why": "It holds the GPU for six hours, so nothing else renders meanwhile.",
      "options": [
        {"id": "tonight", "label": "Render tonight"},
        {"id": "saturday", "label": "Wait until Saturday", "consequence": "The cut slips two days."}
      ],
      "guess": {"option": "tonight", "why": "Nothing else is queued tonight.", "confidence": "high"}
    },
    {
      "id": "music",
      "kind": "choice",
      "title": "Credits music",
      "question": "Which track should play over the credits?",
      "why": "The credits run 40 seconds and the track sets the last mood.",
      "options": [
        {"id": "piano", "label": "The piano theme"},
        {"id": "drums", "label": "The battle drums"},
        {"id": "silence", "label": "No music, just the wind"}
      ],
      "guess": {"option": "drums", "why": "The film ends on the charge.", "confidence": "low"}
    }
  ]
}
"""

# A compare question with a clip, for the Question-Set-Format and Commands pages.
TAKES = """{
  "askwright": 1,
  "id": "takes",
  "title": "Pick the take",
  "media_roots": ["../../renders"],
  "questions": [
    {
      "id": "arrow",
      "kind": "compare",
      "title": "The arrow",
      "question": "Which take of the arrow shot should go in the cut?",
      "why": "This is the only shot of the arrow; the take you pick gets the HD re-render.",
      "look_for": ["The arrow from 1.0 s: does it stay in place when he falls?"],
      "media": [{"src": "arrow_pair.mp4"}],
      "sides": {"left": "t2", "right": "t5", "randomized": true},
      "options": [
        {"id": "t2", "label": "Take 2"},
        {"id": "t5", "label": "Take 5"},
        {"id": "tie", "label": "Either is fine"},
        {"id": "redo", "label": "Neither: redo the shot", "consequence": "About 40 minutes of renders."}
      ],
      "guess": {"option": "t5", "why": "The shaft is thinner and he finishes the line.", "confidence": "low"}
    }
  ]
}
"""

# One set that breaks most question rules, for the Lint-Rules page.
BAD = """{
  "askwright": 1,
  "id": "bad",
  "title": "Everything wrong",
  "questions": [
    {"id": "_tmp", "kind": "pick", "title": "", "question": "Pick a colour", "options": []},
    {"id": "dup", "kind": "choice", "title": "Colour", "question": "Which colour and should we ship it?",
     "why": "It sets the palette.",
     "options": [{"id": "left", "label": "Left"}, {"id": "unsure", "label": "Blue"}, {"id": "b", "label": "Blue"}],
     "guess": {"option": "red", "why": "", "confidence": "maybe"}},
    {"id": "dup", "kind": "confirm", "title": "Colour", "question": "Surely we keep blue?", "why": "Brand.",
     "options": [{"id": "y", "label": "Yes, keep it"}, {"id": "n", "label": "Switch to green"}]},
    {"id": "clip", "kind": "compare", "title": "The clip", "question": "Which take of the clip is better?",
     "why": "One goes in the cut.", "look_for": ["quality"],
     "media": [{"src": "missing.mp4"}, {"src": "notes.txt"}, {"src": "../outside.png"}, {"src": "still.png"}],
     "sides": {"left": "a", "right": "zzz", "randomized": false},
     "options": [{"id": "a", "label": "Take A"}, {"id": "c", "label": "Take C"}],
     "guess": {"option": "a", "why": "Sharper.", "confidence": "high"},
     "show_if": {"question": "nope", "option": ["x"]},
     "one_pager": [{"type": "slides"}]},
    {"id": "old", "kind": "choice", "title": "Old", "question": "Which old one?", "why": "Gone.",
     "status": "superseded", "options": [{"id": "p", "label": "P one"}, {"id": "q", "label": "Q one"}],
     "guess": {"option": "p", "why": "P.", "confidence": "high"}},
    {"id": "gone", "kind": "choice", "title": "Gone", "question": "Which gone one?", "why": "Gone.",
     "status": "withdrawn", "options": [{"id": "p", "label": "P one"}, {"id": "q", "label": "Q one"}],
     "guess": {"option": "p", "why": "P.", "confidence": "high"}},
    {"id": "same", "kind": "compare", "title": "Same", "question": "Which extras should the cut keep?",
     "why": "Asked twice.", "sides": {"left": "x", "right": "z", "randomized": true},
     "options": [{"id": "x", "label": "The outtakes"}, {"id": "z", "label": "The credits sting"}],
     "guess": {"option": "x", "why": "Fun.", "confidence": "high"}},
    {"id": "later", "kind": "choice", "title": "Later", "question": "Which one later?", "why": "Parked.",
     "status": "paused", "options": [{"id": "p", "label": "P one"}, {"id": "q", "label": "Q one"}],
     "guess": {"option": "p", "why": "P.", "confidence": "high"}},
    {"id": "wordy", "kind": "multi", "title": "A title that goes on and on and on, well past the eighty-character limit for a caption",
     "question": "Which extras should the cut keep?",
     "why": "One. Two. Three. Four.",
     "options": [{"id": "x", "label": "The outtakes"}, {"id": "z", "label": "The credits sting"}],
     "guess": {"options": ["x", "w"], "why": "Fun.", "confidence": "high"}}
  ]
}
"""


def main():
    shutil.copy(FIXTURES / "clip.mp4", write("renders/arrow_pair.mp4", "").as_posix())
    shutil.copy(FIXTURES / "swatch.png", ROOT / "swatch.png")
    print(f"python {sys.version.split()[0]} on {sys.platform}")

    section("version")
    ask("--version", pretty=False)

    section("new")
    ask("new", "ask/first", "--title", "Try askwright")
    print((ROOT / "ask/first/questions.json").read_text(encoding="utf-8"))
    ask("new", "ask/first", "--title", "Again")

    section("lint-empty")
    ask("lint", "ask/first")

    section("raw")
    write("ask/first/questions.json", FIRST)
    ask("lint", "ask/first", pretty=False)

    section("serve")
    ask("serve", "ask/first", "--detach")
    print("server.json keys: " + ", ".join(server("ask/first")))
    ask("serve", "ask/first", "--detach")

    section("page-api")
    code, html = http("ask/first", "GET", "/", headers={"X-Ask-Token": None}, show=False)
    print(f"GET / -> {code}, the page carries its token: {server('ask/first')['token'] in html.decode()}")
    http("ask/first", "GET", "/api/set", headers={"X-Ask-Token": "wrong"})
    http("ask/first", "GET", "/api/set", headers={"Host": "evil.example:80"})
    http("ask/first", "POST", "/api/answer", {"qid": "render", "choice": "tonight"},
         headers={"Origin": "http://evil.example"})
    http("ask/first", "POST", "/api/answer", {"qid": "render", "choice": "maybe"})
    http("ask/first", "POST", "/api/answer", {"qid": "render", "choice": "tonight", "q_rev": 1})
    http("ask/first", "POST", "/api/answer", {"qid": "music", "note": "Ask the composer first", "q_rev": 1})

    section("status")
    ask("status", "ask/first")

    section("read")
    ask("read", "ask/first")
    ask("read", "ask/first", "--since", "1")

    section("inline")
    ask("inline", "ask/first")

    section("wait-done")
    ask("status", "ask/first", "--wait-done", "--timeout", "1", "--interval", "0.2")
    http("ask/first", "POST", "/api/event", {"type": "done"})
    st = ask("status", "ask/first")
    print("done:", st["done"])

    section("add")
    write("round2.json", json.dumps({
        "id": "music2", "kind": "choice", "title": "Credits music, again", "supersedes": "music",
        "question": "Which of the two piano cuts should play over the credits?",
        "why": "The composer sent two lengths; the credits run 40 seconds.",
        "options": [{"id": "short", "label": "The 38-second cut"}, {"id": "long", "label": "The 52-second cut"}],
        "guess": {"option": "short", "why": "It fits without a fade.", "confidence": "high"}}, indent=2))
    ask("add", "ask/first", "round2.json")
    ask("add", "ask/first", "round2.json")
    write("render2.json", json.dumps({
        "id": "render", "kind": "confirm", "title": "Tonight's render",
        "question": "When should the final render run?",
        "why": "It now holds the GPU for nine hours, so nothing else renders meanwhile.",
        "options": [{"id": "tonight", "label": "Render tonight"},
                    {"id": "saturday", "label": "Wait until Saturday", "consequence": "The cut slips two days."}],
        "guess": {"option": "tonight", "why": "Nothing else is queued tonight.", "confidence": "high"}}))
    ask("add", "ask/first", "render2.json", "--replace")
    st = ask("status", "ask/first")
    ask("read", "ask/first", "--all")

    section("close")
    ask("close", "ask/first", "music2", "--withdrawn", "The credits were cut")
    ask("close", "ask/first", "nope")

    section("stop")
    ask("stop", "ask/first")
    ask("stop", "ask/first")
    write("ask/first/server.json", json.dumps({"pid": 1, "port": 9, "token": "x"}))
    ask("stop", "ask/first")

    section("serve-lint-failed")
    write("ask/takes/questions.json", TAKES.replace("../../renders", "../renders"))
    ask("serve", "ask/takes", "--detach", "--no-probe")

    section("compare")
    write("ask/takes/questions.json", TAKES)
    ask("lint", "ask/takes", "--no-probe")
    ask("serve", "ask/takes", "--detach", "--no-probe")
    st = json.loads(http("ask/takes", "GET", "/api/set", show=False)[1])
    url = st["questions"][0]["media"][0]["url"]
    print("media url:", url)
    http("ask/takes", "GET", url, headers={"Range": "bytes=0-1"})
    http("ask/takes", "GET", "/m/0/questions.json")
    http("ask/takes", "GET", "/m/1/..%2F..%2Fswatch.png")
    http("ask/takes", "POST", "/api/attachment", b"not an image", headers={"X-Ask-Qid": "arrow",
                                                                         "Content-Type": "image/png"})
    code, body = http("ask/takes", "POST", "/api/attachment", (ROOT / "swatch.png").read_bytes(),
                      headers={"X-Ask-Qid": "arrow", "Content-Type": "image/png"})
    att = json.loads(body)["path"]
    http("ask/takes", "POST", "/api/attachment", b"\x89PNG\r\n\x1a\n" + b"0" * (10 * 1024 * 1024),
         headers={"X-Ask-Qid": "arrow", "Content-Type": "image/png"})
    http("ask/takes", "POST", "/api/answer", {"qid": "arrow", "choice": "t2", "note": "keep the shaft thin",
                                             "attachments": [att], "timecodes": [{"t": 1.4}],
                                             "guess_revealed": True, "guess_revealed_before_pick": True,
                                             "q_rev": 1}, show=False)
    ask("read", "ask/takes")
    ask("stop", "ask/takes")

    section("lint-rules")
    write("ask/bad/still.png", "")
    shutil.copy(ROOT / "swatch.png", ROOT / "ask/bad/still.png")
    write("ask/bad/notes.txt", "notes")
    write("ask/outside.png", "")
    write("ask/bad/questions.json", BAD)
    r = ask("lint", "ask/bad", "--no-probe", pretty=False, show="lint ask/bad --no-probe  # printed as rule lines below")
    for level in ("errors", "warnings"):
        for e in r[level]:
            print(f"{level[:-1]} {e['rule']} [{e['q']}]: {mask(e['msg'])}")

    section("lint-set-rules")
    write("ask/odd/questions.json", json.dumps({"askwright": 2, "id": "has space", "media_roots": ["nowhere"],
                                                "questions": []}))
    r = ask("lint", "ask/odd", pretty=False, show="lint ask/odd  # printed as rule lines below")
    for e in r["errors"] + r["warnings"]:
        print(f"{e['rule']}: {mask(e['msg'])}")
    many = json.loads(FIRST)
    base = many["questions"][0]
    many["questions"] = [dict(base, id=f"q{i}", title=f"Render {i}", question=f"When should render {i} run?")
                         for i in range(13)]
    write("ask/many/questions.json", json.dumps(many))
    r = ask("lint", "ask/many", pretty=False, show="lint ask/many  # printed as rule lines below")
    for e in r["errors"] + r["warnings"]:
        print(f"{e['rule']}: {mask(e['msg'])}")

    section("load-errors")
    ask("lint", "ask/nothing-here")
    write("ask/broken/questions.json", "{\"askwright\": 1,")
    ask("lint", "ask/broken")
    ask("lint")

    section("inline-refused")
    ask("inline", "ask/many")
    ask("inline", "ask/takes")

    section("recipe-wait-then-read")
    RECIPE = '''
import json, subprocess, sys

ASK = "skills/askwright/scripts/ask.py"


def ask(*args):
    out = subprocess.run([sys.executable, ASK, *args], capture_output=True, text=True).stdout
    return json.loads(out)


status = ask("status", "ask/first", "--wait-done", "--timeout", "5", "--interval", "1")
if status["timed_out"]:
    print("not done yet; unanswered:", status["unanswered"], "stale:", status["stale"])
for a in ask("read", "ask/first")["answers"]:
    print(a["qid"], a["state"], a.get("choice"), a["note"] or "-")
'''
    write("recipe.py", RECIPE.replace("skills/askwright/scripts/ask.py", ASK.replace("\\", "/")))
    r = subprocess.run([sys.executable, "recipe.py"], cwd=ROOT, capture_output=True, text=True)
    print(r.stdout.strip() + r.stderr.strip())

    shutil.rmtree(ROOT, ignore_errors=True)


if __name__ == "__main__":
    main()
