"""Visual checks for the askwright pages (Playwright with installed Chrome or Edge). Development only.

Run from the repository root: python tests/test_visual.py
Serves the fixture set with a long title and a project, opens the question page, the dashboard and the project
page at desktop and phone widths, saves a screenshot of each (tests/screenshots/, git-ignored; ASKW_SHOTS=<dir>
to put them elsewhere), and asserts the top bar stays one tidy row: no wrapped title or counter, nothing past
the right edge, no horizontal page scroll, every chip on one baseline. Skips when Playwright or a browser is missing.
"""

import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "askwright" / "scripts"))
import ask  # noqa: E402

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None

FIX = ROOT / "tests" / "fixtures"
SHOTS = Path(os.environ.get("ASKW_SHOTS") or ROOT / "tests" / "screenshots")
WIDTHS = {"desktop": (1280, 860), "laptop": (1000, 760), "phone": (390, 844), "small": (340, 700)}
LONG = "Director 0.14.0 wave limit and dual switch playtest review for the Workshop build"
_pw = _browser = _why = None
_home = _env = None


def setUpModule():
    global _pw, _browser, _why, _home, _env
    _home = tempfile.TemporaryDirectory(prefix="askw-visual-")
    _env = mock.patch.dict(os.environ, {"ASKWRIGHT_HOME": _home.name})
    _env.start()
    if sync_playwright is None:
        _why = "playwright is not installed (pip install playwright); visual tests skipped"
        return
    _pw = sync_playwright().start()
    for channel in ("chrome", "msedge", None):
        try:
            _browser = _pw.chromium.launch(channel=channel) if channel else _pw.chromium.launch()
            return
        except Exception:  # noqa: BLE001 - try the next browser
            continue
    _why = "no Chromium browser available; visual tests skipped"


def tearDownModule():
    if _browser:
        _browser.close()
    if _pw:
        _pw.stop()
    _env.stop()
    _home.cleanup()


# The top bar: one row on desktop; title and counters never wrap; nothing overflows; chips share a baseline.
TOPBAR = """() => {
  const bar = document.querySelector('.top .bar');
  const r = bar.getBoundingClientRect();
  const one = (el) => !el || el.hidden || getComputedStyle(el).display === 'none' ||
    el.getBoundingClientRect().height <= parseFloat(getComputedStyle(el).lineHeight || 20) * 1.15 + 2;
  const chips = [...document.querySelectorAll('#top-links > .chip, #top-links > .more:not([hidden]) > summary')]
    .filter(el => !el.hidden && getComputedStyle(el).display !== 'none').map(el => el.getBoundingClientRect());
  const pills = [...document.querySelectorAll('#progress .pill')].filter(el => getComputedStyle(el).display !== 'none')
    .map(el => el.getBoundingClientRect());
  const title = document.querySelector('#set-title');
  return {
    height: r.height,
    titleOneLine: title.scrollHeight <= title.clientHeight + 1 && one(title),
    titleTruncated: title.scrollWidth > title.clientWidth,
    titleHover: title.title,
    pillsOneLine: pills.every(p => Math.abs(p.top - pills[0].top) < 1 && p.height < 34),
    chipTops: [...new Set(chips.map(c => Math.round(c.top)))],
    chipHeights: [...new Set(chips.map(c => Math.round(c.height)))],
    rightmost: Math.max(...chips.map(c => c.right), ...pills.map(p => p.right)),
    vw: document.documentElement.clientWidth,
    pageScrollX: document.documentElement.scrollWidth > document.documentElement.clientWidth,
  };
}"""

# Dark mode: the body background is dark and every visible text element in `sel` keeps 4.5:1 contrast (WCAG AA).
CONTRAST = r"""(sel) => {
  const rgb = c => (c.match(/[\d.]+/g) || []).map(Number);
  const lum = ([r, g, b]) => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); };
  const bgOf = el => { for (; el; el = el.parentElement) { const c = rgb(getComputedStyle(el).backgroundColor);
    if (c.length === 3 || (c.length === 4 && c[3] > 0.5)) return c.slice(0, 3); }
    return rgb(getComputedStyle(document.documentElement).backgroundColor).slice(0, 3); };
  const low = [];
  for (const el of document.querySelectorAll(sel)) {
    if (!el.getClientRects().length || !el.textContent.trim()) continue;
    const a = lum(rgb(getComputedStyle(el).color).slice(0, 3)), b = lum(bgOf(el));
    const r = (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
    if (r < 4.5) low.push((el.id || el.className || el.tagName) + " " + r.toFixed(2));
  }
  return {bodyLum: lum(bgOf(document.body)), low};
}"""


