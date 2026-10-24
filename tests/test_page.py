"""Browser tests for the askwright page (Playwright with installed Chrome or Edge, for H.264). Development only.

Run from the repository root: python tests/test_page.py
Point the generic tests at a real set (they run on a temp copy, so its answers are never touched):
    ASKW_SET=<set dir> python tests/test_page.py GenericPageTests
Skips with a message when Playwright or a branded browser is missing.
"""

import base64
import json
import os
import shutil
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "askwright" / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import ask  # noqa: E402

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None

AXE = ROOT / "tests" / "vendor" / "axe.min.js"
FIX = ROOT / "tests" / "fixtures"
PNG = (FIX / "media" / "swatch.png").read_bytes()
_pw = _browser = None
_why_skip = None


def setUpModule():
    global _pw, _browser, _why_skip
    if sync_playwright is None:
        _why_skip = "playwright is not installed (pip install playwright); page tests skipped"
        return
    _pw = sync_playwright().start()
    for channel in ("chrome", "msedge"):
        try:
            _browser = _pw.chromium.launch(channel=channel)
            return
        except Exception:  # noqa: BLE001 - try the next browser
            continue
    _why_skip = "neither Chrome nor Edge is installed; page tests need one for H.264"


def tearDownModule():
    if _browser:
        _browser.close()
    if _pw:
        _pw.stop()


def copy_set(src_dir):
    """Copy questions.json to a temp folder, pointing media_roots back at the original files."""
    d, data = ask.load_set(src_dir)
    tmp = Path(tempfile.mkdtemp(prefix="askw-page-"))
    roots = [str(r) for r in ask.media_roots(d, data)]
    data["media_roots"] = roots
    (tmp / "questions.json").write_text(json.dumps(data), encoding="utf-8")
    return tmp


class PageCase(unittest.TestCase):
    SET = FIX / "good"

    def setUp(self):
        if _why_skip:
            self.skipTest(_why_skip)
        self.dir = copy_set(self.SET)
        self.srv = ask.make_server(self.dir, port=0)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.url = "http://127.0.0.1:%d/" % self.srv.server_address[1]
        self.errors = []
        self.ctx = _browser.new_context(bypass_csp=True, viewport={"width": 1100, "height": 900})
        self.page = self.ctx.new_page()
        self.page.on("pageerror", lambda e: self.errors.append(str(e)))
        self.page.on("console", lambda m: m.type == "error" and self.errors.append(m.text))
        self.page.set_default_timeout(10000)

    def tearDown(self):
        if getattr(self, "ctx", None):
            self.ctx.close()
        if getattr(self, "srv", None):
            self.srv.shutdown()
            self.srv.server_close()
            shutil.rmtree(self.dir, ignore_errors=True)

    def open(self):
        self.page.goto(self.url)
        self.page.wait_for_selector("[data-q], h1")
        return self.page

    def qid(self):
        return self.page.get_attribute("[data-q]", "data-q")

    def answers(self):
        return ask.load_answers(self.dir)["answers"]

    def wait_saved(self):
        self.page.wait_for_function("document.querySelector('#save-status').textContent.startsWith('Saved')")

    def axe(self, label):
        if not AXE.exists():
            self.skipTest("tests/vendor/axe.min.js is missing")
        self.page.add_script_tag(path=str(AXE))
        res = self.page.evaluate("async () => (await axe.run(document, {resultTypes: ['violations']})).violations"
                                 ".map(v => ({id: v.id, impact: v.impact, nodes: v.nodes.length}))")
        bad = [v for v in res if v["impact"] in ("serious", "critical")]
        self.assertEqual(bad, [], "%s: axe found %s" % (label, bad))

    def kind(self):
        return next(q for q in ask.load_set(self.dir)[1]["questions"] if q["id"] == self.qid())["kind"]


