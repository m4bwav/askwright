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

    def test_unknown_post_body_is_consumed_before_next_request(self):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        headers = {"Host": "127.0.0.1:%d" % self.port, "X-Ask-Token": self.srv.token,
                   "Origin": "http://127.0.0.1:%d" % self.port, "Content-Type": "application/json"}
        try:
            for path in ("/api/answer", "/api/submit"):
                connection.request("POST", path, json.dumps({"text": "x" * 4096}), headers)
                response = connection.getresponse()
                self.assertEqual(response.status, 404)
                response.read()
                connection.request("GET", "/api/sessions", headers=headers)
                response = connection.getresponse()
                self.assertEqual(response.status, 200)
                self.assertTrue(json.loads(response.read())["ok"])
        finally:
            connection.close()

    def test_dashboard_port_rebinds_after_close_but_cannot_be_shared(self):
        self.assertEqual(self.req("GET", "/", headers={"Connection": "close"})[0], 200)
        with self.assertRaises(OSError):
            ask.make_dashboard_server(self.port)
        self.srv.shutdown()
        self.srv.server_close()
        self.srv = ask.make_dashboard_server(self.port)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.assertEqual(self.srv.server_address[1], self.port)
        self.assertTrue(ask.self_check(self.srv)["ok"])

    def test_stop_tolerates_concurrent_server_info_removal(self):
        info_file = self.s.dir / "server.json"
        info = {"pid": 123, "port": 12345, "token": "test-token", "set_dir": str(self.s.dir)}
        ask.write_json_atomic(info_file, info)
        exists = Path.exists

        def removed_after_check(path):
            if path == info_file:
                info_file.unlink()
                return True
            return exists(path)

        with mock.patch.object(ask, "ping", side_effect=[info, None]), \
                mock.patch.object(ask.os, "kill") as kill, \
                mock.patch.object(Path, "exists", new=removed_after_check), \
                mock.patch.object(ask, "emit", side_effect=lambda result: result):
            result = ask.stop_server(self.s.dir)
        self.assertTrue(result["stopped"])
        kill.assert_called_once_with(123, ask.signal.SIGTERM)
        self.assertFalse(info_file.exists())

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

    def test_study_preview_never_includes_answer_keys(self):
        study_set = StudySet()
        try:
            ask.register_set(study_set.dir)
            row = self.api("/api/sessions")[1]["sessions"][0]
            self.assertNotIn("error", row)
            self.assertTrue(row["next_questions"])
            self.assertTrue(all(set(q) == {"id", "question"} for q in row["next_questions"]))
            self.assertEqual(row["pending"], len(study_set.data["questions"]))
            self.assertEqual(self.api("/api/submit", {})[0], 404)
            self.assertEqual(self.api("/api/retake", {})[0], 404)
        finally:
            study_set.cleanup()

    def test_study_attempts_survive_dashboard_actions(self):
        study_set = StudySet()
        srv = ask.make_server(study_set.dir)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            sid = ask.register_set(study_set.dir)
            self.assertTrue(ask.self_check(srv)["ok"])
            before = {name: (study_set.dir / name).read_bytes() for name in ("questions.json", "results.json")}
            for action in ({"action": "snooze", "seconds": 86400}, {"action": "archive"}, {"action": "restore"}):
                code, result = self.api("/api/session-state", dict(action, id=sid))
                self.assertEqual(code, 200, result)
            self.assertEqual(before, {name: (study_set.dir / name).read_bytes() for name in before})
            self.assertFalse((study_set.dir / "answers.json").exists())
        finally:
            srv.shutdown()
            srv.server_close()
            study_set.cleanup()

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

    def test_back_link(self):
        nd = self.s.tmp / "ask" / "linked"
        code, d = run_cli("new", nd, "--title", "Linked", "--back-link", "http://127.0.0.1:8765/", "Pick page")
        self.assertEqual(code, 0, d)
        data = json.loads((nd / "questions.json").read_text(encoding="utf-8"))
        self.assertEqual(data["back_link"], {"url": "http://127.0.0.1:8765/", "label": "Pick page"})
        ok = lambda data: data.update(back_link={"url": "http://127.0.0.1:8765/", "label": "Pick page"})
        self.assertNotIn("back-link", lint(ok)[0])
        for bad in ({"url": "javascript:alert(1)", "label": "x"}, {"url": "http://x/"}, "http://x/"):
            self.assertIn("back-link", lint(lambda data, bad=bad: data.update(back_link=bad))[0])

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


