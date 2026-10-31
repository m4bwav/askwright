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
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock
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
_home = _env = None


def setUpModule():
    global _pw, _browser, _why_skip, _home, _env
    _home = tempfile.TemporaryDirectory(prefix="askw-page-registry-")
    _env = mock.patch.dict(os.environ, {"ASKWRIGHT_HOME": _home.name})
    _env.start()
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
    _env.stop()
    _home.cleanup()


def copy_set(src_dir):
    """Copy questions.json to a temp folder, pointing media_roots back at the original files."""
    d, data = ask.load_set(src_dir)
    tmp = Path(tempfile.mkdtemp(prefix="askw-page-"))
    roots = [str(r) for r in ask.media_roots(d, data)]
    data["media_roots"] = roots
    (tmp / "questions.json").write_text(json.dumps(data), encoding="utf-8")
    return tmp


def more_menu(p):
    """Under 70rem the secondary top-bar links sit in the More menu: open it when it is shown."""
    if p.locator("#more").is_visible():
        p.click("#more > summary")


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


class DashboardPageTests(PageCase):
    def setUp(self):
        super().setUp()
        self.srv.shutdown()
        self.srv.server_close()
        self.home = tempfile.TemporaryDirectory(prefix="askw-inbox-")
        self.env = mock.patch.dict(os.environ, {"ASKWRIGHT_HOME": self.home.name})
        self.env.start()
        self.srv = ask.make_dashboard_server()
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.url = "http://127.0.0.1:%d/" % self.srv.server_address[1]
        self.other = copy_set(FIX / "good")
        for folder, title, product in ((self.dir, "Film review", "Copilot"), (self.other, "Site review", "Codex")):
            _, data = ask.load_set(folder)
            data.update(title=title, product=product, session="review-session")
            ask.write_json_atomic(folder / "questions.json", data)
            ask.register_set(folder)

    def tearDown(self):
        for folder in (self.dir, self.other):
            subprocess.run([sys.executable, str(ask.__file__), "stop", str(folder)], capture_output=True, timeout=30)
        shutil.rmtree(self.other, ignore_errors=True)
        super().tearDown()
        self.env.stop()
        self.home.cleanup()

    def open(self):
        self.page.goto(self.url)
        self.page.wait_for_selector("article")
        return self.page

    def test_filters_counts_accessibility_and_phone(self):
        p = self.open()
        self.assertEqual(p.locator("article").count(), 2)
        p.locator("#product").select_option("Codex")
        self.assertEqual(p.locator("article h2").all_text_contents(), ["Site review"])
        p.locator("#product").select_option("")
        p.locator("#search").fill("Film")
        self.assertEqual(p.locator("article h2").all_text_contents(), ["Film review"])
        p.locator("#search").fill("")
        for folder in (self.dir, self.other):
            _, data = ask.load_set(folder)
            for q in data["questions"]:
                q["status"] = "closed"
            ask.write_json_atomic(folder / "questions.json", data)
        p.locator("#refresh").click()
        p.wait_for_selector("article", state="detached")
        p.locator("#show-all").check()
        self.assertEqual(p.locator("article").count(), 2)
        self.assertIn("0 need attention", p.locator("article").first.inner_text())
        self.axe("dashboard light")
        p.emulate_media(color_scheme="dark")
        self.axe("dashboard dark")
        p.set_viewport_size({"width": 390, "height": 844})
        self.assertTrue(p.evaluate("document.documentElement.scrollWidth <= window.innerWidth"))
        self.assertEqual(self.errors, [])

    def test_next_five_preview_stays_expanded_after_refresh(self):
        p = self.open()
        card = p.locator("article").filter(has=p.get_by_role("heading", name="Film review", exact=True))
        preview = card.locator(".preview")
        self.assertFalse(preview.evaluate("el => el.open"))
        preview.locator("summary").focus()
        p.keyboard.press("Enter")
        self.assertTrue(preview.evaluate("el => el.open"))
        row = next(row for row in ask.list_sessions()["sessions"] if row["title"] == "Film review")
        self.assertEqual(preview.locator("li").all_text_contents(), [q["question"] for q in row["next_questions"]])
        self.assertEqual(preview.locator("li").count(), 5)
        self.axe("expanded question preview")
        _, data = ask.load_set(self.other)
        data["title"] = "Updated other session"
        ask.write_json_atomic(self.other / "questions.json", data)
        p.locator("#refresh").click()
        p.wait_for_selector("h2:has-text('Updated other session')")
        self.assertTrue(preview.evaluate("el => el.open"))
        self.assertEqual(self.errors, [])

    def test_snooze_archive_and_restore_persist_across_reload(self):
        p = self.open()
        film = p.locator("article").filter(has=p.get_by_role("heading", name="Film review", exact=True))
        film.locator(".snooze > summary").click()
        self.assertEqual(film.locator(".snooze-menu button").all_text_contents(),
                         ["1 hour", "4 hours", "1 day", "3 days", "1 week"])
        p.keyboard.press("Escape")
        self.assertFalse(film.locator(".snooze").evaluate("el => el.open"))
        film.locator(".snooze > summary").click()
        film.get_by_role("button", name="1 hour: Film review", exact=True).click()
        p.wait_for_function("!Array.from(document.querySelectorAll('article h2')).some(el => el.textContent === 'Film review')")
        p.locator("#show-all").check()
        self.assertEqual(p.locator("article").count(), 1)
        p.reload()
        p.wait_for_selector("article")
        self.assertEqual(p.locator("article h2").all_text_contents(), ["Site review"])
        p.locator('[data-view="snoozed"]').click()
        self.assertTrue(film.get_by_text("Snoozed until", exact=False).is_visible())
        self.axe("snoozed sessions")
        film.get_by_role("button", name="Unsnooze: Film review", exact=True).click()
        p.wait_for_selector("article", state="detached")
        p.locator('[data-view="inbox"]').click()
        film.get_by_role("button", name="Archive: Film review", exact=True).click()
        p.wait_for_function("document.querySelectorAll('article').length === 1")
        p.locator("#show-all").check()
        self.assertEqual(p.locator("article h2").all_text_contents(), ["Site review"])
        p.locator('[data-view="archived"]').click()
        self.assertEqual(p.locator("article h2").all_text_contents(), ["Film review"])
        self.axe("archived sessions")
        film.get_by_role("button", name="Unarchive: Film review", exact=True).click()
        p.wait_for_selector("article", state="detached")
        p.locator('[data-view="inbox"]').click()
        self.assertEqual(p.locator("article").count(), 2)
        self.assertEqual(self.errors, [])

    def test_snooze_expiry_returns_without_reload_and_errors_keep_card(self):
        p = self.open()
        film = p.locator("article").filter(has=p.get_by_role("heading", name="Film review", exact=True))
        p.route("**/api/session-state", lambda route: route.fulfill(
            status=500, content_type="application/json", body='{"ok":false,"error":"cannot save state"}'))
        film.get_by_role("button", name="Archive: Film review", exact=True).click()
        p.wait_for_selector("#error:visible")
        self.assertIn("cannot save state", p.locator("#error").inner_text())
        self.assertEqual(p.locator("article").count(), 2)
        self.assertTrue(film.get_by_role("button", name="Archive: Film review", exact=True).is_enabled())
        p.unroute("**/api/session-state")
        film.locator(".snooze > summary").click()
        film.get_by_role("button", name="4 hours: Film review", exact=True).click()
        p.wait_for_function("document.querySelectorAll('article').length === 1")
        sid = ask.register_set(self.dir)
        ask.write_json_atomic(ask.state_dir() / "session-state" / (sid + ".json"),
                              {"state": "snoozed", "snoozed_until": time.time() + .2})
        p.wait_for_selector("h2:has-text('Film review')", timeout=12000)
        self.assertEqual(p.locator("article").count(), 2)

    def test_live_refresh_and_open_stopped_session(self):
        p = self.open()
        _, data = ask.load_set(self.other)
        data["title"] = "Updated title"
        ask.write_json_atomic(self.other / "questions.json", data)
        p.wait_for_selector("h2:has-text('Updated title')", timeout=12000)
        p.get_by_role("button", name="Open questions: Film review", exact=True).click()
        p.wait_for_selector("[data-q]", timeout=60000)
        self.assertTrue(ask.server_info(self.dir)["alive"])
        self.assertEqual(self.errors, [])
        more_menu(p)
        p.get_by_role("link", name="All sessions", exact=True).click()
        p.wait_for_selector("article")
        self.assertEqual(p.locator("article").count(), 2)

    def test_empty_missing_and_failed_requests(self):
        p = self.open()
        (self.dir / "questions.json").unlink()
        p.locator("#refresh").click()
        p.wait_for_selector(".session-error")
        self.assertIn("no questions.json", p.locator(".session-error").inner_text())
        p.route("**/api/open", lambda route: route.fulfill(
            status=400, content_type="application/json", body='{"ok":false,"error":"lint failed"}'))
        p.get_by_role("button", name="Open questions: Site review", exact=True).click()
        p.wait_for_selector("#error:visible")
        self.assertIn("lint failed", p.locator("#error").inner_text())
        self.assertTrue(p.get_by_role("button", name="Open questions: Site review", exact=True).is_enabled())
        p.route("**/api/sessions", lambda route: route.fulfill(
            status=200, content_type="application/json", body='{"ok":true,"sessions":[]}'))
        p.locator("#refresh").click()
        p.wait_for_selector("#sessions:has-text('No sessions registered yet')")


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
        study = ask.is_study(ask.load_set(self.dir)[1])
        p.locator("h1").focus()
        seen = []
        for _ in range(40):
            if p.locator("[data-q]").count() == 0:
                break
            seen.append(self.qid())
            if study and self.kind() == "text":
                p.locator("#ans-text").focus()
                p.keyboard.type("An answer typed with the keyboard.")
            else:
                p.keyboard.press("u" if self.kind() in ("rank", "text") else "1")
            p.locator("h1").focus()
            p.keyboard.press("n")
            p.wait_for_timeout(150)
        self.assertEqual(p.locator("h1").inner_text(), "Check your answers")
        # A hint left out when everything is answered must not reach the page as the text "null".
        self.assertNotIn("null", p.locator("main").inner_text())
        self.wait_saved()
        p.get_by_role("button", name="Submit my answers" if study else "All done").focus()
        p.keyboard.press("Enter")
        p.wait_for_selector("h1:has-text('Your score')" if study else ".done-msg:has-text('Thank you')")
        st = ask.summarize(self.dir)
        self.assertTrue(st["done"])
        self.assertEqual(st["unanswered"], [], st)
        self.assertEqual(len(seen), len(set(seen)), "a question came round twice: %s" % seen)

    def test_media_plays(self):
        _, data = ask.load_set(self.dir)
        if not any(ask.media_type(m.get("src", ""), m.get("type")) == "video"
                   for q in data["questions"] for m in q.get("media") or []):
            self.skipTest("no video in this set")
        p = self.open()
        for _ in range(40):
            if p.locator("[data-q] .media video").count():
                break
            if p.locator("[data-q]").count() == 0:
                self.skipTest("no video in this set")
            p.click("#btn-next")
            p.wait_for_timeout(100)
        else:
            self.skipTest("no video in this set")  # Next cycles through unanswered questions, so it never ends
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
        self.assertFalse(p.locator("details.onepager").evaluate("el => el.open"))
        p.locator("details.onepager summary").click()
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

    def test_bars_whole_at_laptop_and_phone_width(self):
        # 0.2.0's score meter reused the class "bar" and squashed both bars to an 8 px clipped pill.
        p = self.open()
        for width in (1100, 390):
            p.set_viewport_size({"width": width, "height": 800})
            p.wait_for_function("w => document.querySelector('#more').hidden === (w > 1120)", arg=width)  # 70rem
            got = p.evaluate("""() => [...document.querySelectorAll('.top .bar, .bottom .bar')].map(b => ({
                h: b.getBoundingClientRect().height, clipped: b.scrollHeight > b.clientHeight + 1,
                kids: [...b.querySelectorAll('button:not([hidden])')].filter(k => getComputedStyle(k).display !== 'none' && k.checkVisibility())
                  .map(k => k.getBoundingClientRect()).every(r => r.height >= 36 && r.right <= innerWidth)}))""")
            self.assertEqual(len(got), 2)
            for bar in got:
                self.assertGreaterEqual(bar["h"], 44, "width %d: %s" % (width, got))
                self.assertFalse(bar["clipped"], "width %d: %s" % (width, got))
                self.assertTrue(bar["kids"], "width %d: a button is squashed or off screen" % width)
            line = p.evaluate("() => { const t = document.querySelector('#set-title');"
                              " return t.getBoundingClientRect().height <= parseFloat(getComputedStyle(t).lineHeight) + 1; }")
            self.assertTrue(line, "width %d: the set title wrapped" % width)

    def test_no_console_errors_with_csp(self):
        self.csp_clean()

    def csp_clean(self):
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