class VisualCase(unittest.TestCase):
    def setUp(self):
        if _why:
            self.skipTest(_why)
        d, data = ask.load_set(FIX / "good")
        self.dir = Path(tempfile.mkdtemp(prefix="askw-visual-set-"))
        data["media_roots"] = [str(r) for r in ask.media_roots(d, data)]
        data["title"] = LONG
        data["project"] = {"name": "Madness Workshop", "path": str(self.dir)}
        (self.dir / "questions.json").write_text(json.dumps(data), encoding="utf-8")
        ask.ensure_project("Madness Workshop", description="Mod levels and Director tuning for the Workshop.",
                           repos=["https://github.com/example/workshop"], dirs=[str(self.dir)])
        ask.register_set(self.dir)
        self.srv = ask.make_server(self.dir, port=0)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.url = "http://127.0.0.1:%d/" % self.srv.server_address[1]
        SHOTS.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        self.srv.shutdown()
        self.srv.server_close()
        shutil.rmtree(self.dir, ignore_errors=True)

    def page(self, name, scheme="light"):
        w, h = WIDTHS[name]
        ctx = _browser.new_context(viewport={"width": w, "height": h}, color_scheme=scheme)
        self.addCleanup(ctx.close)
        p = ctx.new_page()
        p.set_default_timeout(10000)
        errs = []
        p.on("pageerror", lambda e: errs.append(str(e)))
        p.on("console", lambda m: m.type == "error" and errs.append(m.text))
        self.addCleanup(lambda: self.assertEqual(errs, [], "%s: console errors" % name))
        return p

    def shot(self, p, label, clip_top=False):
        path = SHOTS / (label + ".png")
        if clip_top:
            p.locator("header.top").screenshot(path=str(path))
        else:
            p.screenshot(path=str(path), full_page=True)
        return path

    def test_top_bar_one_clean_row(self):
        for name in WIDTHS:
            with self.subTest(width=name):
                p = self.page(name)
                p.goto(self.url)
                p.wait_for_selector("[data-q]")
                p.click(".opt >> nth=0")  # one answer brings the Show answered chip
                p.wait_for_selector("#save-status:has-text('Saved')")
                got = p.evaluate(TOPBAR)
                self.shot(p, "topbar-" + name, clip_top=True)
                self.shot(p, "question-" + name)
                self.assertTrue(got["titleOneLine"], got)
                self.assertEqual(got["titleHover"], LONG)
                self.assertTrue(got["pillsOneLine"], got)
                self.assertEqual(len(got["chipTops"]), 1, "chips on different rows or baselines: %s" % got)
                self.assertEqual(len(got["chipHeights"]), 1, "chips of different heights: %s" % got)
                self.assertLessEqual(got["rightmost"], got["vw"], got)
                self.assertFalse(got["pageScrollX"], got)
                if name in ("desktop", "laptop"):
                    self.assertLess(got["height"], 70, "the top bar is more than one row: %s" % got)

    def test_more_menu_holds_secondary_links_on_phone(self):
        p = self.page("phone")
        p.goto(self.url)
        p.wait_for_selector("[data-q]")
        self.assertFalse(p.locator("#btn-copy").is_visible())
        p.click("#more > summary")
        self.assertTrue(p.locator("#btn-copy").is_visible())
        self.assertTrue(p.get_by_role("link", name="All sessions").is_visible())
        self.shot(p, "more-menu-phone")
        box = p.locator("#more-menu").bounding_box()
        self.assertGreaterEqual(box["x"], 0)
        self.assertLessEqual(box["x"] + box["width"], WIDTHS["phone"][0])

    def test_dashboard_and_project_pages(self):
        for name in ("desktop", "phone"):
            with self.subTest(width=name):
                p = self.page(name)
                p.goto(self.url + "sessions")
                p.wait_for_selector("#sessions tbody")
                self.assertIn("Madness Workshop", p.locator("#projects").inner_text())
                self.assertTrue(p.locator("#sessions td.updated time").first.get_attribute("title"))
                self.shot(p, "index-" + name)
                p.locator("#projects a").first.click()
                p.wait_for_selector(".set-card")
                self.assertEqual(p.locator("h1").inner_text(), "Madness Workshop")
                self.assertIn("github.com/example/workshop", p.locator("#places").inner_text())
                self.assertEqual(p.locator(".set-card h3").inner_text(), LONG)
                self.assertTrue(p.locator("#facts time").first.get_attribute("title"))
                self.assertFalse(p.evaluate("() => document.documentElement.scrollWidth > innerWidth"))
                self.shot(p, "project-" + name)

    def test_project_link_from_question_page(self):
        p = self.page("desktop")
        p.goto(self.url)
        p.wait_for_selector("[data-q]")
        p.click("#project-line")
        p.wait_for_selector(".set-card")
        self.assertEqual(p.locator("h1").inner_text(), "Madness Workshop")

    def test_dark_mode_pages_are_dark_and_readable(self):
        for name in ("desktop", "phone"):
            with self.subTest(width=name):
                p = self.page(name, scheme="dark")
                p.goto(self.url)
                p.wait_for_selector("[data-q]")
                self.assert_dark(p, "header.top *, [data-q] h2, .opt")
                self.shot(p, "question-dark-" + name)
                p.goto(self.url + "sessions")
                p.wait_for_selector("#sessions tbody")
                self.assert_dark(p, "h1, #sessions td, #sessions th, #projects a")
                self.shot(p, "index-dark-" + name)
                p.locator("#projects a").first.click()
                p.wait_for_selector(".set-card")
                self.assert_dark(p, "h1, .set-card h3, #facts, #places a")
                self.shot(p, "project-dark-" + name)

    def assert_dark(self, p, selector):
        got = p.evaluate(CONTRAST, selector)
        self.assertLess(got["bodyLum"], 0.2, "body is not dark: %s" % got)
        self.assertEqual(got["low"], [], "text below 4.5:1 contrast: %s" % got["low"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