class GenericPageTests(PageCase):
    """Hold for any valid set: the fixture by default, or ASKW_SET."""

    SET = Path(os.environ["ASKW_SET"]) if os.environ.get("ASKW_SET") else FIX / "good"

    def test_one_question_per_screen_nothing_preselected(self):
        p = self.open()
        self.assertEqual(p.locator("[data-q]").count(), 1)
        self.assertEqual(p.locator("input[type=radio]:checked, input[type=checkbox]:checked").count(), 0)
        self.assertTrue(p.locator("h1").inner_text().strip().endswith("?"))
        self.assertEqual(self.errors, [])

    def test_keyboard_only_to_all_done(self):
        p = self.open()
        p.locator("h1").focus()
        seen = []
        for _ in range(40):
            if p.locator("[data-q]").count() == 0:
                break
            seen.append(self.qid())
            p.keyboard.press("u" if self.kind() in ("rank", "text") else "1")
            p.locator("h1").focus()
            p.keyboard.press("n")
            p.wait_for_timeout(150)
        self.assertEqual(p.locator("h1").inner_text(), "Check your answers")
        self.wait_saved()
        p.get_by_role("button", name="All done").focus()
        p.keyboard.press("Enter")
        p.wait_for_selector(".done-msg:has-text('Thank you')")
        st = ask.summarize(self.dir)
        self.assertTrue(st["done"])
        self.assertEqual(st["unanswered"], [], st)
        self.assertEqual(len(seen), len(set(seen)), "a question came round twice: %s" % seen)

    def test_media_plays(self):
        p = self.open()
        for _ in range(40):
            if p.locator("[data-q] .media video").count():
                break
            if p.locator("[data-q]").count() == 0:
                self.skipTest("no video in this set")
            p.click("#btn-next")
            p.wait_for_timeout(100)
        v = p.locator("[data-q] .media video").first
        p.wait_for_function("document.querySelector('.media video').readyState >= 2")
        t0 = v.evaluate("v => v.currentTime")
        v.evaluate("v => { v.muted = true; return v.play(); }")
        p.wait_for_function("t => document.querySelector('.media video').currentTime > t + 0.2", arg=t0)

    def test_axe_each_screen_both_themes(self):
        for scheme in ("light", "dark"):
            self.page.emulate_media(color_scheme=scheme)
            p = self.open()
            self.axe(scheme + " question")
            p.keyboard.press("o")
            p.wait_for_selector("h1:has-text('All questions')")
            self.axe(scheme + " overview")
            p.click("#btn-next")
            p.wait_for_selector("h1:has-text('Check your answers')")
            self.axe(scheme + " finish")