class GalleryPageTests(PageCase):
    def setUp(self):
        super().setUp()
        if not getattr(self, "srv", None):
            return
        image = self.dir / "case.svg"
        image.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1600">'
            '<rect width="1000" height="1600" fill="teal"/></svg>', encoding="utf-8")
        _, data = ask.load_set(self.dir)
        question = data["questions"][0]
        question.update(kind="choice", media=[
            {"src": "case.svg", "alt": "Example %d" % i, "label": "Example %d: " % i + "Long case label " * 8,
             "caption": "Comparison case %d" % i} for i in range(1, 4)
        ], one_pager=[{"type": "text", "text": "Extra context for the decision."}])
        ask.write_json_atomic(self.dir / "questions.json", data)

    def test_gallery_navigation_does_not_answer_or_change_question(self):
        p = self.open()
        gallery = p.get_by_role("region", name="Review cases")
        self.assertEqual(gallery.locator("img").count(), 1)
        self.assertIn("Case 1 of 3", gallery.inner_text())
        self.assertTrue(p.get_by_role("button", name="Previous case").is_disabled())
        p.get_by_role("button", name="Next case").click()
        self.assertEqual(gallery.locator("img").get_attribute("alt"), "Example 2")
        gallery.focus()
        p.keyboard.press("ArrowRight")
        self.assertIn("Case 3 of 3", gallery.inner_text())
        self.assertTrue(p.get_by_role("button", name="Next case").is_disabled())
        p.keyboard.press("ArrowRight")
        self.assertEqual(self.qid(), "arrow")
        p.keyboard.press("ArrowLeft")
        self.assertIn("Case 2 of 3", gallery.inner_text())
        p.get_by_label("Go to case").select_option("0")
        self.assertIn("Case 1 of 3", gallery.inner_text())
        self.assertEqual(self.answers(), {})
        self.assertEqual(p.locator("#ans input:checked").count(), 0)
        self.assertEqual(self.errors, [])

    def test_gallery_position_survives_question_navigation(self):
        p = self.open()
        p.get_by_label("Go to case").select_option("2")
        p.click("#btn-next")
        self.assertNotEqual(self.qid(), "arrow")
        p.click("#btn-back")
        self.assertEqual(self.qid(), "arrow")
        self.assertIn("Case 3 of 3", p.locator(".gallery-count").inner_text())

    def test_background_collapses_and_remembers_expansion(self):
        p = self.open()
        background = p.locator("details.onepager")
        self.assertFalse(background.evaluate("el => el.open"))
        background.locator("summary").focus()
        p.keyboard.press("Enter")
        self.assertTrue(background.evaluate("el => el.open"))
        p.click("#btn-next")
        p.click("#btn-back")
        self.assertTrue(p.locator("details.onepager").evaluate("el => el.open"))
        p.locator("details.onepager summary").click()
        self.assertFalse(p.locator("details.onepager").evaluate("el => el.open"))

    def test_gallery_is_bounded_and_accessible_on_desktop_and_phone(self):
        for width, height in ((1100, 900), (390, 844)):
            with self.subTest(width=width):
                self.page.set_viewport_size({"width": width, "height": height})
                p = self.open()
                p.wait_for_function("document.querySelector('.gallery img').naturalWidth > 0")
                image = p.locator(".gallery img").bounding_box()
                self.assertLessEqual(image["height"], height * .58 + 1)
                self.assertLessEqual(p.evaluate("document.documentElement.scrollWidth"), width)
                self.assertLess(p.locator("#ans").bounding_box()["y"], height * 1.6)
                self.axe("gallery at %d" % width)

    def test_explicit_stack_preserves_simultaneous_images(self):
        _, data = ask.load_set(self.dir)
        data["questions"][0]["media_layout"] = "stack"
        ask.write_json_atomic(self.dir / "questions.json", data)
        p = self.open()
        self.assertEqual(p.locator(".gallery").count(), 0)
        self.assertEqual(p.locator(".media img").count(), 3)

    def test_two_image_gallery_can_be_requested(self):
        _, data = ask.load_set(self.dir)
        data["questions"][0]["media"] = data["questions"][0]["media"][:2]
        data["questions"][0]["media_layout"] = "gallery"
        ask.write_json_atomic(self.dir / "questions.json", data)
        p = self.open()
        self.assertIn("Case 1 of 2", p.locator(".gallery-count").inner_text())

    def test_single_frame_keeps_full_size_access(self):
        _, data = ask.load_set(self.dir)
        data["questions"][0]["media"] = data["questions"][0]["media"][:1]
        ask.write_json_atomic(self.dir / "questions.json", data)
        p = self.open()
        self.assertEqual(p.locator(".gallery").count(), 0)
        self.assertEqual(p.locator(".media img").count(), 1)
        link = p.get_by_role("link", name="Open full-size image", exact=True)
        self.assertTrue(link.is_visible())
        self.assertEqual(link.get_attribute("target"), "_blank")


