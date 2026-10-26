"""Offline tests for ask.py: lint rules, the server contract, status, read, close and add. Standard library only.

Run from the repository root: python tests/test_ask.py
"""

import copy
import http.client
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "skills" / "askwright" / "scripts"
ASK = SCRIPTS / "ask.py"
FIX = ROOT / "tests" / "fixtures"
sys.path.insert(0, str(SCRIPTS))
import ask  # noqa: E402

_home = None
_env = None


def setUpModule():
    global _home, _env
    _home = tempfile.TemporaryDirectory(prefix="askw-registry-")
    _env = mock.patch.dict(os.environ, {"ASKWRIGHT_HOME": _home.name})
    _env.start()


def tearDownModule():
    _env.stop()
    _home.cleanup()


def good():
    return json.loads((FIX / "good" / "questions.json").read_text(encoding="utf-8"))


class TempSet:
    """A copy of the good fixture set (and its media folder) in a temp dir, optionally mutated."""

    def __init__(self, mutate=None):
        self.tmp = Path(tempfile.mkdtemp(prefix="askw-"))
        shutil.copytree(FIX / "media", self.tmp / "media")
        self.dir = self.tmp / "good"
        self.dir.mkdir()
        data = good()
        if mutate:
            mutate(data)
        self.data = data
        self.write(data)

    def write(self, data):
        (self.dir / "questions.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

    def q(self, qid):
        return next(q for q in self.data["questions"] if q["id"] == qid)

    def cleanup(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


def run_cli(*args, timeout=60):
    r = subprocess.run([sys.executable, str(ASK)] + [str(a) for a in args], capture_output=True, text=True,
                       encoding="utf-8", timeout=timeout)
    try:
        return r.returncode, json.loads(r.stdout)
    except ValueError:
        raise AssertionError("no JSON from %s: %s %s" % (args, r.stdout, r.stderr))


def lint(mutate, probe=False):
    s = TempSet(mutate)
    try:
        d, data = ask.load_set(s.dir)
        errs, warns = ask.lint_set(d, data, probe=probe)
        return {e["rule"] for e in errs}, {w["rule"] for w in warns}
    finally:
        s.cleanup()


def qmod(qid, fn):
    def m(data):
        fn(next(q for q in data["questions"] if q["id"] == qid))
    return m


class EvalCheckTests(unittest.TestCase):
    def test_frame_review_requires_individual_judgments(self):
        fixture = TempSet()
        try:
            base = fixture.data["questions"][0]
            questions = []
            for i in range(6):
                q = copy.deepcopy(base)
                q.update(id="frame-%d" % i, title="Frame %d" % i,
                         question="Which version removes prop %d correctly?" % i,
                         media=[{"src": "../media/swatch.png", "alt": "Two frame versions"}],
                         look_for=["Good: prop %d is removed." % i, "Keep: the same room.",
                                   "Reject: prop %d remains." % i],
                         options=[{"id": "t2", "label": "Use take 2"}, {"id": "t5", "label": "Use take 5"},
                                  {"id": "both", "label": "Both meet the request"},
                                  {"id": "neither", "label": "Neither meets the request"}])
                questions.append(q)
            fixture.data["questions"] = questions
            checker = ROOT / "evals" / "check_set.py"

            def check():
                fixture.write(fixture.data)
                return subprocess.run([sys.executable, str(checker), "frame-review"],
                                      cwd=fixture.dir, capture_output=True).returncode

            self.assertEqual(check(), 0)
            questions[-1]["look_for"] = ["Check identity and quality."]
            self.assertEqual(check(), 1)
            fixture.data["questions"] = questions[:1]
            self.assertEqual(check(), 1)
        finally:
            fixture.cleanup()

    def test_compact_media_checks_generated_data(self):
        fixture = TempSet()
        try:
            q = fixture.data["questions"][0]
            q.update(kind="choice", media=[
                {"src": "../media/swatch.png", "type": "image", "alt": "Case %d" % i,
                 "caption": "Comparison %d" % i} for i in range(6)
            ], one_pager=[{"type": "text", "text": "Details about the workflow."}])
            fixture.data["questions"] = [q]
            checker = ROOT / "evals" / "check_set.py"

            def check():
                fixture.write(fixture.data)
                return subprocess.run([sys.executable, str(checker), "compact-media"],
                                      cwd=fixture.dir, capture_output=True).returncode

            self.assertEqual(check(), 0)
            q["media_layout"] = "stack"
            self.assertEqual(check(), 1)
            q["media_layout"] = "gallery"
            extra = copy.deepcopy(q)
            extra.update(id="second", title="Another workflow", question="Which other workflow should be used?")
            fixture.data["questions"].append(extra)
            self.assertEqual(check(), 1)
        finally:
            fixture.cleanup()


class LintTests(unittest.TestCase):
    def test_good_set_is_clean(self):
        errs, warns = lint(None)
        self.assertEqual(errs, set())
        self.assertEqual(warns, set())

    def test_media_layout_values(self):
        for layout in ("auto", "stack"):
            with self.subTest(layout=layout):
                errs, _ = lint(qmod("arrow", lambda q: q.update(media_layout=layout)))
                self.assertEqual(errs, set())
        self.assertError(qmod("arrow", lambda q: q.update(media_layout="slides")), "media-layout")
        self.assertError(qmod("arrow", lambda q: q.update(media_layout="gallery")), "media-layout")

    def test_image_gallery_and_long_stack(self):
        images = [{"src": "../media/swatch.png", "alt": "Case %d" % i} for i in range(4)]
        for layout in ("auto", "gallery"):
            with self.subTest(layout=layout):
                errs, warns = lint(qmod("arrow", lambda q: q.update(media=images, media_layout=layout)))
                self.assertEqual(errs, set())
                self.assertNotIn("long-media", warns)
        self.assertWarning(qmod("arrow", lambda q: q.update(media=images, media_layout="stack")),
                           "long-media")
        errs, warns = lint(qmod("arrow", lambda q: q.update(
            media=images, media_layout="stack", status="closed")))
        self.assertEqual(errs, set())
        self.assertNotIn("long-media", warns)

    def assertError(self, mutate, rule):
        errs, _ = lint(mutate)
        self.assertIn(rule, errs)

    def assertWarning(self, mutate, rule):
        errs, warns = lint(mutate)
        self.assertEqual(errs, set(), "unexpected errors")
        self.assertIn(rule, warns)

    def test_question_mark(self):
        self.assertError(qmod("music", lambda q: q.update(question="Music under the intro")), "question-mark")

    def test_why_required(self):
        self.assertError(qmod("music", lambda q: q.pop("why")), "why")
        self.assertError(qmod("music", lambda q: q.update(why="  ")), "why")

    def test_look_for_required_on_compare_and_media(self):
        self.assertError(qmod("arrow", lambda q: q.pop("look_for")), "look-for")
        self.assertError(qmod("music", lambda q: q.pop("look_for")), "look-for")

    def test_guess_rules(self):
        self.assertError(qmod("music", lambda q: q.pop("guess")), "guess")
        self.assertError(qmod("music", lambda q: q["guess"].pop("confidence")), "guess-confidence")
        self.assertError(qmod("music", lambda q: q["guess"].update(confidence="medium")), "guess-confidence")
        self.assertError(qmod("music", lambda q: q["guess"].update(option="nope")), "guess-option")
        self.assertError(qmod("cuts", lambda q: q["guess"].update(options=["s3", "zz"])), "guess-option")
        self.assertError(qmod("order", lambda q: q["guess"].update(order=["news"])), "guess-option")
        self.assertError(qmod("title-card", lambda q: q["guess"].update(text="")), "guess-option")
        self.assertError(qmod("music", lambda q: q["guess"].update(why="")), "guess-why")

    def test_options(self):
        self.assertError(qmod("music", lambda q: q.update(options=q["options"][:1])), "options")
        self.assertError(qmod("music", lambda q: q["options"][1].update(id="tone")), "option-id")
        self.assertError(qmod("music", lambda q: q["options"][1].update(label="Keep this tone")), "option-label")
        self.assertError(qmod("music", lambda q: q["options"][1].update(id="unsure")), "option-id")

    def test_position_and_yes_no_labels(self):
        for bad in ("Left", "right", "A", "Option 2", "yes", "No.", "3"):
            self.assertError(qmod("music", lambda q, b=bad: q["options"][0].update(label=b)), "position-label")
        self.assertError(qmod("render", lambda q: q["options"][0].update(label="Yes, render tonight")), "confirm-yes-no")

    def test_states(self):
        self.assertError(qmod("old-intro", lambda q: q.pop("superseded_by")), "superseded-by")
        self.assertError(qmod("old-intro", lambda q: q.update(superseded_by="ghost")), "superseded-by")
        self.assertError(qmod("old-intro", lambda q: q.update(status="withdrawn")), "withdrawn-reason")
        self.assertError(qmod("music", lambda q: q.update(status="pending")), "status")
        self.assertError(qmod("pace", lambda q: q.update(title="Music under the intro")), "duplicate-title")

    def test_duplicate_question_text_and_ids(self):
        self.assertError(qmod("pace", lambda q: q.update(question="Which music should play under the intro?")),
                         "duplicate-question")
        self.assertError(qmod("pace", lambda q: q.update(id="music")), "duplicate-id")
        self.assertError(qmod("pace", lambda q: q.update(id="bad id!")), "id")

    def test_superseded_text_may_repeat(self):
        errs, _ = lint(None)  # old-intro shares its text with music
        self.assertNotIn("duplicate-question", errs)

    def test_media(self):
        self.assertError(qmod("music", lambda q: q["media"][0].update(src="missing.wav")), "media-missing")
        outside = Path(tempfile.gettempdir()) / "askw-outside.png"
        shutil.copy(FIX / "media" / "swatch.png", outside)
        try:
            self.assertError(qmod("pace", lambda q: q["media"][0].update(src=str(outside))), "media-outside")
            self.assertError(qmod("pace", lambda q: q["media"][0].update(src="../../askw-outside.png")), "media-outside")
        finally:
            outside.unlink()

    def test_show_if(self):
        self.assertError(qmod("redo-how", lambda q: q.update(show_if={"question": "ghost", "option": ["x"]})), "show-if")
        self.assertError(qmod("redo-how", lambda q: q.update(show_if={"question": "arrow", "option": ["zz"]})), "show-if")

    def test_sides(self):
        self.assertWarning(qmod("arrow", lambda q: q["sides"].update(randomized=False)), "sides-not-randomized")
        self.assertError(qmod("arrow", lambda q: q["sides"].update(left="zz")), "sides")

    def test_wording_warnings(self):
        self.assertWarning(qmod("music", lambda q: q.update(question="Should we cut the intro and change the music?")),
                           "double-ask")
        self.assertWarning(qmod("music", lambda q: q.update(question="Surely the tone is too sharp, is it not?")),
                           "leading")
        errs, warns = lint(None)
        self.assertNotIn("double-ask", warns)  # "Which take of the arrow shot ..." has no second ask

    def test_long_why_and_vague_look_for(self):
        self.assertWarning(qmod("music", lambda q: q.update(why="One. Two. Three. Four.")), "long-text")
        self.assertWarning(qmod("music", lambda q: q.update(look_for=["overall quality"])), "vague-look-for")

    def test_guess_always_first(self):
        def m(data):
            for q in data["questions"]:
                g = q.get("guess", {})
                if "option" in g:
                    g["option"] = q["options"][0]["id"]
                if "options" in g:
                    g["options"] = [q["options"][0]["id"]]
                if "order" in g:
                    g["order"] = [o["id"] for o in q["options"]]
        self.assertWarning(m, "guess-always-first")

    def test_too_many_open(self):
        def m(data):
            base = next(q for q in data["questions"] if q["id"] == "title-card")
            for i in range(8):
                q = copy.deepcopy(base)
                q.update(id="extra%d" % i, title="Extra %d" % i, question="What goes in slot %d?" % i)
                data["questions"].append(q)
        self.assertWarning(m, "too-many")

    def test_codec_warning(self):
        old = ask.probe_codecs
        ask.probe_codecs = lambda p: {"video": "hevc", "audio": "aac"}
        try:
            self.assertIn("codec", lint(None, probe=True)[1])
        finally:
            ask.probe_codecs = old

    def test_top_level(self):
        self.assertError(lambda d: d.update(askwright=2), "version")
        self.assertError(lambda d: d.update(questions=[]), "no-questions")
        self.assertError(lambda d: d.update(id=""), "set-id")
        self.assertError(lambda d: d.update(product=[]), "session-metadata")
        self.assertError(lambda d: d.update(session=123), "session-metadata")


class ServerCase(unittest.TestCase):
    def setUp(self):
        self.s = TempSet()
        self.srv = ask.make_server(self.s.dir, port=0)
        self.port = self.srv.server_address[1]
        self.t = threading.Thread(target=self.srv.serve_forever, daemon=True)
        self.t.start()

    def tearDown(self):
        self.srv.shutdown()
        self.srv.server_close()
        self.s.cleanup()

    def req(self, method, path, body=None, headers=None, host=None):
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        h = {"Host": host or "127.0.0.1:%d" % self.port}
        h.update(headers or {})
        c.request(method, path, body=body, headers=h)
        r = c.getresponse()
        data = r.read()
        c.close()
        return r.status, dict((k.lower(), v) for k, v in r.getheaders()), data

    def api(self, path, payload=None, token=True, origin=True, ctype="application/json", raw=None, extra=None):
        h = {}
        if token:
            h["X-Ask-Token"] = self.srv.token
        if origin:
            h["Origin"] = "http://127.0.0.1:%d" % self.port
        h.update(extra or {})
        if raw is not None or payload is not None:
            h["Content-Type"] = ctype
        body = raw if raw is not None else (json.dumps(payload).encode() if payload is not None else None)
        st, hd, data = self.req("POST" if body is not None else "GET", path, body, h)
        try:
            return st, json.loads(data)
        except ValueError:
            return st, data


class ServerTests(ServerCase):
    def test_dashboard_from_question_page(self):
        st, headers, html = self.req("GET", "/sessions")
        self.assertEqual(st, 200)
        self.assertIn(b"Questions for you", html)
        self.assertIn(self.srv.token.encode(), html)
        self.assertIn("script-src 'self'", headers["content-security-policy"])
        self.assertEqual(self.req("GET", "/dashboard.js")[0], 200)
        self.assertEqual(self.req("GET", "/dashboard.css")[0], 200)
        self.assertEqual(self.api("/api/sessions", token=False)[0], 403)
        self.assertEqual(self.api("/api/sessions", extra={"Origin": "http://evil.example"})[0], 403)
        self.assertEqual(self.api("/api/open", {"id": "../questions"})[0], 400)
        self.assertEqual(self.api("/api/open", {"id": "0" * 64}, token=False)[0], 403)
        self.assertEqual(self.api("/api/open", {"id": "0" * 64}, extra={"Origin": "http://evil.example"})[0], 403)
        sid = ask.register_set(self.s.dir)
        self.assertEqual(self.api("/api/session-state", {"id": sid, "action": "archive"})[0], 200)
        self.assertEqual(ask.session_state(sid)["state"], "archived")
        self.assertEqual(self.api("/api/session-state", {"id": sid, "action": "restore"})[0], 200)

    def test_binds_loopback_only(self):
        self.assertEqual(self.srv.server_address[0], "127.0.0.1")

    def test_busy_port_refused(self):
        with self.assertRaises(OSError):
            ask.make_server(self.s.dir, port=self.port)

    def test_page_has_token_and_csp(self):
        st, h, data = self.req("GET", "/")
        self.assertEqual(st, 200)
        self.assertIn(self.srv.token.encode(), data)
        self.assertIn("script-src 'self'", h["content-security-policy"])
        for f in ("/app.js", "/app.css"):
            self.assertEqual(self.req("GET", f)[0], 200)

    def test_foreign_host_refused(self):
        self.assertEqual(self.req("GET", "/", host="evil.example:%d" % self.port)[0], 403)

    def media_url(self, qid):
        st, d = self.api("/api/set")
        q = next(q for q in d["questions"] if q["id"] == qid)
        return q["media"][0]["url"]

    def test_range(self):
        url = self.media_url("arrow")
        size = (FIX / "media" / "clip.mp4").stat().st_size
        st, h, data = self.req("GET", url, headers={"Range": "bytes=0-1"})
        self.assertEqual(st, 206)
        self.assertEqual(h["content-range"], "bytes 0-1/%d" % size)
        self.assertEqual(len(data), 2)
        self.assertEqual(h["content-type"], "video/mp4")
        st, h, data = self.req("GET", url, headers={"Range": "bytes=-10"})
        self.assertEqual((st, len(data)), (206, 10))
        st, h, data = self.req("GET", url, headers={"Range": "bytes=%d-" % (size + 5)})
        self.assertEqual(st, 416)
        self.assertEqual(h["content-range"], "bytes */%d" % size)
        st, h, data = self.req("GET", url)
        self.assertEqual((st, len(data), h["accept-ranges"]), (200, size, "bytes"))
        st, h, data = self.req("HEAD", url)
        self.assertEqual((st, h["content-length"], data), (200, str(size), b""))

    def test_captions_found(self):
        st, d = self.api("/api/set")
        q = next(q for q in d["questions"] if q["id"] == "arrow")
        self.assertTrue(q["media"][0].get("captions_url", "").endswith("clip.vtt"))

    def test_traversal_refused(self):
        (self.s.tmp / "secret.mp4").write_bytes(b"x")
        for p in ("/m/0/../secret.mp4", "/m/0/%2e%2e/secret.mp4", "/m/1/../secret.mp4", "/m/0/questions.json",
                  "/m/0/server.json", "/m/9/clip.mp4", "/m/x/clip.mp4"):
            self.assertIn(self.req("GET", p)[0], (403, 404), p)

    def test_symlink_escape_refused(self):
        (self.s.tmp / "secret.mp4").write_bytes(b"x")
        try:
            os.symlink(self.s.tmp / "secret.mp4", self.s.dir / "link.mp4")
        except (OSError, NotImplementedError):
            self.skipTest("cannot create symlinks here")
        self.assertIn(self.req("GET", "/m/0/link.mp4")[0], (403, 404))

    def test_api_needs_token_and_origin(self):
        self.assertEqual(self.api("/api/set", token=False)[0], 403)
        payload = {"qid": "music", "choice": "tone"}
        self.assertEqual(self.api("/api/answer", payload, token=False)[0], 403)
        st, _ = self.api("/api/answer", payload, origin=False, extra={"Origin": "http://evil.example"})
        self.assertEqual(st, 403)
        self.assertFalse((self.s.dir / "answers.json").exists())

    def test_answer_roundtrip_atomic_and_events(self):
        st, d = self.api("/api/answer", {"qid": "music", "choice": "tone", "note": "a bit loud", "q_rev": 1})
        self.assertEqual(st, 200, d)
        self.assertEqual(d["answer"]["state"], "answered")
        a = json.loads((self.s.dir / "answers.json").read_text(encoding="utf-8"))
        self.assertEqual(a["answers"]["music"]["choice"], "tone")
        self.assertEqual(list(self.s.dir.glob("*.tmp")), [])
        ev = [json.loads(l) for l in (self.s.dir / "events.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(ev[-1]["type"], "answer")
        st, d = self.api("/api/set")
        self.assertEqual(d["answers"]["music"]["note"], "a bit loud")

    def test_answer_validation(self):
        for bad in ({"qid": "ghost", "choice": "x"}, {"qid": "music", "choice": "nope"},
                    {"qid": "cuts", "choices": ["s3", "zz"]}, {"qid": "order", "order": ["news"]},
                    {"qid": "music", "attachments": ["../questions.json"]}):
            self.assertEqual(self.api("/api/answer", bad)[0], 400, bad)

    def test_note_only_state(self):
        st, d = self.api("/api/answer", {"qid": "music", "note": "the tone clips at the end"})
        self.assertEqual(d["answer"]["state"], "note_only")

    def test_guess_reveal_is_sticky(self):
        self.api("/api/answer", {"qid": "music", "guess_revealed": True, "guess_revealed_before_pick": True})
        st, d = self.api("/api/answer", {"qid": "music", "choice": "silence", "guess_revealed": True,
                                         "guess_revealed_before_pick": False})
        self.assertTrue(d["answer"]["guess_revealed_before_pick"])

    def test_attachment(self):
        png = (FIX / "media" / "swatch.png").read_bytes()
        st, d = self.api("/api/attachment", raw=png, ctype="image/png", extra={"X-Ask-Qid": "music"})
        self.assertEqual(st, 200, d)
        self.assertEqual(d["path"], "attachments/music-1.png")
        self.assertEqual((self.s.dir / d["path"]).read_bytes(), png)
        st, h, data = self.req("GET", d["url"])
        self.assertEqual((st, data), (200, png))
        st, d2 = self.api("/api/attachment", raw=png, ctype="image/png", extra={"X-Ask-Qid": "music"})
        self.assertEqual(d2["path"], "attachments/music-2.png")
        st, _ = self.api("/api/attachment", raw=b"<svg onload=alert(1)>", ctype="image/png",
                         extra={"X-Ask-Qid": "music"})
        self.assertEqual(st, 400)
        st, _ = self.api("/api/attachment", raw=png, ctype="image/png", extra={"X-Ask-Qid": "../x"})
        self.assertEqual(st, 400)

    def test_attachment_size_cap(self):
        big = b"\x89PNG\r\n\x1a\n" + b"0" * (ask.MAX_UPLOAD + 1)
        st, _ = self.api("/api/attachment", raw=big, ctype="image/png", extra={"X-Ask-Qid": "music"})
        self.assertEqual(st, 413)

    def test_events_and_done(self):
        self.assertEqual(self.api("/api/event", {"type": "done"})[0], 200)
        self.assertEqual(self.api("/api/event", {"type": "hack"})[0], 400)
        self.assertTrue(ask.summarize(self.s.dir)["done"])

    def test_questions_reload(self):
        q = self.s.q("pace")
        q["status"] = "withdrawn"
        q["reason"] = "not needed"
        self.s.write(self.s.data)
        st, d = self.api("/api/set")
        self.assertEqual(next(x for x in d["questions"] if x["id"] == "pace")["status"], "withdrawn")

    def test_self_check(self):
        c = ask.self_check(self.srv)
        self.assertTrue(c["ok"], c)
        self.assertEqual(c["media"], 206)


class DashboardTests(ServerCase):
    def setUp(self):
        super().setUp()
        self.srv.shutdown()
        self.srv.server_close()
        self.home = tempfile.TemporaryDirectory(prefix="askw-dashboard-")
        self.env = mock.patch.dict(os.environ, {"ASKWRIGHT_HOME": self.home.name})
        self.env.start()
        self.srv = ask.make_dashboard_server()
        self.port = self.srv.server_address[1]
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def tearDown(self):
        super().tearDown()
        self.env.stop()
        self.home.cleanup()

    def test_standalone_routes_and_checks(self):
        self.assertEqual(self.srv.server_address[0], "127.0.0.1")
        self.assertTrue(ask.self_check(self.srv)["ok"])
        self.assertEqual(self.req("GET", "/", host="evil.example")[0], 403)
        self.assertEqual(self.api("/api/sessions", token=False)[0], 403)
        self.assertEqual(self.api("/api/set")[0], 404)
        self.assertEqual(self.req("GET", "/m/0/server.json")[0], 404)
        self.assertEqual(self.api("/api/answer", {"qid": "music", "choice": "tone"})[0], 404)
        self.assertEqual(self.api("/api/open", {"id": "../server"})[0], 400)
        self.assertEqual(self.api("/api/open", {"id": []})[0], 400)
        self.assertEqual(self.api("/api/open", {"id": "f" * 64})[0], 400)

    def test_preview_is_next_five_visible_pending_questions_in_set_order(self):
        ask.register_set(self.s.dir)
        ask.write_json_atomic(self.s.dir / "answers.json", {"rev": 1, "answers": {
            "arrow": {"choice": "t5", "q_rev": 1},  # stale, so still shown in preview
            "music": {"choice": "tone", "q_rev": 1},
            "cuts": {"choice": "unsure"},
            "pace": {"note": "Still considering"}}})
        row = self.api("/api/sessions")[1]["sessions"][0]
        summary = ask.summarize(self.s.dir)
        pending = set().union(*(summary[k] for k in ("unanswered", "unsure", "note_only", "stale")))
        expected = [q for q in self.s.data["questions"] if q["id"] in pending][:5]
        self.assertEqual(row["next_questions"], [{"id": q["id"], "question": q["question"]} for q in expected])
        self.assertEqual(len(row["next_questions"]), 5)
        self.assertNotIn("music", [q["id"] for q in row["next_questions"]])
        self.assertNotIn("redo-how", [q["id"] for q in row["next_questions"]])
        self.assertEqual(row["next_questions"][0]["id"], "arrow")

    def test_snooze_durations_expire_at_exact_deadline_and_preserve_data(self):
        sid = ask.register_set(self.s.dir)
        ask.write_json_atomic(self.s.dir / "answers.json", {"rev": 1, "answers": {
            "music": {"choice": "tone", "q_rev": 1}}})
        before = {name: (self.s.dir / name).read_bytes() for name in ("questions.json", "answers.json")}
        for seconds in ask.SNOOZE_SECONDS:
            with self.subTest(seconds=seconds):
                with mock.patch.object(ask.time, "time", return_value=1000000):
                    code, state = self.api("/api/session-state", {"id": sid, "action": "snooze", "seconds": seconds})
                    self.assertEqual(code, 200, state)
                    self.assertEqual(state["snoozed_until"], 1000000 + seconds)
                    row = self.api("/api/sessions")[1]["sessions"][0]
                    self.assertEqual(row["state"], "snoozed")
                    self.assertEqual(ask.register_set(self.s.dir), sid)
                    self.assertEqual(ask.session_state(sid)["state"], "snoozed")
                with mock.patch.object(ask.time, "time", return_value=1000000 + seconds - .001):
                    self.assertEqual(ask.session_state(sid)["state"], "snoozed")
                with mock.patch.object(ask.time, "time", return_value=1000000 + seconds):
                    self.assertEqual(ask.session_state(sid), {"state": "inbox", "snoozed_until": None})
        self.assertEqual(before, {name: (self.s.dir / name).read_bytes() for name in before})

    def test_archive_restore_and_state_survives_registration_and_server_restart(self):
        sid = ask.register_set(self.s.dir)
        code, result = self.api("/api/session-state", {"id": sid, "action": "archive"})
        self.assertEqual((code, result["state"]), (200, "archived"))
        ask.register_set(self.s.dir)
        self.srv.shutdown()
        self.srv.server_close()
        self.srv = ask.make_dashboard_server()
        self.port = self.srv.server_address[1]
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        row = self.api("/api/sessions")[1]["sessions"][0]
        self.assertEqual(row["state"], "archived")
        (self.s.dir / "questions.json").unlink()
        row = self.api("/api/sessions")[1]["sessions"][0]
        self.assertEqual(row["state"], "archived")
        self.assertIn("error", row)
        code, result = self.api("/api/session-state", {"id": sid, "action": "restore"})
        self.assertEqual((code, result["state"], result["snoozed_until"]), (200, "inbox", None))

    def test_session_state_validation_auth_and_write_errors(self):
        sid = ask.register_set(self.s.dir)
        payload = {"id": sid, "action": "snooze", "seconds": 3600}
        self.assertEqual(self.api("/api/session-state", payload, token=False)[0], 403)
        self.assertEqual(self.api("/api/session-state", payload, extra={"Origin": "http://evil.example"})[0], 403)
        for invalid in (dict(payload, id="../bad"), dict(payload, id="f" * 64),
                        dict(payload, action="delete"), dict(payload, seconds=True),
                        dict(payload, seconds=3600.0), dict(payload, seconds=0),
                        dict(payload, seconds=-1), dict(payload, seconds="3600"),
                        dict(payload, seconds=604801)):
            self.assertEqual(self.api("/api/session-state", invalid)[0], 400, invalid)
        self.assertFalse((ask.state_dir() / "session-state").exists())
        with mock.patch.object(ask, "write_json_atomic", side_effect=PermissionError("read-only state")):
            code, result = self.api("/api/session-state", payload)
            self.assertEqual(code, 500)
            self.assertIn("cannot save session state", result["error"])
        folder = ask.state_dir() / "session-state"
        (folder / (sid + ".json")).write_text("{", encoding="utf-8")
        self.assertIn("cannot read session state", self.api("/api/sessions")[1]["sessions"][0]["error"])
        self.assertEqual(self.api("/api/session-state", {"id": sid, "action": "restore"})[0], 200)

    def test_registration_deduplicates_and_keeps_products(self):
        self.s.data.update(product="Copilot", session="session-a", asked_by="Review agent")
        self.s.write(self.s.data)
        sid = ask.register_set(self.s.dir)
        self.assertEqual(sid, ask.register_set(self.s.dir / "questions.json"))
        other = TempSet()
        try:
            other.data.update(product="Codex", session="session-b")
            other.write(other.data)
            processes = [subprocess.Popen([sys.executable, str(ASK), "register", str(d)],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                         for d in (self.s.dir, other.dir)]
            for process in processes:
                stdout, stderr = process.communicate(timeout=30)
                self.assertEqual(process.returncode, 0, stderr)
                self.assertTrue(json.loads(stdout)["ok"])
            st, data = self.api("/api/sessions")
            self.assertEqual(st, 200)
            self.assertEqual({row["product"] for row in data["sessions"]}, {"Copilot", "Codex"})
            self.assertEqual(len(data["sessions"]), 2)
            self.assertNotIn("token", json.dumps(data))
        finally:
            other.cleanup()

    def test_live_counts_notes_unsure_stale_closed_and_missing(self):
        sid = ask.register_set(self.s.dir)
        initial = self.api("/api/sessions")[1]["sessions"][0]
        self.assertGreater(initial["pending"], 0)
        ask.write_json_atomic(self.s.dir / "answers.json", {"rev": 1, "answers": {
            "arrow": {"choice": "t5", "q_rev": 1},
            "music": {"note": "Needs work"},
            "cuts": {"choice": "unsure"}}})
        row = self.api("/api/sessions")[1]["sessions"][0]
        self.assertEqual((row["note_only"], row["unsure"], row["stale"]), (1, 1, 1))
        self.assertEqual(row["pending"], initial["pending"])  # stale answers still need attention
        for q in self.s.data["questions"]:
            q["status"] = "closed"
        self.s.write(self.s.data)
        self.assertEqual(self.api("/api/sessions")[1]["sessions"][0]["pending"], 0)
        (self.s.dir / "questions.json").unlink()
        row = self.api("/api/sessions")[1]["sessions"][0]
        self.assertEqual(row["id"], sid)
        self.assertIn("no questions.json", row["error"])

    def test_bad_registry_is_visible(self):
        folder = ask.state_dir() / "sessions"
        folder.mkdir()
        (folder / ("a" * 64 + ".json")).write_text("{", encoding="utf-8")
        self.assertIn("error", self.api("/api/sessions")[1]["sessions"][0])

    def test_open_restarts_stopped_set_and_reuses_live_server(self):
        sid = ask.register_set(self.s.dir)
        answers = {"askwright": 1, "rev": 1, "answers": {"music": {"choice": "tone", "q_rev": 1}}}
        ask.write_json_atomic(self.s.dir / "answers.json", answers)
        try:
            status, opened = self.api("/api/open", {"id": sid})
            self.assertEqual(status, 200, opened)
            first = ask.server_info(self.s.dir)
            self.assertTrue(first["alive"])
            self.assertEqual(opened["url"], first["url"])
            self.assertEqual(self.api("/api/open", {"id": sid})[1]["url"], opened["url"])
            self.assertEqual(ask.server_info(self.s.dir)["pid"], first["pid"])
            self.assertEqual(run_cli("stop", self.s.dir)[0], 0)
            status, opened = self.api("/api/open", {"id": sid})
            self.assertEqual(status, 200, opened)
            self.assertNotEqual(ask.server_info(self.s.dir)["pid"], first["pid"])
            self.assertEqual(ask.load_answers(self.s.dir), answers)
        finally:
            run_cli("stop", self.s.dir)

    def test_open_lint_failure_is_explicit(self):
        sid = ask.register_set(self.s.dir)
        self.s.q("music").pop("why")
        self.s.write(self.s.data)
        status, result = self.api("/api/open", {"id": sid})
        self.assertEqual(status, 400)
        self.assertIn("lint", result["error"])
        self.assertFalse((self.s.dir / "server.json").exists())

    def test_dashboard_detach_reuse_stop_and_bookmark(self):
        try:
            code, started = run_cli("dashboard", "--detach")
            self.assertEqual(code, 0, started)
            info = ask.server_info(ask.state_dir() / "dashboard")
            self.assertTrue(info["alive"])
            self.assertTrue(ask.ping(info)["dashboard"])
            code, again = run_cli("dashboard", "--detach")
            self.assertEqual((code, again["pid"]), (0, started["pid"]))
            self.assertTrue(again["already_running"])
            self.assertEqual(run_cli("dashboard", "--stop")[0], 0)
            code, restarted = run_cli("dashboard", "--detach")
            self.assertEqual(code, 0, restarted)
            self.assertEqual(restarted["url"], started["url"])
        finally:
            run_cli("dashboard", "--stop")


class StateTests(unittest.TestCase):
    def setUp(self):
        self.s = TempSet()

    def tearDown(self):
        self.s.cleanup()

    def put(self, answers):
        ask.write_json_atomic(self.s.dir / "answers.json", {"askwright": 1, "rev": len(answers), "answers": answers})

    def test_status_lists(self):
        self.put({
            "arrow": {"choice": "t5", "q_rev": 1, "rev": 1},
            "music": {"note": "too loud", "rev": 2},
            "cuts": {"choice": "unsure", "rev": 3},
        })
        st = ask.summarize(self.s.dir)
        self.assertEqual(st["note_only"], ["music"])
        self.assertEqual(st["unsure"], ["cuts"])
        self.assertIn("order", st["unanswered"])
        self.assertNotIn("old-intro", st["unanswered"])  # superseded
        self.assertNotIn("redo-how", st["unanswered"])  # show_if not met (arrow is t5)
        self.assertEqual(st["stale"], ["arrow"])  # answered rev 1, question is now rev 2
        self.assertFalse(st["done"])

    def test_show_if_waiting_then_open(self):
        st = ask.summarize(self.s.dir)
        self.assertIn("redo-how", st["waiting"])
        self.put({"arrow": {"choice": "redo", "q_rev": 2, "rev": 1}})
        self.assertIn("redo-how", ask.summarize(self.s.dir)["unanswered"])

    def test_read(self):
        self.put({"arrow": {"choice": "t5", "q_rev": 2, "rev": 1, "note": "good", "timecodes": [{"t": 1.2}]},
                  "music": {"choice": "tone", "rev": 2, "guess_revealed": True, "guess_revealed_before_pick": True},
                  "order": {"order": ["field", "news", "weather"], "rev": 3}})
        r = ask.read_answers(self.s.dir)
        by = {a["qid"]: a for a in r["answers"]}
        self.assertEqual(by["arrow"]["label"], "Take 5")
        self.assertTrue(by["arrow"]["matched_guess"])
        self.assertEqual(by["arrow"]["side"], "right")
        self.assertFalse(by["music"]["matched_guess"])
        self.assertTrue(by["music"]["guess_revealed_before_pick"])
        self.assertFalse(by["order"]["matched_guess"])
        self.assertEqual([a["qid"] for a in ask.read_answers(self.s.dir, since=2)["answers"]], ["order"])

    def test_kill_and_restart_keeps_answers(self):
        srv = ask.make_server(self.s.dir, port=0)
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()
        port = srv.server_address[1]
        c = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
        c.request("POST", "/api/answer", json.dumps({"qid": "music", "choice": "drums"}),
                  {"X-Ask-Token": srv.token, "Content-Type": "application/json", "Host": "127.0.0.1:%d" % port})
        self.assertEqual(c.getresponse().status, 200)
        srv.shutdown()
        srv.server_close()
        srv2 = ask.make_server(self.s.dir, port=0)
        try:
            self.assertEqual(ask.load_answers(self.s.dir)["answers"]["music"]["choice"], "drums")
        finally:
            srv2.server_close()


class CliTests(unittest.TestCase):
    def setUp(self):
        self.s = TempSet()

    def tearDown(self):
        self.s.cleanup()

    def test_lint_cli(self):
        code, d = run_cli("lint", self.s.dir, "--no-probe")
        self.assertEqual((code, d["ok"]), (0, True))
        self.s.q("music")["question"] = "No question mark"
        self.s.write(self.s.data)
        code, d = run_cli("lint", self.s.dir, "--no-probe")
        self.assertEqual((code, d["ok"]), (1, False))
        self.assertEqual(d["errors"][0]["q"], "music")

    def test_serve_refuses_on_lint_errors(self):
        self.s.q("music").pop("why")
        self.s.write(self.s.data)
        code, d = run_cli("serve", self.s.dir, "--no-probe")
        self.assertEqual(code, 1)
        self.assertIn("lint", d["error"])

    def test_close_and_add(self):
        code, d = run_cli("close", self.s.dir, "pace", "--withdrawn", "decided in chat")
        self.assertEqual(code, 0, d)
        data = json.loads((self.s.dir / "questions.json").read_text(encoding="utf-8"))
        pace = next(q for q in data["questions"] if q["id"] == "pace")
        self.assertEqual((pace["status"], pace["reason"]), ("withdrawn", "decided in chat"))
        new = copy.deepcopy(self.s.q("music"))
        new.update(id="music2", title="Music, second round", question="Which of the new music cues fits the intro?",
                   supersedes="music")
        qf = self.s.tmp / "new.json"
        qf.write_text(json.dumps(new), encoding="utf-8")
        code, d = run_cli("add", self.s.dir, qf, "--no-probe")
        self.assertEqual(code, 0, d)
        data = json.loads((self.s.dir / "questions.json").read_text(encoding="utf-8"))
        old = next(q for q in data["questions"] if q["id"] == "music")
        self.assertEqual((old["status"], old["superseded_by"]), ("superseded", "music2"))
        code, d = run_cli("add", self.s.dir, qf, "--no-probe")
        self.assertEqual(code, 1)  # id exists
        wrapped = self.s.tmp / "wrapped.json"  # the questions.json shape: {"questions": [...]}
        wrapped.write_text(json.dumps({"questions": [dict(new, id="music4", supersedes=None, title="Outro music",
                                                                   question="Which music cue fits the outro?")]}), encoding="utf-8")
        code, d = run_cli("add", self.s.dir, wrapped, "--no-probe")
        self.assertEqual((code, d.get("added")), (0, ["music4"]), d)
        bad = dict(new, id="music3", question="no mark")
        qf.write_text(json.dumps(bad), encoding="utf-8")
        before = (self.s.dir / "questions.json").read_text(encoding="utf-8")
        code, d = run_cli("add", self.s.dir, qf, "--no-probe")
        self.assertEqual(code, 1)
        self.assertEqual((self.s.dir / "questions.json").read_text(encoding="utf-8"), before)

    def test_inline(self):
        code, d = run_cli("inline", self.s.dir)
        self.assertFalse(d["eligible"])  # media and more than 4 questions
        small = {"askwright": 1, "id": "small", "title": "Two quick calls", "questions": [
            q for q in good()["questions"] if q["id"] in ("cuts",)]}
        (self.s.dir / "questions.json").write_text(json.dumps(small), encoding="utf-8")
        code, d = run_cli("inline", self.s.dir)
        self.assertTrue(d["eligible"], d)
        self.assertIn("Which shots should be cut", d["text"])
        aq = d["ask_user_question"]["questions"][0]
        self.assertTrue(aq["multiSelect"])
        self.assertLessEqual(len(aq["header"]), 12)

    def test_new(self):
        nd = self.s.tmp / "ask" / "fresh"
        code, d = run_cli("new", nd, "--title", "Fresh set")
        self.assertEqual(code, 0, d)
        data = json.loads((nd / "questions.json").read_text(encoding="utf-8"))
        self.assertEqual((data["id"], data["askwright"]), ("fresh", 1))
        self.assertEqual(run_cli("new", nd, "--title", "Again")[0], 1)

    def test_serve_detach_status_stop(self):
        code, d = run_cli("serve", self.s.dir, "--detach", "--no-probe")
        self.assertEqual(code, 0, d)
        try:
            self.assertTrue(d["url"].startswith("http://127.0.0.1:"))
            sj = json.loads((self.s.dir / "server.json").read_text(encoding="utf-8"))
            self.assertEqual(sj["pid"], d["pid"])
            code2, d2 = run_cli("serve", self.s.dir, "--no-probe")
            self.assertTrue(d2.get("already_running"), d2)
            code, st = run_cli("status", self.s.dir)
            self.assertEqual(st["server"]["url"], d["url"])
        finally:
            code, d3 = run_cli("stop", self.s.dir)
        self.assertTrue(d3["stopped"], d3)
        self.assertFalse((self.s.dir / "server.json").exists())

    def test_wait_done_times_out(self):
        code, d = run_cli("status", self.s.dir, "--wait-done", "--timeout", "1", "--interval", "0.2")
        self.assertTrue(d["timed_out"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
