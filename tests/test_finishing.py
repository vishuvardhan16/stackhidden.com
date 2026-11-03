"""Finishing touches (v5, Nov 2026): skip link, theme colour, home-screen
icon, and the 404 page.

The 404 tests run against a small local server that behaves like GitHub
Pages for a missing address: it answers with 404.html and status 404, at
any depth. The static half (robots.txt, sitemap.xml, absolute URLs in
404.html, matching colours) is in test_static.py.
"""

from __future__ import annotations

import functools
import threading
import unittest
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from helpers import ROOT, BrowserTestCase


THEME_COLOR = {"light": "#fdfefe", "dark": "#151923"}
META = "[...document.querySelectorAll('meta[name=\"theme-color\"]')].map(m => m.content)"


class SkipLinkTest(BrowserTestCase):
    def test_hidden_until_the_first_tab_then_moves_focus_to_main(self) -> None:
        self.assertLessEqual(
            self.page.evaluate("document.querySelector('.skip-link').getBoundingClientRect().bottom"), 0
        )
        self.page.keyboard.press("Tab")
        state = self.page.evaluate(
            """() => { const a = document.activeElement, r = a.getBoundingClientRect();
                       return { cls: a.className, text: a.textContent, top: r.top, onTop: document.elementFromPoint(r.left + 5, r.top + 5) === a }; }"""
        )
        self.assertEqual("skip-link", state["cls"])
        self.assertEqual("Skip to content", state["text"])
        self.assertGreaterEqual(state["top"], 0)
        self.assertTrue(state["onTop"], "the skip link is covered by the header")
        self.page.keyboard.press("Enter")
        self.page.wait_for_timeout(100)
        self.assertEqual("top", self.page.evaluate("document.activeElement.id"))
        # The next Tab lands inside main, past the header's eleven stops.
        self.page.keyboard.press("Tab")
        self.assertTrue(self.page.evaluate("!!document.activeElement.closest('main')"))


class ThemeColorTest(BrowserTestCase):
    color_scheme = "dark"

    def test_both_tags_follow_the_theme_showing(self) -> None:
        self.assertEqual([THEME_COLOR["dark"]] * 2, self.page.evaluate(META))
        self.page.click("#theme-toggle")
        self.assertEqual([THEME_COLOR["light"]] * 2, self.page.evaluate(META))
        # Any path that changes the theme, not only the toggle.
        self.page.evaluate("document.documentElement.setAttribute('data-theme', 'dark')")
        self.page.wait_for_timeout(50)
        self.assertEqual([THEME_COLOR["dark"]] * 2, self.page.evaluate(META))


class TouchIconTest(BrowserTestCase):
    def test_home_screen_icon_loads_at_180px(self) -> None:
        size = self.page.evaluate(
            """() => new Promise(done => {
                const img = new Image();
                img.onload = () => done([img.naturalWidth, img.naturalHeight]);
                img.onerror = () => done(null);
                img.src = document.querySelector('link[rel="apple-touch-icon"]').href;
            })"""
        )
        self.assertEqual([180, 180], size)


class PagesLikeHandler(SimpleHTTPRequestHandler):
    """Serves the repository; a missing file gets 404.html with status 404."""

    def send_error(self, code, message=None, explain=None):  # noqa: D401
        if code != 404:
            return super().send_error(code, message, explain)
        body = (ROOT / "404.html").read_bytes()
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def log_message(self, *args) -> None:
        pass


