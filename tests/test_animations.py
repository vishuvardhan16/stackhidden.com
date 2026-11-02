"""The v5 animations: hero intro, trace render, lineage draw-in.

Each animation must do three things: play when motion is allowed, never
play when it is not, and leave the page exactly as it would be without
it.  The trace module also pins the chart's accuracy, since a bar that
encodes a date is only worth animating if it ends on the right date.
"""

from __future__ import annotations

import re
import unittest
from datetime import date

from helpers import BrowserTestCase


MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}
AXIS_START, AXIS_END = date(2026, 7, 1), date(2026, 12, 1)
INLINE_DECLARATIONS = (
    "[...document.querySelectorAll('#lineageSvg .lnode, #lineageSvg .edges path')]"
    ".reduce((total, el) => total + el.style.length, 0)"
)


def axis_percent(day: date) -> float:
    return (day - AXIS_START).days / (AXIS_END - AXIS_START).days * 100


class AnimationTest(BrowserTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.page.add_style_tag(content="html{scroll-behavior:auto!important}")

    def scroll_to(self, selector: str) -> None:
        self.page.evaluate(f"document.querySelector('{selector}').scrollIntoView({{block:'start'}})")

    def test_hero_intro_plays(self) -> None:
        self.assertEqual(
            "rise",
            self.page.evaluate("getComputedStyle(document.querySelector('.hero-text h1')).animationName"),
        )

    def test_trace_bars_end_on_their_dates(self) -> None:
        rows = self.page.evaluate(
            """() => [...document.querySelectorAll('#trace .trace-row')].map(r => ({
                when: r.querySelector('.trace-date').textContent,
                width: parseFloat(r.querySelector('.trace-bar').style.width)
            }))"""
        )
        self.assertEqual(7, len(rows))
        for row in rows:
            with self.subTest(row=row["when"]):
                month, day = re.match(r"([A-Z][a-z]{2}) (\d+)", row["when"]).groups()
                expected = axis_percent(date(2026, MONTHS[month], int(day)))
                self.assertAlmostEqual(expected, row["width"], delta=0.06)
        labels = self.page.evaluate(
            "[...document.querySelectorAll('#trace .trace-axis span')].map(s => [s.textContent, parseFloat(s.style.left)])"
        )
        for name, left in labels:
            with self.subTest(label=name):
                self.assertAlmostEqual(axis_percent(date(2026, MONTHS[name], 1)), left, delta=0.06)

    def test_trace_renders_on_first_view_then_cleans_up(self) -> None:
        trace = "document.querySelector('#trace .trace')"
        self.assertIn("trace-armed", self.page.evaluate(f"{trace}.className"))
        self.scroll_to("#trace")
        self.page.wait_for_timeout(400)
        self.assertIn("trace-drawn", self.page.evaluate(f"{trace}.className"))
        self.page.wait_for_timeout(1900)
        self.assertEqual("trace", self.page.evaluate(f"{trace}.className"))
        clips = self.page.evaluate("[...document.querySelectorAll('.trace-bar')].map(b => getComputedStyle(b).clipPath)")
        self.assertEqual(["none"] * 7, clips)

    def test_lineage_draws_itself_then_restores_the_graph(self) -> None:
        graph = "document.getElementById('lineageSvg')"
        self.assertIn("pre-draw", self.page.evaluate(f"{graph}.getAttribute('class')"))
        self.scroll_to("#lineage")
        self.page.wait_for_timeout(3600)
        self.assertEqual("lineage-svg", self.page.evaluate(f"{graph}.getAttribute('class')"))
        # Count inline declarations, not [style] attributes: Chrome can
        # leave an empty style="" behind after removeAttribute when the
        # inline style object was touched, which styles nothing.
        self.assertEqual(0, self.page.evaluate(INLINE_DECLARATIONS))
        self.assertEqual("5px, 5px", self.page.evaluate(
            "getComputedStyle(document.getElementById('e-gate-anomaly')).strokeDasharray"))
        self.page.hover(".lnode[data-node='lake'] rect")
        self.assertEqual(
            ["e-gate-lake", "e-lake-api"],
            self.page.evaluate("[...document.querySelectorAll('#lineageSvg .edges path.lit')].map(p => p.id)"),
        )

    def test_turning_motion_off_mid_draw_finishes_at_once(self) -> None:
        self.scroll_to("#lineage")
        self.page.wait_for_timeout(300)
        self.page.evaluate("document.getElementById('motionBtn').click()")
        self.page.wait_for_timeout(100)
        self.assertEqual("lineage-svg", self.page.evaluate("document.getElementById('lineageSvg').getAttribute('class')"))
        self.assertEqual(0, self.page.evaluate(INLINE_DECLARATIONS))

    def test_head_script_applies_a_stored_reduce_motion_choice(self) -> None:
        # The inline <head> script runs before first paint, before app.js,
        # so a returning visitor who turned motion off never sees the intro.
        result = self.page.evaluate(
            """() => {
                const head = [...document.querySelectorAll('head script:not([type])')][0].textContent;
                localStorage.setItem('motion', 'reduced');
                document.documentElement.removeAttribute('data-motion');
                (0, eval)(head);
                const applied = document.documentElement.getAttribute('data-motion');
                localStorage.removeItem('motion');
                return applied;
            }"""
        )
        self.assertEqual("reduced", result)


class ArriveByLinkTest(BrowserTestCase):
    """Opened at #lineage: app.js runs before the browser jumps to the
    anchor, so the graph draws as the visitor lands. It must always end
    fully drawn, never stuck hidden."""

    page_suffix = "#lineage"

    def test_graph_ends_fully_drawn(self) -> None:
        # The browser smooth-scrolls to the anchor first (about a second),
        # so wait for the outcome rather than a fixed time.
        self.page.wait_for_function(
            "document.getElementById('lineageSvg').getAttribute('class') === 'lineage-svg' && "
            + INLINE_DECLARATIONS + " === 0",
            timeout=8000,
        )


class ReducedMotionAnimationTest(BrowserTestCase):
    reduced_motion = "reduce"

    def test_nothing_is_armed_or_animated(self) -> None:
        state = self.page.evaluate(
            """() => ({
                hero: getComputedStyle(document.querySelector('.hero-text h1')).animationName,
                trace: document.querySelector('#trace .trace').className,
                graph: document.getElementById('lineageSvg').getAttribute('class')
            })"""
        )
        self.assertEqual({"hero": "none", "trace": "trace", "graph": "lineage-svg"}, state)


if __name__ == "__main__":
    unittest.main(verbosity=2)
