#!/usr/bin/env python3
"""Who is running in a project: every agent session seen in its folders, with the evidence for each row.

A safety check, so it leans towards showing too much: a session that claimed nothing still shows from its
transcript or its live process, and a claim with no recent activity shows as possibly stale, never hidden.
Rows carry titles, ids, branches, folders and times; never message text.

Sources (each optional; one that cannot be read is named in "problems", never silently empty):
  - Claude Code's live registry  <claude home>/sessions/<pid>.json   (process alive, status, kind)
  - Claude Code transcripts      <claude home>/projects/<cwd>/<id>.jsonl and <id>/subagents/agent-*.meta.json
  - git worktrees of each folder (a session in a worktree belongs to the project)
  - grindwright claims           <folder>/ai-docs/grind/ledger.jsonl items in state running, sessions/*.json
  - other machines               when the grind profile has "work.remote", the repository host's grind-claim/* refs
                                 (grindwright's shared claims) and grind-presence/* refs, where each machine publishes
                                 its own rows (publish(); titles, ids, branches, folders, times; never message text)

Standard library only. Other plugins import collect(); `python agents.py --dir PATH` prints one JSON object.
"""
import argparse
import datetime as dt
import json
import os
import platform
import re
import subprocess
import sys
import time
from pathlib import Path

LIVE_MINUTES = 10        # transcript written this recently: live
RECENT_MINUTES = 120     # after this, activity alone no longer counts as running
WINDOW_HOURS = 24        # transcripts older than this are not read at all
SUBAGENT_MINUTES = 30    # an unfinished subagent quiet longer than this is shown as possibly stale
HEAD_BYTES = 65536
PASS_ITEM_KEYS = ("handed_off", "taken_over", "paused_by", "handed_to", "handoff", "taken_over_from", "quiet")
PASS_SESSION_KEYS = ("quiet", "mode", "handed_to", "handoff")


def claude_home():
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")


def norm(p):
    try:
        p = Path(p).resolve()
    except (OSError, RuntimeError):
        p = Path(p)
    return str(p).replace("\\", "/").rstrip("/").lower()


def inside(path, roots):
    p = norm(path)
    return any(p == r or p.startswith(r + "/") for r in roots)


def encode(path):
    """Claude Code's transcript folder name for a working directory."""
    return re.sub(r"[^A-Za-z0-9]", "-", str(Path(path)))


def iso(ts):
    return dt.datetime.fromtimestamp(ts).astimezone().isoformat(timespec="seconds") if ts else None  # local, like the page's clock


def parse_iso(s):
    try:
        t = dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        return (t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)).timestamp()
    except (TypeError, ValueError):
        return None


def pid_alive(pid):
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes
        k = ctypes.windll.kernel32
        h = k.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return False
        code = ctypes.c_ulong()
        ok = k.GetExitCodeProcess(h, ctypes.byref(code))
        k.CloseHandle(h)
        return bool(ok) and code.value == 259  # STILL_ACTIVE
    try:
        os.kill(pid, 0)
        return True
    except PermissionError:
        return True
    except OSError:
        return False


def this_host():
    return platform.node().lower()