def study():
    return json.loads((FIX / "study" / "questions.json").read_text(encoding="utf-8"))


class StudySet:
    """A copy of the study fixture (a quiz) in a temp dir, optionally mutated."""

    def __init__(self, mutate=None):
        self.dir = Path(tempfile.mkdtemp(prefix="askw-study-"))
        self.data = study()
        if mutate:
            mutate(self.data)
        (self.dir / "questions.json").write_text(json.dumps(self.data, indent=2), encoding="utf-8")

    def lint(self):
        d, data = ask.load_set(self.dir)
        errs, warns = ask.lint_set(d, data, probe=False)
        return {e["rule"] for e in errs}, {w["rule"] for w in warns}

    def cleanup(self):
        shutil.rmtree(self.dir, ignore_errors=True)


def slint(mutate):
    s = StudySet(mutate)
    try:
        return s.lint()
    finally:
        s.cleanup()


def sq(qid, fn):
    def m(data):
        fn(next(q for q in data["questions"] if q["id"] == qid))
    return m


class StudyLintTests(unittest.TestCase):
    def test_study_fixture_is_clean(self):
        self.assertEqual(slint(None), (set(), set()))

    def test_one_right_answer_and_a_why_on_every_option(self):
        self.assertIn("study-correct", slint(sq("frac-half", lambda q: q["options"][0].pop("correct")))[0])
        self.assertIn("study-correct", slint(sq("frac-half", lambda q: q["options"][1].update(correct=True)))[0])
        self.assertIn("study-why", slint(sq("frac-half", lambda q: q["options"][2].pop("why")))[0])

    def test_written_needs_rubric_and_points_are_positive(self):
        def strip(q):
            q.pop("rubric")
            q.pop("model_answer")
        self.assertIn("study-rubric", slint(sq("water-explain", strip))[0])
        self.assertIn("points", slint(sq("water-explain", lambda q: q.update(points=0)))[0])
        self.assertIn("points", slint(sq("water-explain", lambda q: q.update(points=True)))[0])

    def test_kinds_mode_and_topic(self):
        self.assertIn("study-kind", slint(sq("frac-half", lambda q: q.update(kind="rank")))[0])
        self.assertIn("mode", slint(lambda d: d.update(mode="exam"))[0])
        self.assertIn("topic", slint(sq("frac-half", lambda q: q.pop("topic")))[1])
        self.assertIn("study-few-options", slint(sq("frac-half", lambda q: q.update(options=q["options"][:2])))[1])

    def test_decide_rules_relaxed_in_study(self):
        # no guess, no question-level why, a position word ("Left") as an answer: all fine in a quiz
        errs, warns = slint(sq("frac-half", lambda q: q["options"][1].update(label="Left")))
        self.assertEqual((errs, warns), (set(), set()))

    def test_quiz_wording_rules(self):
        # the ask may come before a quoted sentence; options may differ only in capital letters
        quoted = sq("frac-half", lambda q: q.update(question='Which word is the verb? "Our coach runs."'))
        self.assertNotIn("question-mark", slint(quoted)[0])
        self.assertIn("question-mark", slint(sq("frac-half", lambda q: q.update(question="Find the verb.")))[0])
        caps = sq("frac-half", lambda q: (q["options"][0].update(label="After it, we ran."),
                                          q["options"][1].update(label="After it, We ran.")))
        self.assertNotIn("option-label", slint(caps)[0])
        self.assertIn("question-mark", lint(qmod("pace", lambda q: q.update(question='Which? "Quoted."')))[0])

    def test_longest_right_answer_warns(self):
        def pad(data):
            for q in data["questions"]:
                for o in q.get("options") or []:
                    if o.get("correct"):
                        o["label"] += " and that is the full and careful answer"
        self.assertIn("study-longest-right", slint(pad)[1])

    def test_key_fields_in_a_decide_set_warn(self):
        self.assertIn("study-fields", lint(qmod("pace", lambda q: q["options"][0].update(correct=True)))[1])


