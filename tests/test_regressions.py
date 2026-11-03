"""Regression guards for bugs fixed in v5 (Nov 2026).

Each test pins one bug that shipped silently: nothing threw at load, the
page still looked fine at a glance, and the existing suite passed.  They
were found by reading app.js, then confirmed in a browser.
"""

from __future__ import annotations

import unittest

from helpers import BrowserTestCase


PAINTED_PIXELS = """() => {
    const c = document.getElementById('graph');
    const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
    let n = 0;
    for (let i = 3; i < d.length; i += 4) if (d[i] > 0) n++;
    return n;
}"""


class RegressionTest(BrowserTestCase):
    def setUp(self) -> None:
        super().setUp()
        # Smooth scrolling races Playwright's pointer moves; tests that
        # hover after scrolling need the jump to be instant.
        self.page.add_style_tag(content="html{scroll-behavior:auto!important}")

    def test_background_canvas_paints_at_load(self) -> None:
        # A shared `var nodes` let the lineage explorer overwrite the
        # canvas particle array, so the background stayed empty until
        # the visitor resized the window.
        self.assertGreater(self.page.evaluate(PAINTED_PIXELS), 500)

    def test_lineage_hover_still_works_after_a_resize(self) -> None:
        # The same collision ran the other way after a resize: the
        # explorer iterated particle objects and threw on classList.
        self.page.set_viewport_size({"width": 1200, "height": 860})
        self.page.wait_for_timeout(200)
        self.page.evaluate(
            "document.getElementById('lineage').scrollIntoView({block:'center'})"
        )
        self.page.hover(".lnode[data-node='gate'] rect")
        self.assertIn("Quality gate", self.page.inner_text("#lineageDetail"))

    def test_scrollspy_marks_the_section_in_view(self) -> None:
        # The selector targeted a .site-nav class that does not exist.
        for section_id in ("about", "writing", "contact"):
            with self.subTest(section=section_id):
                self.page.evaluate(
                    f"document.getElementById('{section_id}')"
                    ".scrollIntoView({block:'start'})"
                )
                self.page.wait_for_timeout(250)
                active = self.page.evaluate(
                    "[...document.querySelectorAll('.site-header nav a.active')]"
                    ".map(a => a.getAttribute('href'))"
                )
                self.assertEqual([f"#{section_id}"], active)

    # Counts only frames requested by the background loop (the function
    # named `step`). Counting every frame mixes in the core, bot, and
    # glow loops and cannot tell one graph loop from two.
    GRAPH_FRAMES = """async () => {
        let calls = 0;
        const raf = window.requestAnimationFrame;
        window.requestAnimationFrame = cb => {
            if (cb && cb.name === 'step') calls++;
            return raf(cb);
        };
        await new Promise(r => setTimeout(r, 600));
        window.requestAnimationFrame = raf;
        return calls;
    }"""

    def click_motion(self) -> None:
        self.page.evaluate("document.getElementById('motionBtn').click()")

    def test_motion_toggle_does_not_stack_canvas_loops(self) -> None:
        # applyMotion() started a new loop on every call (once at load,
        # then on each toggle), so the field sped up each time.
        baseline = self.page.evaluate(self.GRAPH_FRAMES)
        for _ in range(6):
            self.click_motion()
        after = self.page.evaluate(self.GRAPH_FRAMES)
        # One loop runs at the display rate; a stacked loop doubles it.
        self.assertGreater(baseline, 0)
        self.assertLess(after, baseline * 1.4)

    def test_core_resumes_when_motion_is_turned_back_on(self) -> None:
        # Compare whole frames, not their encoded length (two different
        # frames can encode to the same number of bytes), and wait for a
        # new frame rather than a fixed time, because CI runners are slow.
        # A core that stays frozen still fails: no new frame within 4s.
        self.click_motion()
        self.click_motion()
        first = self.page.evaluate("document.getElementById('coreAnim').toDataURL()")
        self.page.wait_for_function(
            "(first) => document.getElementById('coreAnim').toDataURL() !== first",
            arg=first,
            timeout=4000,
        )

    def test_footer_reduce_motion_holds_the_carousel(self) -> None:
        active = (
            "[...document.querySelectorAll('#quoteCarousel .slide')]"
            ".findIndex(s => s.classList.contains('on'))"
        )
        self.click_motion()
        before = self.page.evaluate(active)
        self.page.wait_for_timeout(5600)
        self.assertEqual(before, self.page.evaluate(active))


class CarouselActiveDotTest(BrowserTestCase):
    """Choosing the slide that is already showing must keep it showing."""

    reduced_motion = "reduce"

    def test_clicking_the_active_dot_keeps_the_quote_on_screen(self) -> None:
        # Before the fix the slide was marked both "on" and "out", "out"
        # won, and the visible quote slid off, leaving an empty stage. The
        # query console's Trace hit the same path for a quote on screen.
        state = """() => {
            const s = document.querySelector('#quoteCarousel .slide.on');
            const st = document.querySelector('#quoteCarousel .carousel-stage').getBoundingClientRect();
            return { out: s.classList.contains('out'), left: Math.round(s.getBoundingClientRect().left - st.left) };
        }"""
        self.page.evaluate("document.querySelectorAll('#quoteCarousel .carousel-dot')[0].click()")
        self.page.wait_for_timeout(100)
        self.assertEqual({"out": False, "left": 0}, self.page.evaluate(state))


LANDING = """(id) => ({
    header: Math.round(document.querySelector('.site-header').getBoundingClientRect().bottom),
    top: Math.round(document.getElementById(id).getBoundingClientRect().top)
})"""


class AnchorLandingTest(BrowserTestCase):
    """In-page jumps stop just below the sticky header, at every width."""

    def test_nav_jumps_land_below_the_header(self) -> None:
        # Before the fix there was no scroll padding, so every jump put the
        # section's top under the header; a section that had not revealed
        # yet then rose 22px further. Writing's heading ended 16px above
        # the viewport, hidden, on desktop and on phones.
        for width, height in ((1400, 900), (390, 844)):
            for target in ("about", "writing", "query"):
                with self.subTest(width=width, target=target):
                    self.page.set_viewport_size({"width": width, "height": height})
                    self.reload_page()
                    self.page.add_style_tag(content="html{scroll-behavior:auto!important}")
                    self.page.evaluate(f"document.querySelector('.site-header nav a[href=\"#{target}\"]').click()")
                    self.page.wait_for_timeout(900)  # past the 0.7s section reveal
                    landing = self.page.evaluate(LANDING, target)
                    self.assertGreaterEqual(landing["top"], landing["header"], landing)
                    self.assertLess(landing["top"] - landing["header"], 30, landing)


if __name__ == "__main__":
    unittest.main(verbosity=2)