def worktrees(folder):
    """[(path, branch)] of the folder's git worktrees; [] when it is not a repository."""
    try:
        out = subprocess.run(["git", "-C", str(folder), "worktree", "list", "--porcelain"], capture_output=True,
                             text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    rows, path = [], None
    for line in out.splitlines():
        if line.startswith("worktree "):
            path = line[9:].strip()
            rows.append([path, ""])
        elif line.startswith("branch ") and rows:
            rows[-1][1] = line[7:].replace("refs/heads/", "")
        elif line == "detached" and rows:
            rows[-1][1] = "(detached)"
    return [tuple(r) for r in rows]


def git_activity(tree):
    """Last time git wrote in a worktree (HEAD, index, reflog): a commit, checkout or add."""
    g = Path(tree) / ".git"
    try:
        gdir = Path(g.read_text(encoding="utf-8").split("gitdir:", 1)[1].strip()) if g.is_file() else g
    except (OSError, IndexError):
        return None
    times = []
    for f in ("HEAD", "index", "logs/HEAD"):
        try:
            times.append((gdir / f).stat().st_mtime)
        except OSError:
            pass
    return max(times) if times else None


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def transcript_facts(path):
    """cwd, branch, first and last time stamps of a transcript, from its head and tail only."""
    facts = {"start_cwd": None, "cwd": None, "branch": None, "started": None, "last": None, "title": None}
    try:
        with open(path, "rb") as h:
            head = h.read(HEAD_BYTES).decode("utf-8", errors="replace")
            size = Path(path).stat().st_size
            h.seek(max(0, size - HEAD_BYTES))
            tail = h.read().decode("utf-8", errors="replace")
    except OSError:
        return facts
    for chunk, first in ((head, True), (tail, False)):
        for line in chunk.splitlines():
            if not line.startswith("{"):
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if not isinstance(d, dict):
                continue
            if d.get("cwd") and first and not facts["start_cwd"]:
                facts["start_cwd"] = d["cwd"]
            if d.get("cwd") and (first and not facts["cwd"] or not first):
                facts["cwd"] = d["cwd"]
            if d.get("gitBranch"):
                if first and not facts["branch"] or not first:
                    facts["branch"] = d["gitBranch"]
            ts = parse_iso(d.get("timestamp")) if d.get("timestamp") else None
            if ts:
                if first and not facts["started"]:
                    facts["started"] = ts
                facts["last"] = max(facts["last"] or 0, ts)
            if d.get("type") == "custom-title" and d.get("customTitle"):
                facts["title"] = str(d["customTitle"])[:120]
    return facts


def subagents(sdir, now):
    out = []
    for meta in sorted((Path(sdir) / "subagents").glob("agent-*.meta.json")):
        m = read_json(meta) or {}
        if m.get("finished"):
            continue
        log = meta.with_name(meta.name.replace(".meta.json", ".jsonl"))
        try:
            last = log.stat().st_mtime
        except OSError:
            last = meta.stat().st_mtime
        age = (now - last) / 60
        out.append({"id": meta.name[6:-10], "description": str(m.get("description") or "")[:120],
                    "type": m.get("agentType") or "", "last_activity": iso(last), "minutes_quiet": round(age),
                    "status": "live" if age <= LIVE_MINUTES else "recent" if age <= SUBAGENT_MINUTES else "possibly stale"})
    return out


def grind_claims(folder):
    state = Path(folder) / "ai-docs" / "grind"
    ledger = state / "ledger.jsonl"
    if not ledger.exists():
        return [], {}
    claims = []
    try:
        lines = ledger.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None, {}
    for line in lines:
        try:
            item = json.loads(line)
        except ValueError:
            continue
        if not isinstance(item, dict) or item.get("state") != "running":
            continue
        c = {"id": item.get("id"), "title": str(item.get("title") or "")[:120], "session": item.get("session") or "solo",
             "branch": item.get("branch") or "", "lease_until": item.get("lease_until"),
             "held_remote": item.get("held_remote") or None}
        c.update({k: item[k] for k in PASS_ITEM_KEYS if item.get(k)})
        claims.append(c)
    sessions = {}
    for f in list((state / "sessions").glob("*.json")) + [state / "session.json"]:
        s = read_json(f)
        if isinstance(s, dict):
            sid = "solo" if f.name == "session.json" else f.stem
            sessions[sid] = {k: s[k] for k in ("started",) + PASS_SESSION_KEYS if s.get(k)}
    return claims, sessions


def chain_claims(roots, now):
    """Open chainwright claims in ledgers listed in ~/.chainwright/runs.json whose ledger, chain prompt, handoff
    or cwd sits in the project. Returns (claims, problems)."""
    reg = Path(os.environ.get("CHAINWRIGHT_HOME") or (Path.home() / ".chainwright")) / "runs.json"
    if not reg.is_file():
        return [], []
    try:
        runs = (json.loads(reg.read_text(encoding="utf-8")) or {}).get("runs") or {}
    except (OSError, ValueError) as e:
        return [], [f"cannot read the chainwright run list: {e}"]
    out, problems = [], []
    for path in runs:
        try:
            doc = json.loads(Path(path).read_text(encoding="utf-8"))
        except FileNotFoundError:
            continue
        except (OSError, ValueError) as e:
            problems.append(f"cannot read chain ledger {Path(path).as_posix()}: {e}")
            continue
        for c in doc.get("chains") or []:
            claim = c.get("claim")
            if not isinstance(claim, dict):
                continue
            spots = [path] + [c.get(k) for k in ("prompt", "handoff", "cwd") if c.get(k)]
            if not any(inside(x, roots) for x in spots):
                continue
            at = parse_iso(claim.get("at"))
            out.append({"chain": c.get("name") or "", "manager": claim.get("manager") or "", "at": claim.get("at"),
                        "minutes": round((now - at) / 60) if at else None, "ledger": Path(path).as_posix(),
                        "prompt": Path(c["prompt"]).name.lower() if c.get("prompt") else ""})
    return out, problems


def tail_names(path, needles):
    """True when the last part of a transcript mentions one of the folders (lower-case match)."""
    try:
        with open(path, "rb") as h:
            h.seek(max(0, Path(path).stat().st_size - 4 * HEAD_BYTES))
            text = h.read().decode("utf-8", errors="replace").lower()
    except OSError:
        return False
    return any(n in text for n in needles)


def status_of(minutes, alive):
    if alive or (minutes is not None and minutes <= LIVE_MINUTES):
        return "live"
    if minutes is not None and minutes <= RECENT_MINUTES:
        return "recent"
    return "possibly stale"


def collect(dirs, home=None, now=None, window_hours=WINDOW_HOURS, remote=True):
    """{built, rows, worktrees_idle, problems} for the folders of one project."""
    now = now or time.time()
    home = Path(home) if home else claude_home()
    problems, roots, trees, raw = [], set(), {}, set()
    for d in dirs:
        if not Path(d).exists():
            problems.append(f"folder not found: {d}")
            continue
        roots.add(norm(d))
        raw.add(str(Path(d)))
        for path, branch in worktrees(d):
            roots.add(norm(path))
            raw.add(str(Path(path)))
            trees[norm(path)] = {"path": Path(path).as_posix(), "branch": branch}
    rows, tpaths = {}, {}

    # 1. live registry
    reg, registry = home / "sessions", {}
    registry_ok = reg.is_dir()
    if registry_ok:
        for f in reg.glob("*.json"):
            s = read_json(f)
            if not isinstance(s, dict) or not s.get("cwd"):
                continue
            if not inside(s["cwd"], roots):
                if pid_alive(s.get("pid")):
                    registry[s.get("sessionId") or f.stem] = True
                continue
            domain = str(s.get("pidDomain") or "")
            other = bool(domain) and ":" in domain and domain.split(":", 1)[1] != this_host()
            alive = False if other else pid_alive(s.get("pid"))
            registry[s.get("sessionId") or f.stem] = alive
            if not alive and not other:
                continue  # a registry file left by a dead process; its transcript still counts below
            sid = s.get("sessionId") or f.stem
            rows[sid] = {"session": sid, "cwd": Path(s["cwd"]).as_posix(), "kind": s.get("kind") or "",
                         "entrypoint": s.get("entrypoint") or "", "name": s.get("name") or "",
                         "pid": s.get("pid"), "process_alive": alive, "machine": domain.split(":", 1)[-1] or this_host(),
                         "agent_status": s.get("status") or "", "started": iso((s.get("startedAt") or 0) / 1000),
                         "evidence": ["process alive"] if alive else [f"registered on {domain}, cannot check from here"]}
    elif home.exists():
        problems.append("Claude Code's session registry folder is missing; live processes cannot be checked")

    # 2. transcripts
    pdir = home / "projects"
    if pdir.is_dir():
        # Claude Code names the folder after the cwd as typed, so try both the given and the resolved spelling
        prefixes = {encode(r).lower() for r in roots | raw}
        for folder in pdir.iterdir():
            name = folder.name.lower()
            if not folder.is_dir() or not any(name.startswith(p) for p in prefixes):
                continue
            for t in folder.glob("*.jsonl"):
                try:
                    mtime = t.stat().st_mtime
                except OSError:
                    continue
                if now - mtime > window_hours * 3600 and t.stem not in rows:
                    continue
                facts = transcript_facts(t)
                if not facts["cwd"] or not inside(facts["cwd"], roots):
                    continue
                sid = t.stem
                minutes = round((now - mtime) / 60)
                row = rows.setdefault(sid, {"session": sid, "cwd": Path(facts["cwd"]).as_posix(), "process_alive": False,
                                            "machine": this_host(), "evidence": []})
                row.update(branch=facts["branch"] or "", title=facts["title"] or row.get("name") or "",
                           last_activity=iso(mtime), minutes_quiet=minutes)
                row.setdefault("started", iso(facts["started"]))
                if not row.get("started"):
                    row["started"] = iso(facts["started"])
                row["evidence"].append(f"transcript written {minutes} min ago")
                row["subagents"] = subagents(folder / sid, now)
                tpaths[sid] = t
        # sessions started in a parent folder (one level up, a workspace of many repos) that work here:
        # their recent tool calls name one of the project's folders. Read only to match; nothing is shown.
        spellings = roots | {x.replace("\\", "/").rstrip("/").lower() for x in raw}  # as typed and resolved
        needles = spellings | {r.replace("/", "\\\\") for r in spellings} | {r.replace("/", "\\") for r in spellings}
        for folder in pdir.iterdir():
            name = folder.name.lower()
            if not folder.is_dir() or not any(p.startswith(name) and p != name for p in prefixes):
                continue
            for t in folder.glob("*.jsonl"):
                try:
                    mtime = t.stat().st_mtime
                except OSError:
                    continue
                if now - mtime > RECENT_MINUTES * 60 or t.stem in rows:
                    continue
                facts = transcript_facts(t)
                if not facts["cwd"]:
                    continue
                moved_in = inside(facts["cwd"], roots)  # the session's shell moved into the project
                starts = {norm(c) for c in (facts["cwd"], facts["start_cwd"]) if c}
                if not moved_in and not any(r.startswith(c + "/") for r in roots for c in starts):
                    continue
                here = [a for a in subagents(folder / t.stem, now) if tail_names(
                    folder / t.stem / "subagents" / f"agent-{a['id']}.jsonl", needles)]
                if not moved_in and not here and not tail_names(t, needles):
                    continue
                minutes = round((now - mtime) / 60)
                tpaths[t.stem] = t
                rows[t.stem] = {"session": t.stem, "cwd": Path(facts["cwd"]).as_posix(),
                                "process_alive": registry.get(t.stem, False),
                                "machine": this_host(), "branch": "", "title": facts["title"] or "",
                                "started": iso(facts["started"]), "last_activity": iso(mtime), "minutes_quiet": minutes,
                                "subagents": here, "from_parent_folder": True,
                                # show the project folder it works in, not the parent it was started from
                                "worktree": "" if moved_in else Path(sorted(raw)[0]).as_posix(),
                                "evidence": [f"started in {Path(facts['start_cwd'] or facts['cwd']).as_posix()}; recent tool "
                                             f"calls name this project (transcript written {minutes} min ago)"]}
    else:
        problems.append(f"no Claude Code transcripts folder at {pdir.as_posix()}")

    # 3b is below; 3. grindwright claims
    claims_all, grind_sessions = [], {}
    for d in dirs:
        if not Path(d).exists():
            continue
        claims, sess = grind_claims(d)
        if claims is None:
            problems.append(f"cannot read the grind ledger in {d}")
            continue
        claims_all += claims
        grind_sessions.update(sess)
    for c in claims_all:
        c["session_info"] = grind_sessions.get(c["session"], {})
        match = next((r for r in rows.values() if c["branch"] and r.get("branch") == c["branch"]), None)
        lease = parse_iso(c.get("lease_until"))
        c["lease_expired"] = bool(lease and lease < now)
        if match:
            match.setdefault("claims", []).append(c)
            match["evidence"].append(f"grindwright claim {c['id']}")
            continue
        key = f"claim:{c['session']}:{c['id']}"
        rows[key] = {"session": c["session"], "claims": [c], "process_alive": False, "machine": "",
                     "branch": c["branch"], "title": c["title"], "evidence": ["grindwright claim only, no session seen"
                                                                           + (" (lease expired)" if c["lease_expired"] else "")]}

    # 3b. chainwright claims: a manager handed this chain to a session. Joined to the session whose transcript
    # names the chain's prompt file; otherwise its own row, stale once the claim is older than RECENT_MINUTES.
    cclaims, cprob = chain_claims(roots, now)
    problems += cprob
    for c in cclaims:
        match = next((r for sid, r in rows.items() if c["prompt"] and sid in tpaths
                      and tail_names(tpaths[sid], {c["prompt"]})), None)
        if match:
            match.setdefault("chain_claims", []).append(c)
            match["evidence"].append(f"chainwright claim on chain {c['chain']}")
            continue
        old = c["minutes"] is None or c["minutes"] > RECENT_MINUTES
        rows[f"chain:{c['ledger']}:{c['chain']}"] = {
            "session": f"chain {c['chain']}", "chain_claims": [c], "process_alive": False, "machine": this_host(),
            "branch": "", "title": f"chain {c['chain']} (manager {c['manager']})", "started": c["at"],
            "status_hint": "possibly stale" if old else "claimed, no session seen",
            "evidence": [f"chainwright claim only, no session seen; claimed {c['minutes']} min ago in {c['ledger']}"]}

    # status and order
    out = []
    for r in rows.values():
        r.setdefault("subagents", [])
        r.setdefault("claims", [])
        minutes = r.get("minutes_quiet")
        r["status"] = r.pop("status_hint", None) or status_of(minutes, r["process_alive"])
        if r["status"] == "possibly stale" and r.get("chain_claims") and not r.get("last_activity"):
            r["stale_reason"] = f"chain claim {r['chain_claims'][0]['minutes']} min old and no session seen"
        if (r["status"] == "live" and not r["process_alive"] and registry_ok and r.get("machine") == this_host()
                and not registry.get(r["session"])):
            r["status"] = "recent"  # written lately, but no live Claude Code process holds it: ended or idle
            r["evidence"].append("no live Claude Code process registered for it")
        if r["status"] != "live":
            for a in r["subagents"]:
                if a["status"] == "live":
                    a["status"] = "recent"  # a subagent cannot outlive its session's process
        if (r["status"] == "possibly stale" and r["claims"] and not r.get("last_activity")
                and not any(c.get("lease_expired") for c in r["claims"])):
            r["status"] = "claimed, no session seen"
        if r["status"] == "possibly stale" and r["claims"] and not r.get("last_activity"):
            r["stale_reason"] = "claimed, but no transcript or process seen" + (
                f"; lease ran out {c_age(r['claims'][0], now)}" if r["claims"][0].get("lease_expired") else "")
        tree = next((trees[k] for k in trees if r.get("cwd") and inside(r["cwd"], {k})), None)
        r["worktree"] = tree["path"] if tree else r.get("worktree") or ""
        if r["status"] == "possibly stale" and not r["claims"] and not r.get("chain_claims") and minutes is not None and minutes > RECENT_MINUTES:
            continue  # finished sessions in the window are history, not running
        out.append(r)
    out.sort(key=lambda r: ({"live": 0, "recent": 1}.get(r["status"], 2), r.get("minutes_quiet") or 0))
    used = {norm(r["worktree"]) for r in out if r.get("worktree")}
    idle = [t for k, t in trees.items() if k not in used and k not in {norm(d) for d in dirs}]
    for t in idle:
        last = git_activity(t["path"])
        t["last_git_activity"] = iso(last)
        t["minutes_since_git"] = round((now - last) / 60) if last else None
    idle.sort(key=lambda t: t["minutes_since_git"] if t["minutes_since_git"] is not None else 10**9)
    result = {"ok": True, "built": iso(now), "machine": this_host(), "rows": out, "worktrees_idle": idle,
              "problems": problems, "dirs": [Path(d).as_posix() for d in dirs],
              "note": "this machine only; sessions on other computers show only through their grindwright claims"}
    repos = remote_repos(dirs) if remote else []
    for repo in repos:
        try:
            others = remote_rows(repo, now)
        except Exception as e:  # never an empty list for a failed read
            problems.append(f"could not read other machines' sessions from {repo}: {str(e)[:200]}")
            continue
        out.extend(others)
        result["note"] = f"this machine, and other machines through {repo}"
    if repos:
        out.sort(key=lambda r: ({"live": 0, "recent": 1}.get(r["status"], 2), r.get("minutes_quiet") or 0))
    result["totals"] = time_totals(out, now)
    return result


def time_totals(rows, now):
    """How long each session has been running (start to last activity, or to now while live), and the sum per day
    of the start date. Sets row['running_minutes']; sessions without a start time count nowhere."""
    total, by_day = 0, {}
    for r in rows:
        start = parse_iso(r.get("started")) if r.get("started") else None
        if start is None:
            continue
        end = now if r.get("status") == "live" else (parse_iso(r.get("last_activity")) if r.get("last_activity") else None)
        if end is None or end < start:
            continue
        mins = round((end - start) / 60)
        r["running_minutes"] = mins
        total += mins
        day = time.strftime("%Y-%m-%d", time.localtime(start))
        by_day[day] = by_day.get(day, 0) + mins
    return {"running_minutes": total, "by_day": dict(sorted(by_day.items(), reverse=True))}


# ---- other machines: shared through the repository host (grindwright's "work.remote" channel)

CLAIM_PREFIX, PRESENCE_PREFIX = "grind-claim/", "grind-presence/"
PRESENCE_HEAD = "grindwright presence"
REMOTE_CACHE_SECONDS = 60
PUBLISH_KEYS = ("session", "status", "machine", "branch", "title", "name", "kind", "started", "last_activity",
                "minutes_quiet", "worktree", "cwd", "evidence", "from_parent_folder", "process_alive")


def remote_repos(dirs):
    repos = []
    for d in dirs:
        prof = read_json(Path(d) / "ai-docs" / "grind" / "profile.json")
        work = prof.get("work") if isinstance(prof, dict) else None
        block = work.get("remote") if isinstance(work, dict) else None
        repo = isinstance(block, dict) and (block.get("repo") or (work.get("issues") or {}).get("repo"))
        if repo and repo not in repos:
            repos.append(repo)
    return repos


def gh_api(*args, body=None):
    cmd = os.environ.get("ASKWRIGHT_GH")
    argv = (json.loads(cmd) if cmd else ["gh"]) + ["api", *args] + (["--input", "-"] if body is not None else [])
    r = subprocess.run(argv, input=json.dumps(body) if body is not None else None, capture_output=True, text=True,
                       encoding="utf-8", timeout=30)
    if r.returncode:
        raise RuntimeError(((r.stderr or r.stdout or "gh failed").strip().splitlines() or ["gh failed"])[-1])
    return json.loads(r.stdout) if r.stdout.strip() else {}


def last_json(message):
    for line in reversed((message or "").strip().splitlines()):
        if line.startswith("{"):
            try:
                return json.loads(line)
            except ValueError:
                return {}
    return {}


def _missing(e):
    return "404" in str(e) or "Not Found" in str(e)


def remote_refs(repo):
    """{"claims": [...], "presence": [...]} from the host, cached for a minute so page refreshes stay cheap."""
    cache = Path(os.environ.get("ASKWRIGHT_HOME") or Path.home() / ".askwright").expanduser() / "remote-agents" / (re.sub(r"[^A-Za-z0-9]+", "-", repo) + ".json")
    old = read_json(cache)
    if isinstance(old, dict) and time.time() - old.get("at", 0) < REMOTE_CACHE_SECONDS:
        return old
    out = {"at": time.time()}
    for kind, prefix in (("claims", CLAIM_PREFIX), ("presence", PRESENCE_PREFIX)):
        try:
            refs = gh_api(f"repos/{repo}/git/matching-refs/heads/{prefix}")
        except RuntimeError as e:
            if not _missing(e):
                raise
            refs = []
        out[kind] = []
        for ref in refs if isinstance(refs, list) else []:
            commit = gh_api(f"repos/{repo}/git/commits/{ref['object']['sha']}")
            out[kind].append(dict(last_json(commit.get("message")), key=ref["ref"].split(prefix, 1)[-1]))
    try:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(out), encoding="utf-8")
    except OSError:
        pass
    return out


