"""A fake `gh api` for refs and commits, state in FAKE_REFS_STATE (json). Enough for agents.py publish and read."""
import json
import os
import sys

state_path = os.environ["FAKE_REFS_STATE"]
try:
    st = json.load(open(state_path, encoding="utf-8"))
except (OSError, ValueError):
    st = {"refs": {}, "commits": {"base": {"message": "", "tree": {"sha": "t0"}, "parents": []}}, "n": 0}

args = sys.argv[1:]
assert args[0] == "api"
path = args[1]
method = args[args.index("-X") + 1] if "-X" in args else "GET"
body = json.loads(sys.stdin.read()) if "--input" in args else None
repo, _, rest = path.partition("/git/") if "/git/" in path else (path, "", "")


def save():
    json.dump(st, open(state_path, "w", encoding="utf-8"))


def notfound():
    sys.stderr.write("gh: Not Found (HTTP 404)\n")
    sys.exit(1)


if path.count("/") == 2 and not rest:  # repos/o/r
    print(json.dumps({"default_branch": "main"}))
elif "/commits/" in path and not rest:  # repos/o/r/commits/main
    print(json.dumps({"sha": "base", "commit": {"tree": {"sha": "t0"}}}))
elif rest.startswith("matching-refs/heads/"):
    prefix = rest[len("matching-refs/"):]
    print(json.dumps([{"ref": "refs/" + k, "object": {"sha": v}} for k, v in st["refs"].items() if k.startswith(prefix)]))
elif rest.startswith("ref/heads/"):
    k = rest[len("ref/"):]
    if k not in st["refs"]:
        notfound()
    print(json.dumps({"ref": "refs/" + k, "object": {"sha": st["refs"][k]}}))
elif rest.startswith("commits/") and method == "GET":
    c = st["commits"].get(rest.split("/", 1)[1]) or notfound()
    print(json.dumps(c))
elif rest == "commits" and method == "POST":
    st["n"] += 1
    sha = f"c{st['n']}"
    st["commits"][sha] = {"message": body["message"], "tree": {"sha": body["tree"]}, "parents": [{"sha": p} for p in body["parents"]]}
    save()
    print(json.dumps({"sha": sha}))
elif rest == "refs" and method == "POST":
    st["refs"][body["ref"][len("refs/"):]] = body["sha"]
    save()
    print(json.dumps({"ref": body["ref"]}))
elif rest.startswith("refs/heads/") and method == "PATCH":
    st["refs"][rest[len("refs/"):]] = body["sha"]
    save()
    print(json.dumps({}))
else:
    sys.stderr.write(f"fake gh: unhandled {method} {path}\n")
    sys.exit(2)