class NotFoundPageTest(BrowserTestCase):
    path = "/writing/an-old-post"

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        handler = functools.partial(PagesLikeHandler, directory=str(ROOT))
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.origin = f"http://127.0.0.1:{cls.server.server_address[1]}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        super().tearDownClass()

    def open_page(self, suffix: str = "") -> None:
        self.visit(self.path)

    def visit(self, path: str) -> int:
        if not hasattr(self, "visited"):
            # Chrome logs a console error for the document's own 404,
            # which is this page working. Note where each error came from
            # so tearDown can drop exactly those, and no other.
            self.visited: list[str] = []
            self.console: list[tuple[str, str]] = []
            self.page.on("console", lambda m: self.console.append((m.text, m.location.get("url", "")))
                         if m.type == "error" else None)
        response = self.page.goto(self.origin + path, wait_until="load")
        self.visited.append(response.url)
        self.page.wait_for_timeout(100)
        return response.status

    def tearDown(self) -> None:
        for text, url in self.console:
            if url in self.visited and "status of 404" in text and text in self.page_errors:
                self.page_errors.remove(text)
        super().tearDown()

    def query_line(self) -> str:
        return self.page.text_content(".query code")

    def test_a_missing_address_gets_the_page_with_status_404(self) -> None:
        self.assertEqual(404, self.visit("/a/b/c/deep"))
        self.assertEqual("Page not found | stackhidden", self.page.title())
        self.assertEqual("SELECT * FROM pages WHERE path = '/a/b/c/deep';", self.query_line())
        self.assertEqual("0 rows. Did you mean /?", self.page.text_content(".status"))

    def test_every_link_and_icon_works_from_any_depth(self) -> None:
        links = self.page.evaluate("[...document.querySelectorAll('a')].map(a => a.href)")
        self.assertEqual(f"{self.origin}/", links[0])
        for href in links:
            with self.subTest(href=href):
                self.assertTrue(href.startswith(f"{self.origin}/"), href)
        statuses = self.page.evaluate(
            """async () => Promise.all(['link[rel="icon"]', 'link[rel="apple-touch-icon"]'].map(
                s => fetch(document.querySelector(s).href).then(r => r.status)))"""
        )
        self.assertEqual([200, 200], statuses)

    def test_quotes_in_the_path_are_doubled_as_in_sql(self) -> None:
        self.visit("/it's")
        self.assertEqual("SELECT * FROM pages WHERE path = '/it''s';", self.query_line())

    def test_markup_in_the_path_stays_text(self) -> None:
        self.visit("/%3Cimg%20src=x%20onerror=window.__pwned=1%3E")
        self.assertIn("<img src=x onerror=window.__pwned=1>", self.query_line())
        self.assertEqual(
            {"imgs": 0, "pwned": False},
            self.page.evaluate("({ imgs: document.querySelectorAll('main img').length, pwned: !!window.__pwned })"),
        )

    def test_a_long_path_is_cut_at_80_characters(self) -> None:
        self.visit("/" + "x" * 200)
        quoted = self.query_line().split(" = ", 1)[1].rstrip(";")
        self.assertEqual(80 + 2, len(quoted))
        self.assertTrue(quoted.endswith("…'"))

    def test_follows_the_theme_the_visitor_chose(self) -> None:
        for scheme in ("light", "dark"):
            with self.subTest(scheme=scheme):
                self.page.emulate_media(color_scheme=scheme)
                self.visit(self.path)
                self.assertEqual(scheme, self.page.evaluate("document.documentElement.dataset.theme"))
                self.assertEqual([THEME_COLOR[scheme]] * 2, self.page.evaluate(META))
        # A choice saved on the home page wins over the OS setting.
        self.page.evaluate("localStorage.setItem('theme', 'light')")
        self.visit(self.path)
        self.assertEqual("light", self.page.evaluate("document.documentElement.dataset.theme"))
        self.assertEqual(
            "rgb(255, 255, 255)",
            self.page.evaluate("getComputedStyle(document.querySelector('nav a')).backgroundColor"),
        )

    def test_fits_a_phone(self) -> None:
        self.page.set_viewport_size({"width": 360, "height": 740})
        self.visit("/" + "a-very-long-segment-" * 4)
        self.assertLessEqual(self.page.evaluate("document.documentElement.scrollWidth"), 360)


if __name__ == "__main__":
    unittest.main(verbosity=2)