def remote_rows(repo, now, me=None):
    """Rows for sessions on other machines: what each published, plus their shared grindwright claims."""
    me = (me or this_host()).lower()
    data, rows = remote_refs(repo), []
    for p in data.get("presence", []):
        machine = str(p.get("machine") or p.get("key") or "").lower()
        if not machine or machine == me:
            continue
        at = parse_iso(p.get("at"))
        age = round((now - at) / 60) if at else None
        for src in p.get("rows", []):
            r = {k: src[k] for k in PUBLISH_KEYS if k in src}
            r.update(machine=machine, remote=True, subagents=src.get("subagents") or [], claims=src.get("claims") or [])
            if age is None or age > RECENT_MINUTES:
                r["status"] = "possibly stale"
                r["stale_reason"] = f"{machine} last published {age if age is not None else '?'} min ago"
            elif age > 2 * LIVE_MINUTES and r.get("status") == "live":
                r["status"] = "recent"  # the other machine stopped publishing: it may be off or asleep
            r["minutes_quiet"] = (r.get("minutes_quiet") or 0) + (age or 0)
            r["evidence"] = [f"published by {machine} {age if age is not None else '?'} min ago through {repo}"] + [
                f"{machine}: {e}" for e in (src.get("evidence") or [])[:3]]
            rows.append(r)
    for c in data.get("claims", []):
        machine = str(c.get("machine") or "").lower()
        if not machine or machine == me:
            continue
        until = parse_iso(c.get("until"))
        expired = bool(until and until < now)
        claim = {"id": c.get("item") or c.get("key"), "title": c.get("title") or "", "issue": c.get("issue"),
                 "lease_until": c.get("until"), "lease_expired": expired}
        match = next((r for r in rows if r.get("machine") == machine and str(r.get("session")) == str(c.get("session"))), None)
        if match:
            if not any(str(x.get("id")) == str(claim["id"]) for x in match["claims"]):
                match["claims"].append(claim)
            continue
        at = parse_iso(c.get("at"))
        rows.append({"session": c.get("session") or "", "machine": machine, "remote": True, "branch": "",
                     "title": c.get("title") or "", "claims": [claim], "subagents": [], "process_alive": False,
                     "started": c.get("at"), "minutes_quiet": round((now - at) / 60) if at else None,
                     "status": "possibly stale" if expired else "claimed, no session seen",
                     "stale_reason": f"lease ran out {round((now - until) / 3600, 1)} h ago" if expired else "",
                     "evidence": [f"shared grindwright claim by {machine} through {repo}"
                                  + (" (lease expired)" if expired else f", lease until {c.get('until')}")]})
    return rows


