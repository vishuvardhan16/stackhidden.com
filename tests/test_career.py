"""Career, as a trace (v5, Nov 2026).

The Experience section opens with every role since 2019, and the graduate
degree, as a span on a year axis.  A bar that encodes dates is only worth
showing if it ends on the right dates, so these tests recompute every
position in Python and compare.  They also pin that the chart restates the
entries below it and adds nothing, that it works from the keyboard, that
its year labels never collide at any width, and that its first-view render
follows the motion rules in docs/motion.md.
"""

from __future__ import annotations

import re
import unittest
from datetime import date

from helpers import ROOT, BrowserTestCase


FIRST_YEAR = 2019
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
# The inline positions in index.html, which a visitor sees with JavaScript
# off, are the same computation as of this date.
SNAPSHOT = date(2026, 11, 2)


def axis_percent(day: date, today: date) -> float:
    start, end = date(FIRST_YEAR, 1, 1), date(today.year + 1, 1, 1)
    return (day - start).days / (end - start).days * 100


def span_percent(start: str, end: str, today: date) -> tuple[float, float]:
    """Left and width of a span, as app.js draws it.

    A span starts on the first day of its first month and ends on the first
    day of the month after its last, so a one-month internship has width.
    "now" ends on today.
    """

    y, m = map(int, start.split("-"))
    left = axis_percent(date(y, m, 1), today)
    if end == "now":
        right = axis_percent(today, today)
    else:
        y, m = map(int, end.split("-"))
        right = axis_percent(date(y + m // 12, m % 12 + 1, 1), today)
    return left, right - left


def month_label(ym: str) -> str:
    y, m = map(int, ym.split("-"))
    return f"{MONTHS[m - 1]} {y}"


def length_label(start: str, end: str, today: date) -> str:
    """Inclusive months, the way LinkedIn counts: "4 yrs 3 mos"."""

    sy, sm = map(int, start.split("-"))
    ey, em = (today.year, today.month) if end == "now" else map(int, end.split("-"))
    n = (ey - sy) * 12 + (em - sm) + 1
    yrs, mos = divmod(n, 12)
    out = []
    if yrs:
        out.append(f"{yrs} yr" if yrs == 1 else f"{yrs} yrs")
    if mos:
        out.append(f"{mos} mo" if mos == 1 else f"{mos} mos")
    return " ".join(out)


ROWS = """() => [...document.querySelectorAll('.career-row')].map(r => ({
    start: r.dataset.start, end: r.dataset.end, kind: r.dataset.kind, target: r.dataset.target,
    org: r.querySelector('.career-org').textContent,
    title: r.querySelector('.career-title').textContent,
    when: r.querySelector('.career-when').textContent,
    barKind: r.querySelector('.career-bar').classList[1],
    left: parseFloat(r.querySelector('.career-bar').style.left),
    width: parseFloat(r.querySelector('.career-bar').style.width)
}))"""
AXIS = """() => [...document.querySelectorAll('.career-axis span')].map(s => {
    const r = s.getBoundingClientRect();
    return { text: s.textContent, left: parseFloat(s.style.left), shown: getComputedStyle(s).visibility === 'visible',
             x0: r.left, x1: r.right };
})"""


class CareerTest(BrowserTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.page.add_style_tag(content="html{scroll-behavior:auto!important}")
        self.today = date.today()

    def rows(self) -> list[dict]:
        return self.page.evaluate(ROWS)

    def test_every_span_sits_on_its_dates(self) -> None:
        rows = self.rows()
        self.assertEqual(6, len(rows))
        for row in rows:
            with self.subTest(row=f"{row['org']}, {row['title']}"):
                left, width = span_percent(row["start"], row["end"], self.today)
                self.assertAlmostEqual(left, row["left"], delta=0.01)
                self.assertAlmostEqual(width, row["width"], delta=0.01)
                self.assertEqual(f"kind-{row['kind']}", row["barKind"])
        # The current role ends exactly at today's mark on the axis.
        amazon = rows[-1]
        self.assertEqual("now", amazon["end"])
        self.assertAlmostEqual(axis_percent(self.today, self.today), amazon["left"] + amazon["width"], delta=0.02)

    def test_every_bar_is_drawn_at_full_height(self) -> None:
        # The bars first shipped as class "role", which the page's older
        # .role heading rule matched: its margins collapsed both role bars
        # (TA Digital, Amazon) to zero height while their positions were
        # still right. So check what is painted, not only the numbers.
        bars = self.page.evaluate(
            """() => [...document.querySelectorAll('.career-row')].map(r => {
                const bar = r.querySelector('.career-bar').getBoundingClientRect();
                const track = r.querySelector('.career-track').getBoundingClientRect();
                const cs = getComputedStyle(r.querySelector('.career-bar'));
                return { kind: r.dataset.kind, h: bar.height, w: bar.width, track: track.height,
                         painted: cs.backgroundImage !== 'none' || cs.backgroundColor !== 'rgba(0, 0, 0, 0)' };
            })"""
        )
        for bar in bars:
            with self.subTest(bar=bar):
                self.assertEqual(bar["track"], bar["h"])
                self.assertGreaterEqual(bar["w"], 6)
                self.assertTrue(bar["painted"])

    def test_rows_run_oldest_first(self) -> None:
        starts = [row["start"] for row in self.rows()]
        self.assertEqual(sorted(starts), starts)

    def test_axis_marks_every_year_and_today(self) -> None:
        labels = self.page.evaluate(AXIS)
        years = list(range(FIRST_YEAR, self.today.year + 1))
        self.assertEqual([str(y) for y in years] + ["now"], [label["text"] for label in labels])
        for year, label in zip(years, labels):
            with self.subTest(year=year):
                self.assertAlmostEqual(axis_percent(date(year, 1, 1), self.today), label["left"], delta=0.01)
        self.assertAlmostEqual(axis_percent(self.today, self.today), labels[-1]["left"], delta=0.01)
        # At desktop width every label has room.
        self.assertTrue(all(label["shown"] for label in labels), labels)

    def test_the_chart_restates_the_entries_below_it(self) -> None:
        # Nothing in the chart is new: each row's organisation, title, and
        # dates appear in the entry it links to, in that entry's words
        # ("Present" for the current role).
        for row in self.rows():
            with self.subTest(row=f"{row['org']}, {row['title']}"):
                start = month_label(row["start"])
                if row["end"] == "now":
                    expected_when, entry_when = f"{start} to now", f"{start} to Present"
                elif row["end"] == row["start"]:
                    expected_when = entry_when = start
                else:
                    expected_when = entry_when = f"{start} to {month_label(row['end'])}"
                self.assertEqual(expected_when, row["when"])
                entry = self.page.evaluate(
                    "(id) => { const el = document.getElementById(id); return el ? el.textContent.replace(/\\s+/g, ' ') : null; }",
                    row["target"],
                )
                self.assertIsNotNone(entry, f"no entry #{row['target']}")
                self.assertIn(row["org"], entry)
                # The TA Digital internship is a sentence in that entry
                # ("interned there from Dec 2019 to Feb 2020"), not a heading.
                self.assertIn(row["title"].lower(), entry.lower())
                self.assertIn(entry_when, entry)

    def test_keyboard_moves_between_rows_and_selects_one(self) -> None:
        index = "[...document.querySelectorAll('.career-row')].indexOf(document.activeElement)"
        self.page.focus(".career-row")
        for key, expected in (("ArrowDown", 1), ("ArrowDown", 2), ("End", 5), ("ArrowDown", 5),
                              ("Home", 0), ("ArrowUp", 0), ("End", 5)):
            self.page.keyboard.press(key)
            self.assertEqual(expected, self.page.evaluate(index), key)
        self.page.keyboard.press("Enter")
        pressed = self.page.evaluate(
            "[...document.querySelectorAll('.career-row')].map(r => r.getAttribute('aria-pressed'))"
        )
        self.assertEqual(["false"] * 5 + ["true"], pressed)
        length = length_label("2022-09", "now", self.today)
        self.assertEqual(
            f"Amazon Advertising · Software Development Engineer · Sep 2022 to now · {length}"
            " · New York City Metropolitan Area, Hybrid.Read the full entry",
            self.page.text_content("#careerDetail"),
        )

    def test_detail_gives_length_and_place_and_links_to_the_entry(self) -> None:
        for i, row in enumerate(self.rows()):
            with self.subTest(row=f"{row['org']}, {row['title']}"):
                self.page.locator(".career-row").nth(i).click()
                text = self.page.text_content("#careerDetail")
                self.assertIn(f" · {length_label(row['start'], row['end'], self.today)}", text)
                self.assertEqual(f"#{row['target']}", self.page.get_attribute("#careerDetail a", "href"))
        # The degree has no place line in its entry, and none is invented.
        self.page.locator(".career-row").nth(3).click()
        self.assertEqual(
            "University at Buffalo · Master of Engineering Science, Data Science (MS) · Aug 2021 to Aug 2022 · 1 yr 1 mo.",
            self.page.evaluate("document.getElementById('careerDetail').firstChild.textContent"),
        )
        self.page.click("#careerDetail a")
        # Past the section's 0.7s reveal, which must not move the entry.
        self.page.wait_for_timeout(900)
        state = self.page.evaluate(
            """() => { const el = document.getElementById('edu-buffalo'), r = el.getBoundingClientRect();
                       const header = document.querySelector('.site-header').getBoundingClientRect().bottom;
                       return { traced: el.classList.contains('traced'),
                                belowHeader: r.top >= header && r.top < header + 40 }; }"""
        )
        self.assertEqual({"traced": True, "belowHeader": True}, state)

    def test_year_labels_never_collide_at_any_width(self) -> None:
        for width in (360, 414, 768, 1024, 1400):
            with self.subTest(width=width):
                self.page.set_viewport_size({"width": width, "height": 900})
                self.page.wait_for_timeout(120)
                shown = [label for label in self.page.evaluate(AXIS) if label["shown"]]
                self.assertEqual("now", shown[-1]["text"])
                self.assertEqual(str(FIRST_YEAR), shown[0]["text"])
                self.assertGreaterEqual(len(shown), 4, shown)
                for a, b in zip(shown, shown[1:]):
                    self.assertGreaterEqual(b["x0"] - a["x1"], 6, (a, b))
                self.assertLessEqual(self.page.evaluate("document.documentElement.scrollWidth"), width)

    def test_renders_on_first_view_then_cleans_up(self) -> None:
        career = "document.querySelector('.career')"
        self.assertIn("career-armed", self.page.evaluate(f"{career}.className"))
        self.page.evaluate("document.querySelector('.career-rows').scrollIntoView({block:'center'})")
        self.page.wait_for_timeout(300)
        self.assertIn("career-drawn", self.page.evaluate(f"{career}.className"))
        self.page.wait_for_timeout(1700)
        self.assertEqual("career", self.page.evaluate(f"{career}.className"))
        state = self.page.evaluate(
            """() => [...document.querySelectorAll('.career-bar')].map(b => [getComputedStyle(b).clipPath, b.style.getPropertyValue('--i')])"""
        )
        self.assertEqual([["none", ""]] * 6, state)


class CareerDarkTest(CareerTest):
    color_scheme = "dark"


class CareerReducedMotionTest(BrowserTestCase):
    reduced_motion = "reduce"

    def test_spans_are_drawn_in_place(self) -> None:
        state = self.page.evaluate(
            """() => ({ cls: document.querySelector('.career').className,
                        clips: [...document.querySelectorAll('.career-bar')].map(b => getComputedStyle(b).clipPath) })"""
        )
        self.assertEqual({"cls": "career", "clips": ["none"] * 6}, state)


class CareerSnapshotTest(unittest.TestCase):
    """With JavaScript off, the inline positions are the whole chart."""

    def test_inline_positions_match_the_snapshot_date(self) -> None:
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        rows = re.findall(
            r'data-start="([\d-]+)" data-end="([\w-]+)".*?class="career-bar [\w-]+" style="left:([\d.]+)%;width:([\d.]+)%"',
            html,
        )
        self.assertEqual(6, len(rows))
        for start, end, left, width in rows:
            with self.subTest(start=start):
                want_left, want_width = span_percent(start, end, SNAPSHOT)
                self.assertAlmostEqual(want_left, float(left), delta=0.01)
                self.assertAlmostEqual(want_width, float(width), delta=0.01)
        axis = re.search(r'<div class="career-axis"[^>]*>(.*?)</div>', html).group(1)
        ticks = re.findall(r'style="left:([\d.]+)%">(\d{4}|now)<', axis)
        self.assertEqual([str(y) for y in range(FIRST_YEAR, SNAPSHOT.year + 1)] + ["now"], [t for _, t in ticks])
        for left, label in ticks:
            day = SNAPSHOT if label == "now" else date(int(label), 1, 1)
            with self.subTest(label=label):
                self.assertAlmostEqual(axis_percent(day, SNAPSHOT), float(left), delta=0.01)


if __name__ == "__main__":
    unittest.main(verbosity=2)