class FigureTests(unittest.TestCase):
    GRAPH = {"type": "graph", "x_label": "Time (s)", "y_label": "Distance (m)",
             "lines": [{"label": "A & <B>", "points": [[0, 0], [5, 40]], "marks": [{"x": 2, "y": 16, "label": "C"}]}]}
    FORCES = {"type": "forces", "object": "box", "forces": [{"dir": "right", "newtons": 30}, {"dir": "left", "newtons": 12},
                                                          {"dir": "right", "newtons": 5, "label": "push"}]}

    def test_each_type_renders_well_formed_svg(self):
        import xml.etree.ElementTree as ET
        shapes = {"type": "shapes", "items": [{"shape": "rect", "x": 1, "y": 1, "w": 9, "h": 9, "label": "r"},
                                              {"shape": "circle", "x": 5, "y": 5, "r": 3},
                                              {"shape": "arrow", "x1": 0, "y1": 0, "x2": 9, "y2": 9},
                                              {"shape": "text", "x": 3, "y": 3, "text": "hi"}]}
        for fig in (self.GRAPH, self.FORCES, shapes):
            self.assertEqual(ask.figure_errors(fig), [])
            root = ET.fromstring(ask.render_figure(fig))
            self.assertTrue(root.tag.endswith("svg"))
        svg = ask.render_figure(self.GRAPH)
        self.assertIn("A &amp; &lt;B&gt;", svg)  # labels are escaped
        self.assertIn("12 N", ask.render_figure(self.FORCES))
        self.assertTrue(ask.figure_url(self.FORCES).startswith("data:image/svg+xml;base64,"))

    def test_bad_specs_are_lint_errors(self):
        for bad in ({"type": "pie"}, {"type": "graph", "lines": [{"points": [[0, 0]]}]},
                    {"type": "forces", "forces": [{"dir": "sideways", "newtons": 3}]},
                    {"type": "shapes", "items": [{"shape": "rect", "x": 1}]}, "graph"):
            self.assertTrue(ask.figure_errors(bad), bad)
        errs, warns = slint(sq("frac-half", lambda q: q.update(media=[{"figure": {"type": "pie"}}])))
        self.assertIn("figure", errs)
        self.assertIn("alt", warns)

    def test_page_gets_a_data_url_and_self_check_skips_it(self):
        s = StudySet()
        srv = ask.make_server(s.dir, port=0)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            st = ask.page_set(srv)
            q = next(x for x in st["questions"] if x["id"] == "frac-compare")
            self.assertEqual(q["media"][0]["type"], "image")
            self.assertTrue(q["media"][0]["url"].startswith("data:image/svg+xml;base64,"))
            self.assertNotIn("figure", q["media"][0])
            c = ask.self_check(srv)
            self.assertTrue(c["ok"], c)
        finally:
            srv.shutdown()
            srv.server_close()
            s.cleanup()

    def test_figure_cli(self):
        tmp = Path(tempfile.mkdtemp(prefix="askw-fig-"))
        try:
            (tmp / "f.json").write_text(json.dumps({"figure": self.GRAPH}), encoding="utf-8")
            code, d = run_cli("figure", tmp / "f.json", tmp / "f.svg")
            self.assertEqual(code, 0, d)
            self.assertTrue((tmp / "f.svg").read_text(encoding="utf-8").startswith("<svg"))
            (tmp / "f.json").write_text(json.dumps({"type": "pie"}), encoding="utf-8")
            self.assertEqual(run_cli("figure", tmp / "f.json", tmp / "g.svg")[0], 1)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class StudyScoreTests(unittest.TestCase):
    def test_score_by_topic_pending_and_bonus(self):
        data = study()
        answers = {"frac-half": {"choice": "four"}, "frac-compare": {"choice": "eighth"},
                   "water-evap": {"choice": "air"}, "water-explain": {"text": "It evaporates and rains."},
                   "frac-bonus": {"text": "2/3 each"}}
        sc = ask.study_score(data, answers)
        self.assertEqual((sc["earned"], sc["max"], sc["pending_points"]), (2, 6, 2))
        self.assertEqual(sc["unanswered"], ["water-cond"])
        self.assertEqual(sc["wrong"], ["frac-compare"])
        self.assertEqual(sorted(sc["pending"]), ["frac-bonus", "water-explain"])
        self.assertEqual(sc["by_topic"]["Fractions"], {"earned": 1, "max": 2, "pending": 0})  # bonus is not counted
        self.assertEqual(sc["by_topic"]["The water cycle"], {"earned": 1, "max": 4, "pending": 2})
        sc = ask.study_score(data, answers, {"water-explain": {"points": 1}, "frac-bonus": {"points": 1}})
        self.assertEqual((sc["earned"], sc["pending_points"], sc["bonus_earned"]), (3, 0, 1))
        self.assertEqual(sc["partial"], ["water-explain"])

    def test_option_order_is_shuffled_by_seed_and_stable(self):
        q = study()["questions"][0]
        orders = {tuple(ask.option_order(q, seed)) for seed in range(40)}
        self.assertGreater(len(orders), 5)
        self.assertEqual(ask.option_order(q, 7), ask.option_order(q, 7))
        self.assertEqual(ask.option_order(dict(q, shuffle=False), 7), ask.option_ids(q))