def publish(dirs, home=None, now=None, me=None):
    """Write this machine's rows for the project to grind-presence/<machine> on each remote repository.
    Only PUBLISH_KEYS travel, with claim ids and titles and subagent descriptions: never message text."""
    now = now or time.time()
    me = (me or this_host()).lower()
    repos = remote_repos(dirs)
    if not repos:
        return {"ok": True, "published": [], "note": "no grind profile with work.remote"}
    data = collect(dirs, home, now, remote=False)
    rows = []
    for r in data["rows"]:
        row = {k: r[k] for k in PUBLISH_KEYS if k in r}
        row["claims"] = [{k: c.get(k) for k in ("id", "title", "lease_until")} for c in r.get("claims", [])]
        row["subagents"] = [{k: a.get(k) for k in ("description", "type", "status", "minutes_quiet")}
                            for a in r.get("subagents", [])]
        rows.append(row)
    body = {"machine": me, "at": iso(now), "rows": rows}
    slug = re.sub(r"[^a-z0-9-]+", "-", me).strip("-") or "machine"
    nl = chr(10)
    msg = (f"{PRESENCE_HEAD} {slug}{nl}{nl}Which agent sessions run on {slug} now; replaced every few minutes. "
           f"Do not merge.{nl}{nl}{json.dumps(body, sort_keys=True)}{nl}")
    done, problems = [], []
    for repo in repos:
        try:
            try:
                ref = gh_api(f"repos/{repo}/git/ref/heads/{PRESENCE_PREFIX}{slug}")
                commit = gh_api(f"repos/{repo}/git/commits/{ref['object']['sha']}")
                parent, tree, exists = (commit.get("parents") or [{"sha": ref["object"]["sha"]}])[0]["sha"], commit["tree"]["sha"], True
            except RuntimeError as e:
                if not _missing(e):
                    raise
                default = gh_api(f"repos/{repo}")["default_branch"]
                head = gh_api(f"repos/{repo}/commits/{default}")
                parent, tree, exists = head["sha"], head["commit"]["tree"]["sha"], False
            sha = gh_api(f"repos/{repo}/git/commits", "-X", "POST",
                         body={"message": msg, "tree": tree, "parents": [parent]})["sha"]
            if exists:  # its own ref, replaced each time on the same parent: no history grows
                gh_api(f"repos/{repo}/git/refs/heads/{PRESENCE_PREFIX}{slug}", "-X", "PATCH", body={"sha": sha, "force": True})
            else:
                gh_api(f"repos/{repo}/git/refs", "-X", "POST", body={"ref": f"refs/heads/{PRESENCE_PREFIX}{slug}", "sha": sha})
            done.append(repo)
        except Exception as e:
            problems.append(f"{repo}: {str(e)[:200]}")
    return {"ok": not problems, "published": done, "rows": len(rows), "problems": problems, "machine": me}


def c_age(claim, now):
    lease = parse_iso(claim.get("lease_until"))
    return f"{round((now - lease) / 3600, 1)} h ago" if lease else "at an unknown time"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dir", action="append", required=True, help="a project folder (repeatable)")
    ap.add_argument("--home", help="Claude Code config folder (default ~/.claude or CLAUDE_CONFIG_DIR)")
    ap.add_argument("--window-hours", type=float, default=WINDOW_HOURS)
    ap.add_argument("--publish", action="store_true",
                    help="write this machine's rows to the project's grind-presence ref (needs work.remote and gh)")
    ap.add_argument("--local", action="store_true", help="this machine only; do not read other machines")
    a = ap.parse_args(argv)
    if a.publish:
        print(json.dumps(publish(a.dir, a.home), indent=1))
        return 0
    print(json.dumps(collect(a.dir, a.home, window_hours=a.window_hours, remote=not a.local), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