class ClickMediaTests(PageCase):
    """0.9.0: click a picture, or the Pick button under a clip or sound, to pick the option it stands for."""

    def with_arrow(self, **fields):
        _, data = ask.load_set(self.dir)
        q = next(x for x in data["questions"] if x["id"] == "arrow")
        q.update(fields)
        ask.write_json_atomic(self.dir / "questions.json", data)
        return self.open()

    def test_click_image_picks_its_side(self):
        p = self.with_arrow(media=[{"src": "swatch.png", "alt": "take A"}, {"src": "swatch.png", "alt": "take B"}])
        figs = p.locator("figure.pickable")
        self.assertEqual(figs.count(), 2)
        figs.nth(1).locator("img").click()
        self.wait_saved()
        self.assertEqual(self.answers()["arrow"]["choice"], "t5")  # sides.right
        self.assertIn("picked", figs.nth(1).get_attribute("class"))
        figs.nth(0).locator("img").click()
        self.wait_saved()
        self.assertEqual(self.answers()["arrow"]["choice"], "t2")

    def test_side_by_side_clip_gets_left_and_right_pick_buttons(self):
        p = self.open()
        self.assertEqual(p.locator(".side-picks .media-pick").count(), 2)
        p.click(".side-picks .media-pick >> nth=1")
        self.wait_saved()
        self.assertEqual(self.answers()["arrow"]["choice"], "t5")

    def test_media_option_field_and_answered_question(self):
        p = self.with_arrow(sides=None, media=[{"src": "tone.wav", "label": "A", "option": "tie"},
                                               {"src": "tone.wav", "label": "B", "option": "redo"}])
        p.click(".bench-row >> nth=1 >> .media-pick")
        self.wait_saved()
        self.assertEqual(self.answers()["arrow"]["choice"], "redo")
        p.reload()
        p.wait_for_selector("[data-q]")
        p.keyboard.press("o")
        p.click(".tasks a >> text=The arrow shot")
        p.click(".bench-row >> nth=0 >> .media-pick")  # an answered question reopens for editing
        self.wait_saved()
        self.assertEqual(self.answers()["arrow"]["choice"], "tie")

    def test_no_pick_targets_on_plain_media(self):
        p = self.open()
        p.keyboard.press("o")
        p.click(".tasks a >> text=%s" % next(q["title"] for q in ask.load_set(self.dir)[1]["questions"] if q["id"] == "pace"))
        p.wait_for_selector("[data-q=pace]")
        self.assertEqual(p.locator(".pickable, .media-pick").count(), 0)


