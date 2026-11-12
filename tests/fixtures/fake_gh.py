"""Stands in for `gh api` in tests: comments live in the JSON file named by FAKE_GH_STATE."""
import json, os, re, sys

state_path = os.environ["FAKE_GH_STATE"]
st = json.load(open(state_path, encoding="utf-8")) if os.path.exists(state_path) else {"comments": [], "calls": []}
args = sys.argv[1:]
assert args[0] == "api"
args = args[1:]
method = "GET"
if "--method" in args:
    i = args.index("--method"); method = args[i + 1]; del args[i:i + 2]
body = json.load(sys.stdin) if "--input" in args else None
path = [a for a in args if not a.startswith("-")][0]
st["calls"].append({"method": method, "path": path})
out = None
m = re.match(r"repos/([^/]+/[^/]+)/issues/(\d+)/comments(\?.*)?$", path)
r = re.match(r"repos/([^/]+/[^/]+)/pulls/(\d+)/comments/(\d+)/replies$", path)
g = re.match(r"repos/([^/]+/[^/]+)/(issues|pulls)/comments/(\d+)$", path)
if (m or r) and method == "POST":
    repo, n = (m or r).group(1), int((m or r).group(2))
    cid = 1000 + len(st["comments"])
    c = {"id": cid, "body": body["body"], "repo": repo, "number": n,
         "html_url": f"https://github.com/{repo}/issues/{n}#issuecomment-{cid}", "reply_to": r and int(r.group(3))}
    st["comments"].append(c); out = c
elif m:
    page = int(re.search(r"[?&]page=(\d+)", path).group(1)) if re.search(r"[?&]page=", path) else 1
    out = [c for c in st["comments"] if c["repo"] == m.group(1) and c["number"] == int(m.group(2))][(page - 1) * 100:page * 100]
elif g:
    out = next(c for c in st["comments"] if c["id"] == int(g.group(3)))
else:
    sys.stderr.write("fake gh: unknown " + path); sys.exit(1)
json.dump(st, open(state_path, "w", encoding="utf-8"))
print(json.dumps(out))
