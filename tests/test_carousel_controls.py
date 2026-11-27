"""Carousel controls and slide motion, for both carousels.

Nov 26, 2026, at the owner's request: with 46 quotes, Featured In drew
46 dots in a row. On a phone the row ran past the panel and pushed both
arrows out of reach, and on a laptop it read as clutter. Both carousels
now show their position as a counter ("12 / 46") and a thin meter, with
two arrow buttons. The same change fixed three bugs:

- Slide bleed. A slide that had just left sat at the right, and on the
  next move it slid all the way back across the stage, behind the new
  slide, to its waiting place on the left. Mid-move, three slides
  showed at once, cut off at both edges.
- Writing cards lost their padding. The carousel's 6px slide padding
  beat the card's 24px, so the logo sat against the card's border.
- Without JavaScript neither carousel showed anything: every slide
  waited off stage.
"""

from __future__ import annotations

import unittest

from helpers import BrowserTestCase, chromium_launch_kwargs, page_url


CAROUSELS = [
    # id, prev, next, slide count, item name
    ("quoteCarousel", "quotePrev", "quoteNext", 46, "Quote"),
    ("writingCarousel", "writingPrev", "writingNext", 7, "Article"),
]

# Slides that show any part of themselves inside the stage right now.
VISIBLE_SLIDES = """(id) => {
    const stage = document.querySelector('#' + id + ' .carousel-stage').getBoundingClientRect();
    return [...document.querySelectorAll('#' + id + ' .slide')].filter(s => {
        const r = s.getBoundingClientRect();
        return getComputedStyle(s).visibility !== 'hidden'
            && r.right > stage.left + 1 && r.left < stage.right - 1;
    }).length;
}"""

ACTIVE = "(id) => [...document.querySelectorAll('#' + id + ' .slide')].findIndex(s => s.classList.contains('on'))"


class ControlsTest(BrowserTestCase):
    reduced_motion = "reduce"

    def setUp(self) -> None:
        super().setUp()
        self.page.add_style_tag(content="html{scroll-behavior:auto!important}")

    def count(self, carousel: str) -> dict[str, str]:
        return self.page.evaluate(
            """(id) => {
                const c = document.querySelector('#' + id + ' .carousel-count');
                // What a sighted visitor sees: everything but the
                // screen-reader words ("Quote", "of").
                return { shown: [...c.childNodes].filter(n => !(n.classList && n.classList.contains('sr-only'))).map(n => n.textContent).join('').replace(/\\s+/g, ' ').trim(),
                         spoken: c.textContent.replace(/\\s+/g, ' ').replace(' / ', ' ').trim(),
                         live: c.getAttribute('aria-live') };
            }""",
            carousel,
        )

    def meter(self, carousel: str) -> float:
        return self.page.evaluate(
            """(id) => {
                const f = document.querySelector('#' + id + ' .carousel-meter-fill');
                const t = document.querySelector('#' + id + ' .carousel-meter');
                return f.getBoundingClientRect().width / t.getBoundingClientRect().width;
            }""",
            carousel,
        )

    def test_no_dots_and_the_counter_shows_position_and_total(self) -> None:
        for cid, prev, nxt, total, item in CAROUSELS:
            with self.subTest(carousel=cid):
                self.assertEqual(0, self.page.locator(f"#{cid} .carousel-dot").count())
                self.assertEqual({"shown": f"1 / {total}", "spoken": f"{item} 1 of {total}", "live": "off"}, self.count(cid))
                self.page.click(f"#{nxt}")
                self.assertEqual(f"2 / {total}", self.count(cid)["shown"])
                self.assertEqual(f"{item} 2 of {total}", self.count(cid)["spoken"])
                # Back past the first slide wraps to the last.
                self.page.click(f"#{prev}")
                self.page.click(f"#{prev}")
                self.assertEqual(f"{total} / {total}", self.count(cid)["shown"])
                self.assertEqual(total - 1, self.page.evaluate(ACTIVE, cid))

    def test_the_meter_fills_to_the_position(self) -> None:
        for cid, prev, nxt, total, _ in CAROUSELS:
            with self.subTest(carousel=cid):
                self.assertAlmostEqual(1 / total, self.meter(cid), delta=0.01)
                for _ in range(3):
                    self.page.click(f"#{nxt}")
                self.assertAlmostEqual(4 / total, self.meter(cid), delta=0.01)
                self.page.evaluate(f"document.getElementById('{cid}').goToSlide({total - 1})")
                self.assertAlmostEqual(1.0, self.meter(cid), delta=0.01)

    def test_position_is_announced_only_when_the_visitor_moves_it(self) -> None:
        # Auto-advance stays quiet (aria-live off); a press of an arrow
        # makes the next change polite, so a screen reader hears where
        # the visitor landed.
        for cid, prev, nxt, total, item in CAROUSELS:
            with self.subTest(carousel=cid):
                self.assertEqual("off", self.count(cid)["live"])
                self.page.click(f"#{nxt}")
                self.assertEqual("polite", self.count(cid)["live"])

    def test_arrows_are_44px_targets_with_centred_chevrons(self) -> None:
        for cid, prev, nxt, _, _ in CAROUSELS:
            for bid in (prev, nxt):
                with self.subTest(button=bid):
                    box = self.page.evaluate(
                        """(id) => {
                            const b = document.getElementById(id).getBoundingClientRect();
                            const i = document.querySelector('#' + id + ' svg').getBoundingClientRect();
                            return { w: b.width, h: b.height,
                                     dx: (i.left + i.width / 2) - (b.left + b.width / 2),
                                     dy: (i.top + i.height / 2) - (b.top + b.height / 2) };
                        }""",
                        bid,
                    )
                    self.assertGreaterEqual(box["w"], 44)
                    self.assertGreaterEqual(box["h"], 44)
                    self.assertLessEqual(abs(box["dx"]), 1)
                    self.assertLessEqual(abs(box["dy"]), 1)

    def test_writing_slides_keep_the_card_padding(self) -> None:
        pads = self.page.evaluate(
            """() => ({
                slide: getComputedStyle(document.querySelector('#writingCarousel .slide')).paddingLeft,
                card: getComputedStyle(document.querySelector('#writing .cards .card')).paddingLeft
            })"""
        )
        self.assertEqual(pads["card"], pads["slide"])
        self.assertEqual("24px", pads["slide"])


