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
                    # A fresh load at the top, not a reload: a reload
                    # restores the previous jump's scroll position, and
                    # under load that restore can land after the click
                    # below, failing about 1 run in 6 when the suite runs
                    # alongside other work (seen Nov 7, 2026, on code
                    # from before that day too).
                    self.open_page()
                    self.page.add_style_tag(content="html{scroll-behavior:auto!important}")
                    self.page.evaluate(f"document.querySelector('.site-header nav a[href=\"#{target}\"]').click()")
                    self.page.wait_for_timeout(900)  # past the 0.7s section reveal
                    landing = self.page.evaluate(LANDING, target)
                    self.assertGreaterEqual(landing["top"], landing["header"], landing)
                    self.assertLess(landing["top"] - landing["header"], 30, landing)


# The phone header's link row, measured against its own box.
NAV_ROW = """() => {
    const nav = document.querySelector('.site-header nav'), box = nav.getBoundingClientRect();
    const mask = getComputedStyle(nav).webkitMaskImage || getComputedStyle(nav).maskImage || 'none';
    const links = [...nav.querySelectorAll('a')].map(a => {
        const r = a.getBoundingClientRect();
        return { text: a.textContent, left: r.left - box.left, right: r.right - box.left, active: a.classList.contains('active') };
    });
    return {
        width: box.width, scrollLeft: nav.scrollLeft, links,
        // Do the row's ends fade? The mask's first and last colour stops.
        fadesLeft: /^linear-gradient\\(to right, rgba\\(0, 0, 0, 0\\)/.test(mask),
        fadesRight: /rgba\\(0, 0, 0, 0\\)\\)$/.test(mask)
    };
}"""
FADE = 28  # px, the width of each edge fade in style.css


class PhoneNavRowTest(BrowserTestCase):
    """On phones the links scroll sideways in one row under the brand.

    Nov 7, 2026: once the row had scrolled, its left edge cut a link in
    half with a hard edge ("ting" of Writing), the link in view could sit
    half under the fade, and going back to the top left the last section's
    link lit and the row still scrolled.
    """

    viewport = {"width": 390, "height": 844}
    reduced_motion = "reduce"
    # At 390px every scroll of the row runs to its end; at 320px it can
    # stop part way, which is where the lit link's position is chosen.
    WIDTHS = (320, 390)
    SECTIONS = ("about", "engineering", "trace", "writing", "featured", "speaking", "query", "contact")

    def at_width(self, width: int) -> None:
        self.page.set_viewport_size({"width": width, "height": 844})
        self.reload_page()
        self.page.add_style_tag(content="html{scroll-behavior:auto!important}")

    def go(self, section_id: str) -> dict:
        self.page.evaluate(f"document.getElementById('{section_id}').scrollIntoView({{block:'start'}})")
        self.page.wait_for_timeout(300)
        return self.page.evaluate(NAV_ROW)

    def test_wherever_the_row_cuts_a_link_that_edge_fades(self) -> None:
        for width in self.WIDTHS:
            self.at_width(width)
            scrolled = False
            for section_id in self.SECTIONS:
                with self.subTest(width=width, section=section_id):
                    row = self.go(section_id)
                    scrolled = scrolled or row["scrollLeft"] > 0
                    for link in row["links"]:
                        if link["left"] < 0 < link["right"]:
                            self.assertTrue(row["fadesLeft"], f"{link['text']} is cut at the left with no fade")
                            self.assertLessEqual(link["right"], FADE, f"{link['text']} shows past the fade")
                        if link["left"] < row["width"] < link["right"]:
                            self.assertTrue(row["fadesRight"], f"{link['text']} is cut at the right with no fade")
                    # No fade over the start of the row before it has scrolled.
                    if row["scrollLeft"] == 0:
                        self.assertFalse(row["fadesLeft"])
            self.assertTrue(scrolled, f"the row never scrolled at {width}px, so this checked nothing")

    def test_the_lit_link_sits_clear_of_both_fades(self) -> None:
        for width in self.WIDTHS:
            self.at_width(width)
            for section_id in self.SECTIONS:
                with self.subTest(width=width, section=section_id):
                    row = self.go(section_id)
                    active = [link for link in row["links"] if link["active"]]
                    self.assertEqual(1, len(active))
                    start = FADE if row["fadesLeft"] else 0
                    self.assertGreaterEqual(active[0]["left"], start - 0.5, active[0])
                    self.assertLessEqual(active[0]["right"], row["width"] - FADE + 0.5, active[0])

    def test_a_swipe_comes_to_rest_on_a_link_not_mid_word(self) -> None:
        # Swipe the row by hand, in steps that stop between links, and
        # let it settle: the cut link, if any, lies inside the left fade.
        for width in self.WIDTHS:
            self.at_width(width)
            box = self.page.locator(".site-header nav").bounding_box()
            self.page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
            for step in range(6):
                with self.subTest(width=width, step=step):
                    self.page.mouse.wheel(57, 0)
                    self.page.wait_for_timeout(500)
                    row = self.page.evaluate(NAV_ROW)
                    for link in row["links"]:
                        if link["left"] < 0 < link["right"]:
                            self.assertLessEqual(link["right"], FADE + 0.5, f"{link['text']} shows past the fade")
                    starts = [link["left"] for link in row["links"] if link["left"] >= 0]
                    if row["scrollLeft"] > 0:
                        self.assertAlmostEqual(FADE, min(starts), delta=1)

    def test_widening_the_window_restores_the_desktop_row(self) -> None:
        # The space after the last link is sized for the phone row only.
        trailing = "getComputedStyle(document.querySelector('.site-header nav a:last-child')).marginRight"
        self.at_width(320)
        self.assertNotEqual("28px", self.page.evaluate(trailing))
        self.page.set_viewport_size({"width": 1400, "height": 900})
        self.page.wait_for_timeout(200)
        widened = self.page.evaluate(trailing)
        self.reload_page()
        self.assertEqual(self.page.evaluate(trailing), widened)

    def test_back_at_the_top_no_link_is_lit_and_the_row_starts_over(self) -> None:
        for width in self.WIDTHS:
            with self.subTest(width=width):
                self.at_width(width)
                self.go("contact")
                self.page.evaluate("document.querySelector('.brand').click()")
                self.page.wait_for_timeout(400)
                row = self.page.evaluate(NAV_ROW)
                self.assertEqual([], [link["text"] for link in row["links"] if link["active"]])
                self.assertEqual(0, row["scrollLeft"])
                self.assertFalse(row["fadesLeft"])


class DesktopNavTopTest(BrowserTestCase):
    """The same rule on desktop: at the top, above About, nothing is lit."""

    reduced_motion = "reduce"

    def test_back_at_the_top_no_link_is_lit(self) -> None:
        self.page.add_style_tag(content="html{scroll-behavior:auto!important}")
        self.page.evaluate("document.getElementById('contact').scrollIntoView({block:'start'})")
        self.page.wait_for_timeout(300)
        self.page.evaluate("document.querySelector('.brand').click()")
        self.page.wait_for_timeout(400)
        self.assertEqual([], self.page.evaluate("[...document.querySelectorAll('.site-header nav a.active')].map(a => a.textContent)"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