class FixturePageTests(PageCase):
    def go(self, qid):
        p = self.page
        for _ in range(20):
            if self.qid() == qid:
                return
            p.click("#btn-next")
            p.wait_for_timeout(100)
        self.fail("never reached %s" % qid)

    def test_compare_sides_revealed_after_pick(self):
        p = self.open()
        self.assertEqual(self.qid(), "arrow")
        self.assertEqual(p.locator(".opt[data-oid=t2] .label").inner_text(), "Left")
        self.assertIn("My guess: Right", p.locator(".guess").inner_text())
        p.keyboard.press("1")
        p.wait_for_selector(".opt[data-oid=t2] .label:has-text('Left (Take 2)')")
        self.wait_saved()
        self.assertEqual(self.answers()["arrow"]["choice"], "t2")

    def test_answered_leave_the_line_and_come_back(self):
        p = self.open()
        p.keyboard.press("1")
        self.wait_saved()
        p.click("#btn-next")
        p.click("#btn-next")
        p.click("#btn-back")
        p.click("#btn-back")
        self.assertEqual(self.qid(), "arrow")  # Back still reaches it, read-only
        self.assertTrue(p.locator("#ans input").first.is_disabled())
        p.click("text=Change")
        self.assertFalse(p.locator("#ans input").first.is_disabled())
        for _ in range(12):  # Next never comes back round to the answered question
            p.click("#btn-next")
            p.wait_for_timeout(80)
            if p.locator("[data-q]").count() == 0:
                break
            self.assertNotEqual(self.qid(), "arrow")
        p.click("#btn-answered")
        p.keyboard.press("o")
        p.click(".tasks a:has-text('The arrow shot')")
        self.assertEqual(self.qid(), "arrow")

    def test_show_if(self):
        p = self.open()
        p.keyboard.press("4")  # Neither: redo the shot
        self.wait_saved()
        self.assertIn("redo", p.locator("#btn-next").inner_text().lower())
        p.click("#btn-next")
        self.assertEqual(self.qid(), "redo-how")

    def test_low_guess_hidden_and_reveal_recorded(self):
        p = self.open()
        self.go("music")
        self.assertEqual(p.locator("#guess-line").count(), 0)
        p.click("text=Show my guess")
        p.wait_for_selector("#guess-line")
        self.wait_saved()
        p.keyboard.press("2")
        self.wait_saved()
        r = {a["qid"]: a for a in ask.read_answers(self.dir)["answers"]}
        self.assertTrue(r["music"]["guess_revealed_before_pick"])
        self.assertTrue(r["music"]["matched_guess"])

    def test_note_without_choice_is_note_only(self):
        p = self.open()
        self.go("music")
        p.fill("#note", "the tone clips at the end")
        self.wait_saved()
        p.click("#btn-next")
        p.wait_for_selector(".prompt")
        p.click("text=Go on without picking")
        p.wait_for_timeout(200)
        self.assertNotEqual(self.qid(), "music")
        self.assertEqual(self.answers()["music"]["state"], "note_only")
        self.assertIn("music", ask.summarize(self.dir)["note_only"])

    def test_paste_image_lands_in_attachments(self):
        p = self.open()
        p.evaluate("""b64 => {
            const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
            const dt = new DataTransfer();
            dt.items.add(new File([bytes], 'shot.png', {type: 'image/png'}));
            document.dispatchEvent(new ClipboardEvent('paste', {clipboardData: dt, bubbles: true}));
        }""", base64.b64encode(PNG).decode())
        p.wait_for_selector(".atts img")
        self.wait_saved()
        self.assertEqual((self.dir / "attachments" / "arrow-1.png").read_bytes(), PNG)
        self.assertEqual(self.answers()["arrow"]["attachments"], ["attachments/arrow-1.png"])
        p.set_input_files(".note input[type=file]", str(FIX / "media" / "swatch.png"))
        p.wait_for_selector(".atts figure:nth-child(2) img")

    def test_timecoded_note(self):
        p = self.open()
        p.wait_for_function("document.querySelector('.media video').readyState >= 2")
        p.evaluate("() => { const v = document.querySelector('.media video'); v.muted = true; return v.play(); }")
        p.wait_for_function("document.querySelector('.media video').currentTime > 0.7")
        p.click("#note")
        p.keyboard.type("x")
        self.assertTrue(p.evaluate("document.querySelector('.media video').paused"))
        p.click("text=Tie this note to")
        self.wait_saved()
        self.assertGreater(self.answers()["arrow"]["timecodes"][0]["t"], 0.5)

    def test_resume_line_names_what_is_left(self):
        p = self.open()
        p.keyboard.press("1")
        self.wait_saved()
        time.sleep(1.1)
        p.reload()
        p.wait_for_selector("#notice:not([hidden])")
        txt = p.locator("#notice").inner_text()
        self.assertIn("Welcome back", txt)
        self.assertIn("Music under the intro", txt)
        self.assertNotIn("The arrow shot,", txt)
        self.assertEqual(self.qid(), "music")

    def test_one_pager_and_rank_and_text(self):
        p = self.open()
        self.go("render")
        self.assertTrue(p.locator("details.onepager[open] table").first.is_visible())
        self.assertIn("every", p.locator(".onepager strong").first.inner_text())
        p.keyboard.press("o")
        p.click(".tasks a:has-text('Running order')")
        p.click("[aria-label='Move The field report up']")
        p.click("text=Use this order")
        self.wait_saved()
        self.assertEqual(self.answers()["order"]["order"], ["field", "news", "weather"])
        p.keyboard.press("o")
        p.click(".tasks a:has-text('Title card')")
        p.fill("#ans-text", "The Test Reel")
        self.wait_saved()
        self.assertEqual(self.answers()["title-card"]["state"], "answered")

    def test_poll_shows_added_questions(self):
        p = self.open()
        d, data = ask.load_set(self.dir)
        q = json.loads(json.dumps(next(x for x in data["questions"] if x["id"] == "title-card")))
        q.update(id="late", title="A late question", question="Is there a late question?")
        data["questions"].append(q)
        ask.write_json_atomic(self.dir / "questions.json", data)
        p.evaluate("() => window.dispatchEvent(new Event('focus'))")
        p.wait_for_selector("#notice:has-text('1 question was added')", timeout=25000)

    def test_no_console_errors_with_csp(self):
        ctx = _browser.new_context()
        page = ctx.new_page()
        errs = []
        page.on("console", lambda m: m.type == "error" and errs.append(m.text))
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.goto(self.url)
        page.wait_for_selector("[data-q]")
        page.keyboard.press("o")
        page.wait_for_timeout(300)
        ctx.close()
        self.assertEqual(errs, [])


if __name__ == "__main__":
    unittest.main(verbosity=1)