class ListenPageTests(PageCase):
    """0.7.0: the listen bench, audio on options, the project label and the copy-continue-prompt button."""

    def setUp(self):
        super().setUp()
        if not getattr(self, "srv", None):
            return
        import math
        import struct
        import wave
        for name, hz in (("v1.wav", 330), ("v2.wav", 440), ("v3.wav", 550)):
            with wave.open(str(self.dir / name), "wb") as w:  # 4 s quiet tones: long enough to switch mid-clip
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(8000)
                w.writeframes(b"".join(struct.pack("<h", int(800 * math.sin(2 * math.pi * hz * i / 8000)))
                                       for i in range(8000 * 4)))
        _, data = ask.load_set(self.dir)
        data["project"] = {"name": "Test reel", "path": "/work/reel"}
        q = next(x for x in data["questions"] if x["id"] == "arrow")
        q.update(kind="choice", sides=None, media_layout="listen", look_for=["Which voice sounds tired at 2.0 s?"],
                 media=[{"src": "v1.wav", "label": "Voice one", "text": "We ride at dawn."},
                        {"src": "v2.wav", "label": "Voice two", "caption": "Slower read"},
                        {"src": "v3.wav", "label": "Voice three"}])
        q.pop("sides")
        q["options"][0]["media"] = [{"src": "v1.wav", "label": "Take 2 voice"}]
        ask.write_json_atomic(self.dir / "questions.json", data)

    def paused(self):
        return self.page.evaluate("() => [...document.querySelectorAll('.bench audio')].map(a => a.paused)")

    def test_bench_rows_and_one_clip_at_a_time(self):
        p = self.open()
        bench = p.get_by_role("region", name="Listen and compare")
        self.assertEqual(bench.locator(".bench-row").count(), 3)
        self.assertEqual(p.locator(".bench audio[controls]").count(), 0)
        self.assertIn("We ride at dawn.", bench.inner_text())
        self.assertIn("What to listen for", p.locator(".look h2").text_content())
        p.get_by_role("button", name="Play Voice one").click()
        p.wait_for_function("() => !document.querySelectorAll('.bench audio')[0].paused")
        p.get_by_role("button", name="Play Voice two").click()
        p.wait_for_function("() => !document.querySelectorAll('.bench audio')[1].paused")
        self.assertEqual(self.paused(), [True, False, True])
        self.assertEqual(p.get_by_role("button", name="Pause Voice two").get_attribute("aria-pressed"), "true")
        self.assertEqual(self.answers(), {})
        self.assertEqual(self.errors, [])

    def test_shift_number_and_ab_switch_keep_position(self):
        p = self.open()
        p.locator("h1").focus()
        p.keyboard.press("Shift+Digit1")
        p.wait_for_function("() => document.querySelectorAll('.bench audio')[0].currentTime > 1")
        self.assertEqual(p.locator("#ans input:checked").count(), 0)  # Shift+1 plays, it does not pick option 1
        p.keyboard.press("b")
        p.wait_for_function("() => !document.querySelectorAll('.bench audio')[1].paused")
        t = p.evaluate("() => document.querySelectorAll('.bench audio')[1].currentTime")
        self.assertGreater(t, 0.9)
        self.assertEqual(self.paused(), [True, False, True])
        p.wait_for_selector(".bench-row.playing[data-clip='1']")
        p.locator(".bench-seek").nth(2).fill("500")
        self.assertAlmostEqual(p.evaluate("() => document.querySelectorAll('.bench audio')[2].currentTime"), 2.0, delta=0.2)

    def test_option_sound_plays_without_picking(self):
        p = self.open()
        btn = p.get_by_role("button", name="Play the sample for this option: Take 2 voice")
        btn.click()
        p.wait_for_function("() => !document.querySelector('.opt-sound audio').paused")
        self.assertEqual(p.locator("#ans input:checked").count(), 0)
        p.get_by_role("button", name="Play Voice three").click()
        p.wait_for_function("() => document.querySelector('.opt-sound audio').paused")

    def test_compare_bench_hides_takes_until_pick(self):
        _, data = ask.load_set(self.dir)
        q = next(x for x in data["questions"] if x["id"] == "arrow")
        q.update(kind="compare", sides={"left": "t2", "right": "t5", "randomized": True},
                 media=[{"src": "v1.wav", "option": "t2"}, {"src": "v2.wav", "option": "t5"}])
        ask.write_json_atomic(self.dir / "questions.json", data)
        p = self.open()
        self.assertEqual(p.locator(".bench-label").all_inner_texts(), ["Left", "Right"])
        p.click(".opt[data-oid='t5']")
        self.wait_saved()
        self.assertEqual(p.locator(".bench-label").all_inner_texts(), ["Left (Take 2)", "Right (Take 5)"])

    def test_project_label_and_copy_prompt(self):
        self.ctx.grant_permissions(["clipboard-read", "clipboard-write"], origin=self.url.rstrip("/"))
        p = self.open()
        self.assertEqual(p.locator("#project-line").inner_text().lower(), "project: test reel")
        self.assertIn("Test reel · Pick the takes", p.locator(".context-line").inner_text())
        p.click(".opt[data-oid='t5']")
        self.wait_saved()
        more_menu(p)
        p.get_by_role("button", name="Copy continue prompt").click()
        p.wait_for_selector("#toast:not([hidden])")
        text = p.evaluate("() => navigator.clipboard.readText()")
        self.assertIn("Continue Test reel (project folder: /work/reel)", text)
        self.assertIn('read "%s"' % self.dir.resolve(), text)
        self.assertIn("1 answered", text)

    def test_copy_falls_back_without_clipboard_api(self):
        p = self.open()
        p.evaluate("() => { Object.defineProperty(navigator, 'clipboard', {value: {writeText: () => Promise.reject(new Error('no'))}});"
                   " window.__copied = null; document.execCommand = (c) => { window.__copied = document.activeElement.value; return true; }; }")
        more_menu(p)
        p.get_by_role("button", name="Copy continue prompt").click()
        p.wait_for_selector("#toast:not([hidden])")
        self.assertIn("Continue Test reel", p.evaluate("() => window.__copied"))
        self.assertNotIn("Could not", p.locator("#toast").inner_text())

    def test_dashboard_card_shows_project_and_copies(self):
        self.ctx.grant_permissions(["clipboard-read", "clipboard-write"], origin=self.url.rstrip("/"))
        ask.register_set(self.dir)
        p = self.page
        p.goto(self.url + "sessions")
        card = p.locator("article").first
        card.wait_for()
        self.assertIn("Test reel", card.locator(".project").text_content())
        card.get_by_role("button", name="Copy continue prompt").first.click()
        p.wait_for_selector("#toast:not([hidden])")
        self.assertIn("Continue Test reel", p.evaluate("() => navigator.clipboard.readText()"))

    def test_bench_fits_and_passes_axe_on_phone(self):
        for width, height in ((1100, 900), (390, 844)):
            with self.subTest(width=width):
                self.page.set_viewport_size({"width": width, "height": height})
                p = self.open()
                self.assertLessEqual(p.evaluate("document.documentElement.scrollWidth"), width)
                for box in (p.locator(".bench-play").nth(i).bounding_box() for i in range(3)):
                    self.assertGreaterEqual(box["height"], 44)
                self.axe("listen bench at %d" % width)


