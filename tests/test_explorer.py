"""Interactive lineage explorer behaviour."""

from __future__ import annotations

import unittest

from helpers import BrowserTestCase


class LineageExplorerTest(BrowserTestCase):
    def test_nine_nodes_and_hover_lights_only_connected_edges(self) -> None:
        nodes = self.page.locator("#lineageSvg .lnode")
        self.assertEqual(9, nodes.count())

        ingest = self.page.locator('#lineageSvg .lnode[data-node="ingest"]')
        ingest.scroll_into_view_if_needed()
        ingest.hover()
        self.page.wait_for_function(
            "() => document.getElementById('e-feed-ingest').classList.contains('lit')"
        )

        connected = self.page.locator("#e-feed-ingest")
        unrelated = self.page.locator("#e-lake-api")
        self.assertIn("lit", connected.get_attribute("class") or "")
        self.assertIn("dim", unrelated.get_attribute("class") or "")
        self.assertIn(
            "Ingest - first stage under our control.",
            self.page.locator("#lineageDetail").inner_text(),
        )


# The graph's geometry in its own user units (the viewBox), so it holds at
# every width. Nov 7, 2026: Flagged anomalies sat on top of the Data lake
# (10 units deep), its label touched its border, the gate's edge to the
# lake stopped 15 units short of it, the dashed edge to Flagged anomalies
# ran through the lake, and the clickstream edge grazed Advertiser
# analytics. These pin the fixed layout.
GEOMETRY = """() => {
    const svg = document.getElementById('lineageSvg');
    const stages = {};
    svg.querySelectorAll('.lnode').forEach(g => {
        const r = g.querySelector('rect'), t = g.querySelector('text').getBBox();
        const box = { x: +r.getAttribute('x'), y: +r.getAttribute('y'), w: +r.getAttribute('width'), h: +r.getAttribute('height') };
        box.labelPad = Math.min(t.x - box.x, box.x + box.w - (t.x + t.width));
        box.labelInside = t.y >= box.y && t.y + t.height <= box.y + box.h;
        stages[g.dataset.node] = box;
    });
    const dist = (p, b) => Math.hypot(Math.max(b.x - p.x, 0, p.x - (b.x + b.w)), Math.max(b.y - p.y, 0, p.y - (b.y + b.h)));
    const sample = (path) => {
        const L = path.getTotalLength(), pts = [];
        for (let s = 0; s < L; s += 1) pts.push(path.getPointAtLength(s));
        pts.push(path.getPointAtLength(L));
        return pts;
    };
    const names = Object.keys(stages), gaps = [];
    for (let i = 0; i < names.length; i++) for (let j = i + 1; j < names.length; j++) {
        const a = stages[names[i]], b = stages[names[j]];
        const dx = Math.max(a.x - (b.x + b.w), b.x - (a.x + a.w)), dy = Math.max(a.y - (b.y + b.h), b.y - (a.y + a.h));
        // Overlapping boxes have both dx and dy negative: report how deep.
        gaps.push({ pair: names[i] + '/' + names[j], gap: dx < 0 && dy < 0 ? Math.max(dx, dy) : Math.hypot(Math.max(dx, 0), Math.max(dy, 0)) });
    }
    const edges = [...svg.querySelectorAll('.edges path')].map(p => {
        const [, from, to] = p.id.split('-'), pts = sample(p);
        const clearance = {};
        names.filter(n => n !== from && n !== to).forEach(n => { clearance[n] = Math.min(...pts.map(q => dist(q, stages[n]))); });
        return { id: p.id, start: dist(pts[0], stages[from]), end: dist(pts[pts.length - 1], stages[to]), clearance };
    });
    const amber = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    amber.setAttribute('d', svg.querySelector('.anomaly-packet animateMotion').getAttribute('path'));
    svg.appendChild(amber);
    const amberPts = sample(amber);
    amber.remove();
    return {
        stages, gaps, edges,
        amber: { touches: names.filter(n => amberPts.some(q => dist(q, stages[n]) === 0)),
                 endsIn: names.filter(n => dist(amberPts[amberPts.length - 1], stages[n]) === 0) }
    };
}"""

# Follows the record dot a visitor sends, frame by frame, until it is gone.
FOLLOW_RECORD = """async (bad) => {
    const svg = document.getElementById('lineageSvg'), pts = [];
    const watch = new MutationObserver(ms => ms.forEach(m => {
        if (m.target.classList.contains('rec')) pts.push([+m.target.getAttribute('cx'), +m.target.getAttribute('cy')]);
    }));
    watch.observe(svg, { subtree: true, attributes: true, attributeFilter: ['cx', 'cy'] });
    document.getElementById(bad ? 'sendBad' : 'sendClean').click();
    await new Promise(done => { const t = setInterval(() => { if (!svg.querySelector('.rec')) { clearInterval(t); done(); } }, 40); });
    watch.disconnect();
    return pts;
}"""