class ControlsFitTest(BrowserTestCase):
    """The controls stay on one row, inside the carousel, at any width."""

    reduced_motion = "reduce"

    def test_controls_fit_at_every_width(self) -> None:
        for width in (320, 390, 768, 1288):
            self.page.set_viewport_size({"width": width, "height": 900})
            for cid, prev, nxt, _, _ in CAROUSELS:
                with self.subTest(width=width, carousel=cid):
                    fit = self.page.evaluate(
                        """([cid, prev, next]) => {
                            const c = document.getElementById(cid).getBoundingClientRect();
                            const row = document.querySelector('#' + cid + ' .carousel-controls');
                            const inside = id => {
                                const b = document.getElementById(id).getBoundingClientRect();
                                return b.left >= c.left && b.right <= c.right && b.width > 0;
                            };
                            return { overflow: row.scrollWidth - row.clientWidth,
                                     height: row.getBoundingClientRect().height,
                                     prev: inside(prev), next: inside(next) };
                        }""",
                        [cid, prev, nxt],
                    )
                    self.assertLessEqual(fit["overflow"], 0)
                    self.assertLessEqual(fit["height"], 64)
                    self.assertTrue(fit["prev"])
                    self.assertTrue(fit["next"])


class NoBleedTest(BrowserTestCase):
    """With motion on, at most two slides (the one arriving and the one
    leaving) ever show during a move."""

    def test_only_two_slides_show_mid_move(self) -> None:
        self.page.add_style_tag(content="html{scroll-behavior:auto!important}")
        for cid, prev, nxt, _, _ in CAROUSELS:
            with self.subTest(carousel=cid):
                self.page.evaluate(f"document.getElementById('{cid}').scrollIntoView({{block:'center'}})")
                self.page.click(f"#{nxt}")
                self.page.wait_for_timeout(900)
                self.page.click(f"#{nxt}")
                seen = []
                for _ in range(14):
                    seen.append(self.page.evaluate(VISIBLE_SLIDES, cid))
                    self.page.wait_for_timeout(50)
                self.assertLessEqual(max(seen), 2, seen)
                # And once the move is over, only the new slide shows.
                self.page.wait_for_timeout(700)
                self.assertEqual(1, self.page.evaluate(VISIBLE_SLIDES, cid))


class NoJavaScriptTest(unittest.TestCase):
    """Without JavaScript every slide is on the page, one after another,
    and the controls (which need JavaScript) are not shown."""

    def test_every_slide_is_readable_without_javascript(self) -> None:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(**chromium_launch_kwargs(), args=["--no-sandbox"])
            try:
                page = browser.new_context(java_script_enabled=False, viewport={"width": 1288, "height": 900}).new_page()
                page.goto(page_url())
                for cid, _, _, total, _ in CAROUSELS:
                    with self.subTest(carousel=cid):
                        state = page.evaluate(
                            """(id) => {
                                const c = document.getElementById(id);
                                const stage = c.querySelector('.carousel-stage').getBoundingClientRect();
                                const slides = [...c.querySelectorAll('.slide')].map(s => s.getBoundingClientRect());
                                return {
                                    inStage: slides.filter(r => r.left >= stage.left - 1 && r.right <= stage.right + 1 && r.height > 0).length,
                                    overlaps: slides.slice(1).filter((r, i) => r.top < slides[i].bottom - 1).length,
                                    controls: getComputedStyle(c.querySelector('.carousel-controls')).display
                                };
                            }""",
                            cid,
                        )
                        self.assertEqual({"inStage": total, "overlaps": 0, "controls": "none"}, state)
            finally:
                browser.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
