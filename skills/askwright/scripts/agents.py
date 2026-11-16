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
PASS_ITEM_KEYS = ("handed_to", "handed_off", "handoff", "taken_over_from", "took_over", "takeover", "quiet")
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
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).isoformat(timespec="seconds") if ts else None


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


def collect(dirs, home=None, now=None, window_hours=WINDOW_HOURS):
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
    rows = {}

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
        # sessions started in a parent folder (one level up, a workspace of many repos) that work here:
        # their recent tool calls name one of the project's folders. Read only to match; nothing is shown.
        needles = {r for r in roots} | {r.replace("/", "\\\\") for r in roots} | {r.replace("/", "\\") for r in roots}
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
                rows[t.stem] = {"session": t.stem, "cwd": Path(facts["cwd"]).as_posix(),
                                "process_alive": registry.get(t.stem, False),
                                "machine": this_host(), "branch": "", "title": facts["title"] or "",
                                "started": iso(facts["started"]), "last_activity": iso(mtime), "minutes_quiet": minutes,
                                "subagents": here, "from_parent_folder": True,
                                "evidence": [f"started in a parent folder; recent tool calls name this project "
                                             f"(transcript written {minutes} min ago)"]}
    else:
        problems.append(f"no Claude Code transcripts folder at {pdir.as_posix()}")

    # 3. grindwright claims
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

    # status and order
    out = []
    for r in rows.values():
        r.setdefault("subagents", [])
        r.setdefault("claims", [])
        minutes = r.get("minutes_quiet")
        r["status"] = status_of(minutes, r["process_alive"])
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
        r["worktree"] = tree["path"] if tree else ""
        if r["status"] == "possibly stale" and not r["claims"] and minutes is not None and minutes > RECENT_MINUTES:
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
    return {"ok": True, "built": iso(now), "machine": this_host(), "rows": out, "worktrees_idle": idle,
            "problems": problems, "dirs": [Path(d).as_posix() for d in dirs],
            "note": "this machine only; sessions on other computers show only through their grindwright claims"}


def c_age(claim, now):
    lease = parse_iso(claim.get("lease_until"))
    return f"{round((now - lease) / 3600, 1)} h ago" if lease else "at an unknown time"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dir", action="append", required=True, help="a project folder (repeatable)")
    ap.add_argument("--home", help="Claude Code config folder (default ~/.claude or CLAUDE_CONFIG_DIR)")
    ap.add_argument("--window-hours", type=float, default=WINDOW_HOURS)
    a = ap.parse_args(argv)
    print(json.dumps(collect(a.dir, a.home, window_hours=a.window_hours), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