class LineageLayoutTest(BrowserTestCase):
    """Every stage has room, and every edge joins the stages it names."""

    reduced_motion = "reduce"

    def setUp(self) -> None:
        super().setUp()
        self.geometry = self.page.evaluate(GEOMETRY)

    def test_no_two_stages_overlap_or_crowd(self) -> None:
        for pair in self.geometry["gaps"]:
            with self.subTest(pair=pair["pair"]):
                self.assertGreaterEqual(pair["gap"], 20)

    def test_every_label_sits_inside_its_box_with_room(self) -> None:
        # The labels are in each visitor's system font, so check the font
        # this machine renders and DejaVu Sans, the Linux default and the
        # widest common one. On Nov 7, 2026 this passed here in Inter and
        # failed on the site-checks runner in DejaVu Sans, with Advertiser
        # feeds, Spark transform, and Flagged anomalies 6 units from their
        # borders; the boxes were then sized for DejaVu Sans.
        for font in (None, "DejaVu Sans"):
            if font:
                self.page.evaluate("(f) => document.querySelector('#lineageSvg .nodes').setAttribute('font-family', f)", font)
            stages = self.page.evaluate(GEOMETRY)["stages"]
            for name, box in stages.items():
                with self.subTest(font=font or "system font here", stage=name):
                    self.assertTrue(box["labelInside"])
                    self.assertGreaterEqual(box["labelPad"], 8)

    def test_every_edge_joins_its_two_stages_and_clears_the_rest(self) -> None:
        for edge in self.geometry["edges"]:
            with self.subTest(edge=edge["id"]):
                self.assertLessEqual(edge["start"], 1)
                self.assertLessEqual(edge["end"], 1)
                for stage, clearance in edge["clearance"].items():
                    self.assertGreaterEqual(clearance, 12, f"{edge['id']} passes {clearance:.1f} units from {stage}")

    def test_the_drawing_has_even_margins_inside_its_frame(self) -> None:
        # Every stage inside the viewBox, with the same room above the
        # top stage as below the bottom one, and left as right.
        frame = self.page.evaluate("(() => { const v = document.getElementById('lineageSvg').viewBox.baseVal; return [v.width, v.height]; })()")
        boxes = self.geometry["stages"].values()
        top = min(b["y"] for b in boxes)
        bottom = frame[1] - max(b["y"] + b["h"] for b in boxes)
        left = min(b["x"] for b in boxes)
        right = frame[0] - max(b["x"] + b["w"] for b in boxes)
        self.assertGreaterEqual(min(top, bottom), 12)
        self.assertLessEqual(abs(top - bottom), 6)
        self.assertGreaterEqual(min(left, right), 8)
        self.assertLessEqual(abs(left - right), 6)

    def test_the_amber_packet_never_crosses_the_data_lake(self) -> None:
        # The gate exists to keep flagged records out of the lake, so the
        # packet that stands for them must not travel through it.
        amber = self.geometry["amber"]
        self.assertEqual(["anomaly"], amber["endsIn"])
        for stage in ("lake", "api", "analytics"):
            self.assertNotIn(stage, amber["touches"])


class RecordRouteTest(BrowserTestCase):
    """The record a visitor sends follows the drawn pipeline."""

    def setUp(self) -> None:
        super().setUp()
        self.page.add_style_tag(content="html{scroll-behavior:auto!important}")
        self.page.evaluate("document.getElementById('lineage').scrollIntoView({block:'center'})")
        self.stages = self.page.evaluate(GEOMETRY)["stages"]

    def inside(self, point: list[float]) -> set[str]:
        x, y = point
        return {n for n, b in self.stages.items() if b["x"] <= x <= b["x"] + b["w"] and b["y"] <= y <= b["y"] + b["h"]}

    def test_a_bad_record_stops_at_flagged_anomalies_without_entering_the_lake(self) -> None:
        points = self.page.evaluate(FOLLOW_RECORD, True)
        self.assertGreater(len(points), 30)
        visited = set().union(*(self.inside(p) for p in points))
        self.assertTrue({"ingest", "transform", "gate", "anomaly"} <= visited, visited)
        self.assertFalse(visited & {"lake", "api", "analytics"}, visited)
        self.assertEqual({"anomaly"}, self.inside(points[-1]))

    def test_a_clean_record_reaches_analytics_without_touching_flagged_anomalies(self) -> None:
        points = self.page.evaluate(FOLLOW_RECORD, False)
        visited = set().union(*(self.inside(p) for p in points))
        self.assertTrue({"ingest", "transform", "gate", "lake", "api", "analytics"} <= visited, visited)
        self.assertNotIn("anomaly", visited)
        self.assertEqual({"analytics"}, self.inside(points[-1]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
