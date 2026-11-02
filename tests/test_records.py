"""Send a record through the lineage explorer (v5, Nov 2026).

The feature makes one claim: a bad record never reaches anything past
the quality gate.  These tests check that claim from the pipeline log,
the counter, and the announcement, in normal and reduced motion, and
that the graph stays legible on a phone.
"""

from __future__ import annotations

import unittest

from helpers import BrowserTestCase


LOG = "[...document.querySelectorAll('#linLog li')].map(li => li.querySelector('b').textContent + ' ' + li.querySelector('span').textContent)"


def stages_for(lines: list[str], record_id: str) -> list[str]:
    return [line.split(" ", 1)[0] for line in lines if f" {record_id} " in f" {line} "]


class SendRecordTest(BrowserTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.page.add_style_tag(content="html{scroll-behavior:auto!important}")
        self.page.evaluate("document.getElementById('lineage').scrollIntoView()")

    def wait_for_count(self, text: str) -> None:
        self.page.wait_for_function(
            f"document.getElementById('linCount').textContent.replace(/\\s+/g,' ') === {text!r}",
            timeout=9000,
        )

    def record_ids(self, lines: list[str]) -> list[str]:
        ids: list[str] = []
        for line in lines:
            rid = line.split(" ")[1]
            if rid not in ids:
                ids.append(rid)
        return ids

    def test_clean_record_reaches_analytics(self) -> None:
        self.page.click("#sendClean")
        self.wait_for_count("Passed 1 · Flagged 0")
        lines = self.page.evaluate(LOG)
        rid = self.record_ids(lines)[0]
        self.assertEqual(
            ["ingest", "transform", "gate", "lake", "api", "analytics"],
            stages_for(lines, rid),
        )
        self.assertIn("reached Advertiser analytics", self.page.inner_text("#lineageDetail"))
        self.page.wait_for_timeout(600)
        self.assertEqual(0, self.page.evaluate("document.querySelectorAll('#lineageSvg .rec').length"))

    def test_bad_record_stops_at_the_gate(self) -> None:
        self.page.click("#sendBad")
        self.wait_for_count("Passed 0 · Flagged 1")
        lines = self.page.evaluate(LOG)
        rid = self.record_ids(lines)[0]
        stages = stages_for(lines, rid)
        self.assertEqual(["ingest", "transform", "gate", "anomaly"], stages)
        self.assertNotIn("lake", stages)
        self.assertEqual(2, self.page.evaluate("document.querySelectorAll('#linLog li.fail').length"))
        self.assertIn("Nothing downstream received it", self.page.inner_text("#lineageDetail"))

    def test_records_in_flight_together_keep_their_own_routes(self) -> None:
        self.page.click("#sendClean")
        self.page.wait_for_timeout(200)
        self.page.click("#sendBad")
        self.wait_for_count("Passed 1 · Flagged 1")
        lines = self.page.evaluate(LOG)
        clean, bad = self.record_ids(lines)[:2]
        self.assertEqual("analytics", stages_for(lines, clean)[-1])
        self.assertEqual("anomaly", stages_for(lines, bad)[-1])


class SendRecordReducedMotionTest(BrowserTestCase):
    reduced_motion = "reduce"

    def test_arrives_at_once_without_a_moving_dot(self) -> None:
        self.page.click("#sendBad")
        self.assertEqual("Passed 0 · Flagged 1", self.page.inner_text("#linCount"))
        self.assertEqual(4, self.page.evaluate("document.querySelectorAll('#linLog li').length"))
        self.assertEqual(0, self.page.evaluate("document.querySelectorAll('#lineageSvg .rec').length"))


class LineagePhoneTest(BrowserTestCase):
    viewport = {"width": 360, "height": 800}

    def test_graph_labels_stay_legible_and_scroll_in_place(self) -> None:
        info = self.page.evaluate(
            """() => {
                const label = document.querySelector('#lineageSvg .lnode text');
                const wrap = document.querySelector('.lineage-scroll');
                return {
                    label: label.getBoundingClientRect().height,
                    inner: wrap.scrollWidth, box: wrap.clientWidth,
                    page: document.documentElement.scrollWidth
                };
            }"""
        )
        self.assertGreaterEqual(info["label"], 10)
        self.assertGreater(info["inner"], info["box"])
        self.assertLessEqual(info["page"], 361)


if __name__ == "__main__":
    unittest.main(verbosity=2)
