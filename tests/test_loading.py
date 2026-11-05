"""Mobile loading (v5, Nov 2026): what the page downloads, and when.

Every image on the page sits below the fold, so none of them loads with
the page; each comes in as the visitor scrolls near it. The quote
carousel loads all its slides together, so no slide ever shows a blank
card. The hero loop (1.2MB) loads only when it will play: never under
reduced motion, Data Saver, or a 2G connection.
"""

from __future__ import annotations

import unittest

from helpers import BrowserTestCase


LOADED = """(sel) => [...document.querySelectorAll(sel)].map(i => ({
    src: i.getAttribute('src'), done: i.complete && i.naturalWidth > 0,
    natural: [i.naturalWidth, i.naturalHeight], attrs: [+i.getAttribute('width'), +i.getAttribute('height')]
}))"""


class RequestLog(BrowserTestCase):
    """Records every URL the page asks for, from the first request."""

    def open_page(self, suffix: str = "") -> None:
        if not hasattr(self, "requested"):
            self.requested: list[str] = []
            self.page.on("request", lambda r: self.requested.append(r.url))
        super().open_page(suffix)

    def asked_for(self, part: str) -> list[str]:
        return [u for u in self.requested if part in u]


class LazyImagesTest(RequestLog):
    def setUp(self) -> None:
        super().setUp()
        self.page.add_style_tag(content="html{scroll-behavior:auto!important}")

    def test_no_image_loads_with_the_page(self) -> None:
        self.page.wait_for_timeout(500)
        self.assertEqual([], self.asked_for("/assets/logos/"))
        self.assertEqual([], self.asked_for("/assets/quote-"))

    def test_images_arrive_as_the_visitor_scrolls_near_them(self) -> None:
        self.page.evaluate("document.getElementById('writing').scrollIntoView({block:'center'})")
        self.page.wait_for_function(
            "[...document.querySelectorAll('#writing .pub-logo')].filter(i => getComputedStyle(i).display !== 'none').every(i => i.complete && i.naturalWidth)",
            timeout=5000,
        )

    def test_the_carousel_loads_every_slide_before_showing_one(self) -> None:
        # Within a screen of the viewport, all six quotes and every
        # caption logo load, including the slides still off stage.
        self.page.evaluate(
            "window.scrollTo(0, document.getElementById('quoteCarousel').getBoundingClientRect().top + scrollY - 1.6 * innerHeight)"
        )
        self.page.wait_for_function(
            "[...document.querySelectorAll('#quoteCarousel img')].every(i => i.complete && i.naturalWidth)",
            timeout=5000,
        )
        self.assertEqual(6, len(set(self.asked_for("/assets/quote-"))))

    def test_quote_screenshots_declare_their_real_size(self) -> None:
        self.page.evaluate("document.getElementById('quoteCarousel').scrollIntoView({block:'center'})")
        self.page.wait_for_function(
            "[...document.querySelectorAll('#quoteCarousel .slide > a > img')].every(i => i.complete && i.naturalWidth)",
            timeout=5000,
        )
        for img in self.page.evaluate(LOADED, "#quoteCarousel .slide > a > img"):
            with self.subTest(src=img["src"]):
                self.assertTrue(img["src"].endswith(".webp"))
                self.assertEqual(img["natural"], img["attrs"])

    def test_the_carousel_keeps_its_height_while_quotes_load(self) -> None:
        # The declared sizes reserve each screenshot's box, so nothing
        # below the carousel moves when the files arrive.
        height = "Math.round(document.querySelector('#quoteCarousel .carousel-track').getBoundingClientRect().height)"
        before = self.page.evaluate(height)
        self.assertFalse(self.page.evaluate("document.querySelector('#quoteCarousel .slide > a > img').complete"))
        self.page.evaluate("document.getElementById('quoteCarousel').scrollIntoView({block:'center'})")
        self.page.wait_for_function(
            "[...document.querySelectorAll('#quoteCarousel .slide > a > img')].every(i => i.complete && i.naturalWidth)",
            timeout=5000,
        )
        self.assertAlmostEqual(before, self.page.evaluate(height), delta=1)


class LazyImagesPhoneTest(LazyImagesTest):
    viewport = {"width": 390, "height": 844}


class HeroVideoTest(RequestLog):
    def test_loads_when_it_will_play(self) -> None:
        # Asserts the download, not playback: the Chromium that CI installs
        # has no H.264 decoder, so play() may be refused there.
        self.page.wait_for_timeout(1200)
        self.assertTrue(self.asked_for("data-hero-loop.mp4"))


class HeroVideoReducedMotionTest(RequestLog):
    reduced_motion = "reduce"

    def test_never_downloads_under_reduced_motion(self) -> None:
        self.page.wait_for_timeout(1200)
        self.assertTrue(self.page.evaluate("document.getElementById('heroVideo').paused"))
        self.assertEqual([], self.asked_for("data-hero-loop.mp4"))


class HeroVideoSaveDataTest(RequestLog):
    def open_page(self, suffix: str = "") -> None:
        # Chrome's Data Saver, as a page sees it.
        self.context.add_init_script(
            "Object.defineProperty(navigator, 'connection', { get: () => ({ saveData: true, effectiveType: '4g' }) })"
        )
        super().open_page(suffix)

    def test_keeps_the_still_and_downloads_nothing(self) -> None:
        self.page.wait_for_timeout(1200)
        state = self.page.evaluate(
            "({ paused: document.getElementById('heroVideo').paused, poster: document.getElementById('heroVideo').poster.endsWith('data-hero.webp') })"
        )
        self.assertEqual({"paused": True, "poster": True}, state)
        self.assertEqual([], self.asked_for("data-hero-loop.mp4"))


class HeroVideoSlowConnectionTest(HeroVideoSaveDataTest):
    def open_page(self, suffix: str = "") -> None:
        self.context.add_init_script(
            "Object.defineProperty(navigator, 'connection', { get: () => ({ saveData: false, effectiveType: 'slow-2g' }) })"
        )
        RequestLog.open_page(self, suffix)


if __name__ == "__main__":
    unittest.main(verbosity=2)