class StudyPageTests(PageCase):
    """Study mode (a quiz): no key before submit, the review after it, grading shown at the next poll, try again."""

    SET = FIX / "study"

    def pick(self, qid, label):
        p = self.page
        p.keyboard.press("o")
        p.click(".tasks a >> text=%s" % next(q["title"] for q in ask.load_set(self.dir)[1]["questions"] if q["id"] == qid))
        p.click(".opt:has-text('%s')" % label)
        self.wait_saved()

    def submit(self):
        p = self.page
        p.locator("h1").focus()  # keys do nothing while the answer box has focus
        p.keyboard.press("o")
        p.click("#btn-next")
        p.wait_for_selector("h1:has-text('Check your answers')")
        p.click("text=Submit my answers")
        p.wait_for_selector("h1:has-text('Your score')")

    def test_no_key_extras_guess_or_note_before_submit(self):
        p = self.open()
        html = p.content()
        for secret in ("Half of 8 is 8 divided by 2", "The sun heats sea water", "Splitting into fewer pieces"):
            self.assertNotIn(secret, html)
        self.assertEqual(p.locator("input[value=unsure], input[value=other], .guess, #note").count(), 0)
        values = p.eval_on_selector_all("input[type=radio]", "els => els.map(e => e.value)")
        self.assertEqual(sorted(values), ["o1", "o2", "o3", "o4"])  # real ids ("four") would hint at the answer
        self.assertIn("Fractions", p.locator(".caption").inner_text())
        self.assertEqual(p.locator("input[type=radio]:checked").count(), 0)
        self.assertEqual(self.errors, [])

    def test_submit_review_grade_and_try_again(self):
        p = self.open()
        self.pick("frac-half", "4 slices")
        self.pick("water-cond", "Water leaks through the glass")
        p.keyboard.press("o")
        p.click(".tasks a >> text=Explain the cycle")
        p.fill("#ans-text", "The sun evaporates sea water and it rains.")
        self.wait_saved()
        self.submit()
        self.assertIn("1 / 6", p.locator(".score-big").inner_text())
        self.assertIn("waiting for grading", p.locator(".notice-line").inner_text())
        self.assertEqual(p.locator(".topics tbody tr").count(), 2)
        self.assertEqual(p.locator(".topics .weak").count(), 2)
        wrong = p.locator(".rv[data-rq=water-cond]")
        self.assertIn("Not right", wrong.locator(".verdict").inner_text())
        self.assertIn("Water leaks through the glass", wrong.locator(".opt-rv.mine").inner_text())
        self.assertIn("Glass does not let water through", wrong.locator(".opt-rv.mine").inner_text())
        self.assertIn("cools, and its water vapor", wrong.locator(".opt-rv.right").inner_text())
        self.assertTrue(wrong.locator("details.others[open]").is_visible())
        self.assertIn("Waiting for grading", p.locator(".rv[data-rq=water-explain] .verdict").inner_text())
        right = p.locator(".rv[data-rq=frac-half]")
        self.assertIn("Your answer, and the right one", right.inner_text())
        p.click("text=Show only the ones to fix")
        self.assertEqual(p.locator(".rv[data-rq=frac-half]").count(), 0)
        p.click("text=Show every question")
        for scheme in ("light", "dark"):
            p.emulate_media(color_scheme=scheme)
            self.axe(scheme + " review")
        p.reload()  # the review survives a reload: the attempt is submitted on disk
        p.wait_for_selector("h1:has-text('Your score')")
        res = ask.load_results(self.dir)
        att = res["attempts"][-1]
        att["grades"] = {"water-explain": {"points": 1, "feedback": "Say where the vapor condenses."}}
        att["score"] = ask.study_score(ask.load_set(self.dir)[1], att["answers"], att["grades"])
        ask.write_json_atomic(self.dir / "results.json", res)
        p.evaluate("() => window.dispatchEvent(new Event('focus'))")
        p.wait_for_selector(".rv[data-rq=water-explain] .verdict:has-text('Part right')")
        self.assertIn("Say where the vapor condenses.", p.locator(".rv[data-rq=water-explain]").inner_text())
        self.assertIn("2 / 6", p.locator(".score-big").inner_text())
        p.click("text=Try again")
        p.wait_for_selector("[data-q]")
        self.assertEqual(p.locator("input[type=radio]:checked").count(), 0)
        self.assertEqual([a["n"] for a in ask.load_results(self.dir)["attempts"]], [1, 2])
        self.assertEqual(self.answers(), {})
        self.assertEqual(self.errors, [])

    def test_figure_draws_under_the_csp(self):
        ctx = _browser.new_context()  # the real CSP, not bypassed: figures are data URLs the policy allows
        page = ctx.new_page()
        page.goto(self.url)
        page.wait_for_selector("[data-q]")
        page.keyboard.press("o")
        page.click(".tasks a >> text=The bigger fraction")
        page.wait_for_selector("[data-q] .media img")
        ok = page.evaluate("() => { const i = document.querySelector('[data-q] .media img'); "
                           "return i.complete && i.naturalWidth > 0 && i.alt.length > 0; }")
        ctx.close()
        self.assertTrue(ok)

    def test_review_fits_a_phone(self):
        self.ctx.close()
        self.ctx = _browser.new_context(bypass_csp=True, viewport={"width": 375, "height": 740}, is_mobile=True)
        self.page = self.ctx.new_page()
        p = self.open()
        self.pick("frac-compare", "1/8")
        self.submit()
        wide = p.evaluate("() => document.documentElement.scrollWidth - window.innerWidth")
        self.assertLessEqual(wide, 0)
        self.assertTrue(p.locator(".rv[data-rq=frac-compare] .opt-rv.right").is_visible())

    def test_no_console_errors_with_csp(self):
        FixturePageTests.csp_clean(self)


if __name__ == "__main__":
    unittest.main(verbosity=1)