class StudyServerTests(unittest.TestCase):
    def setUp(self):
        self.s = StudySet()
        self.srv = ask.make_server(self.s.dir, port=0)
        self.port = self.srv.server_address[1]
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def tearDown(self):
        self.srv.shutdown()
        self.srv.server_close()
        self.s.cleanup()

    def call(self, path, payload=None):
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        h = {"Host": "127.0.0.1:%d" % self.port, "X-Ask-Token": self.srv.token,
             "Origin": "http://127.0.0.1:%d" % self.port, "Content-Type": "application/json"}
        c.request("POST" if payload is not None else "GET", path, json.dumps(payload) if payload is not None else None, h)
        r = c.getresponse()
        body = json.loads(r.read())
        c.close()
        return r.status, body

    def answer(self, qid, real):
        """Posts a pick the way the page does: by the neutral id this attempt shows for that option."""
        q = next(x for x in self.s.data["questions"] if x["id"] == qid)
        alias = ask.option_aliases(q, ask.current_seed(self.s.dir)).get(real, real)
        return self.call("/api/answer", {"qid": qid, "choice": alias})

    def test_key_is_hidden_until_submit_then_scored(self):
        st, d = self.call("/api/set")
        self.assertEqual((st, d["mode"], d["study"]["attempt"], d["study"]["submitted"]), (200, "study", 1, False))
        raw = json.dumps(d["questions"])
        for secret in ('"correct"', "Half of 8 is 8 divided by 2", "model_answer", "rubric", "The sun heats sea water"):
            self.assertNotIn(secret, raw)
        res = ask.load_results(self.s.dir)
        q0 = next(q for q in d["questions"] if q["id"] == "frac-half")
        self.assertEqual([o["id"] for o in q0["options"]], ["o1", "o2", "o3", "o4"])  # ids never give the answer away
        labels = {o["id"]: o["label"] for o in self.s.data["questions"][0]["options"]}
        self.assertEqual([o["label"] for o in q0["options"]],
                         [labels[i] for i in ask.option_order(self.s.data["questions"][0], res["attempts"][0]["seed"])])
        self.assertEqual(self.answer("frac-half", "four")[0], 200)
        self.assertEqual(self.answer("frac-half", "unsure")[0], 400)  # no extras
        self.assertEqual(self.answer("water-cond", "leak")[0], 200)
        self.assertEqual(self.call("/api/answer", {"qid": "water-explain", "text": "Sun, vapor, clouds, rain."})[0], 200)
        st, r = self.call("/api/submit", {})
        self.assertEqual(st, 200, r)
        sc = r["review"]["score"]
        self.assertEqual((sc["earned"], sc["max"], sc["pending_points"]), (1, 6, 2))
        rq = {q["qid"]: q for q in r["review"]["questions"]}
        self.assertEqual(rq["water-cond"]["status"], "wrong")
        self.assertTrue(any(o["correct"] and o["why"] for o in rq["water-cond"]["options"]))
        self.assertEqual(rq["water-explain"]["status"], "pending")
        self.assertEqual(self.answer("frac-compare", "third")[0], 409)
        self.assertEqual(self.call("/api/submit", {})[0], 409)
        st, d = self.call("/api/set")
        self.assertTrue(d["study"]["submitted"])
        self.assertEqual(d["review"]["score"]["earned"], 1)
        self.assertEqual(ask.summarize(self.s.dir)["done"], True)

    def test_retake_keeps_earlier_attempts(self):
        self.assertEqual(self.call("/api/retake", {})[0], 409)  # nothing submitted yet
        self.call("/api/set")
        self.answer("frac-half", "two")
        self.call("/api/submit", {})
        st, r = self.call("/api/retake", {})
        self.assertEqual((st, r["attempt"]), (200, 2))
        self.assertEqual(ask.load_answers(self.s.dir)["answers"], {})
        res = ask.load_results(self.s.dir)
        self.assertEqual([a["n"] for a in res["attempts"]], [1, 2])
        self.assertEqual(res["attempts"][0]["answers"]["frac-half"], {"choice": "two"})
        self.assertIsNone(res["attempts"][1]["submitted"])
        st, d = self.call("/api/set")
        self.assertEqual((d["study"]["attempt"], d["study"]["submitted"], d["review"]), (2, False, None))
        self.assertEqual([a["n"] for a in d["study"]["attempts"]], [1])
        self.assertFalse(ask.summarize(self.s.dir)["done"])

    def test_decide_set_refuses_study_routes(self):
        s = TempSet()
        srv = ask.make_server(s.dir, port=0)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            self.port, keep, self.srv = srv.server_address[1], self.srv, srv
            st, _ = self.call("/api/submit", {})
            self.assertEqual(st, 400)
            st, d = self.call("/api/set")
            self.assertEqual(d["mode"], "decide")
            self.assertNotIn("study", d)
        finally:
            self.srv = keep
            self.port = keep.server_address[1]
            srv.shutdown()
            srv.server_close()
            s.cleanup()

    def test_grade_round_trip(self):
        self.call("/api/set")
        self.answer("frac-half", "four")
        self.call("/api/answer", {"qid": "water-explain", "text": "The sun makes it vapor, then it rains."})
        self.call("/api/answer", {"qid": "frac-bonus", "text": "Two thirds."})
        code, d = run_cli("grade", self.s.dir)
        self.assertEqual(code, 1)  # nothing submitted yet
        self.call("/api/submit", {})
        code, d = run_cli("grade", self.s.dir)
        self.assertEqual(code, 0, d)
        self.assertEqual(sorted(i["qid"] for i in d["ungraded"]), ["frac-bonus", "water-explain"])
        item = next(i for i in d["ungraded"] if i["qid"] == "water-explain")
        self.assertEqual((item["points"], len(item["rubric"])), (2, 2))
        self.assertIn("vapor", item["answer"])
        gf = self.s.dir.parent / (self.s.dir.name + "-grades.json")
        try:
            gf.write_text(json.dumps({"water-explain": {"points": 3}}), encoding="utf-8")
            code, d = run_cli("grade", self.s.dir, "--apply", gf)
            self.assertEqual(code, 1)  # over the question's points: nothing saved
            gf.write_text(json.dumps({"frac-half": {"points": 1}}), encoding="utf-8")
            self.assertEqual(run_cli("grade", self.s.dir, "--apply", gf)[0], 1)  # not a written question
            gf.write_text(json.dumps({"grades": {"water-explain": {"points": 1, "feedback": "Say where it condenses."},
                                                 "frac-bonus": {"points": 1}}}), encoding="utf-8")
            code, d = run_cli("grade", self.s.dir, "--apply", gf)
            self.assertEqual(code, 0, d)
            self.assertEqual((d["earned"], d["pending_points"], d["bonus_earned"]), (2, 0, 1))
        finally:
            gf.unlink()
        code, d = run_cli("grade", self.s.dir)
        self.assertEqual((d["ungraded"], len(d["graded"])), ([], 2))
        st, page = self.call("/api/set")  # the review page sees the grade at its next poll
        rq = {q["qid"]: q for q in page["review"]["questions"]}
        self.assertEqual((rq["water-explain"]["status"], rq["water-explain"]["grade"]["feedback"]),
                         ("partial", "Say where it condenses."))
        r = ask.read_answers(self.s.dir)
        self.assertEqual((r["mode"], r["attempt"], r["score"]["earned"]), ("study", 1, 2))
        by = {q["qid"]: q for q in r["questions"]}
        self.assertEqual((by["frac-half"]["status"], by["frac-half"]["picked"], by["frac-half"]["right"]),
                         ("right", "4 slices", "4 slices"))
        self.assertEqual(by["water-cond"]["status"], "unanswered")
        code, st = run_cli("status", self.s.dir)
        self.assertEqual(st["study"]["attempts"][0]["earned"], 2)

    def test_inline_refuses_a_study_set(self):
        code, d = run_cli("inline", self.s.dir)
        self.assertFalse(d["eligible"])
        self.assertIn("study set", d["reason"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
