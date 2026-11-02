"""The Query this page console (v5, Nov 2026).

The console's promise is that its tables are the page: built from the
HTML at load, so a query cannot disagree with what a visitor reads.  The
first tests check that promise against the DOM directly; the rest cover
the query semantics a reader would rely on, the error messages, the
safety of rendering visitor input, and the Trace, Tab, palette, and
deep-link paths.
"""

from __future__ import annotations

import unittest
import urllib.parse

from helpers import BrowserTestCase


# Result rows only: the "No rows matched" placeholder row is not a row.
ROWS = "document.querySelectorAll('#sqlResult tbody tr:not(:has(.sql-empty))').length"
CELLS = """() => [...document.querySelectorAll('#sqlResult tbody tr:not(:has(.sql-empty))')].map(tr =>
    [...tr.cells].filter(c => !c.classList.contains('sql-action')).map(c => c.textContent))"""


class QueryConsoleTest(BrowserTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.page.add_style_tag(content="html{scroll-behavior:auto!important}")

    def run_sql(self, sql: str) -> list[list[str]]:
        self.page.fill("#sqlInput", sql)
        self.page.press("#sqlInput", "Enter")
        return self.page.evaluate(CELLS)

    def status(self) -> str:
        return self.page.inner_text("#sqlStatus")

    def test_opens_with_an_example_already_run(self) -> None:
        self.assertGreater(self.page.evaluate(ROWS), 0)
        self.assertIn("scan writing", self.status())

    def test_table_row_counts_match_the_page(self) -> None:
        rows = {r[0]: int(r[1]) for r in self.run_sql("SHOW TABLES")}
        dom = self.page.evaluate(
            """() => ({
                writing: document.querySelectorAll('#writing .card').length,
                featured: document.querySelectorAll('#featured .slide').length,
                spans: document.querySelectorAll('#trace .trace-row').length,
                roles: document.querySelectorAll('#experience .role-block').length,
                case_files: document.querySelectorAll('#engineering .case').length,
                skills: document.querySelectorAll('#work .chips li').length
            })"""
        )
        for name, count in dom.items():
            with self.subTest(table=name):
                self.assertGreater(count, 0)
                self.assertEqual(count, rows[name])

    def test_values_are_read_from_the_page(self) -> None:
        titles = [r[0] for r in self.run_sql("SELECT title FROM writing")]
        page_titles = self.page.evaluate(
            "[...document.querySelectorAll('#writing .card h3')].map(h => h.textContent.trim())"
        )
        self.assertEqual(page_titles, titles)
        dates = [r[0] for r in self.run_sql("SELECT date FROM featured ORDER BY date")]
        self.assertEqual(["2026-09-30", "2026-10-23", "2026-11-02"], dates)

    def test_grouping_counts_and_sorting(self) -> None:
        result = self.run_sql(
            "SELECT kind, COUNT(*) AS n FROM spans GROUP BY kind ORDER BY n DESC, kind"
        )
        counts = {kind: int(n) for kind, n in result}
        self.assertEqual(7, sum(counts.values()))
        self.assertEqual("featured", result[0][0])
        self.assertIn("group by kind", self.status())

    def test_null_semantics(self) -> None:
        # The current role has no end date: IS NULL finds it, = never does.
        self.assertEqual([["Amazon Advertising"]], self.run_sql("SELECT company FROM roles WHERE end IS NULL"))
        self.assertEqual([], self.run_sql("SELECT company FROM roles WHERE end = NULL"))
        self.assertIn("use IS NULL", self.page.inner_text("#sqlResult .sql-empty"))

    def test_like_is_case_insensitive_and_limit_trims(self) -> None:
        upper = self.run_sql("SELECT name FROM skills WHERE name LIKE '%DATA%'")
        lower = self.run_sql("SELECT name FROM skills WHERE name LIKE '%data%'")
        self.assertEqual(upper, lower)
        self.assertGreater(len(lower), 3)
        self.assertEqual(2, len(self.run_sql("SELECT name FROM skills LIMIT 2")))

    def test_errors_explain_and_suggest(self) -> None:
        cases = {
            "SELECT titel FROM writing": "Did you mean title?",
            "SELECT * FROM writng": "Did you mean writing?",
            "SELECT title, COUNT(*) FROM writing": "GROUP BY",
            "SELECT * FROM writing WHERE outlet = 'TDWI": "never closes",
            "SELECT * FROM writing; DROP TABLE writing": "after the end of the query",
        }
        for sql, expected in cases.items():
            with self.subTest(sql=sql):
                self.run_sql(sql)
                self.assertIn(expected, self.status())
                self.assertIn("sql-error", self.page.get_attribute("#sqlStatus", "class"))
                self.assertEqual(0, self.page.evaluate(ROWS))

    def test_visitor_input_is_never_rendered_as_html(self) -> None:
        payload = "SELECT '<img src=x onerror=window.__pwned=1>' AS x FROM writing LIMIT 1"
        cells = self.run_sql(payload)
        self.assertEqual("<img src=x onerror=window.__pwned=1>", cells[0][0])
        self.run_sql("<img src=x onerror=window.__pwned=1>")
        self.assertEqual(0, self.page.evaluate("document.querySelectorAll('#query img').length"))
        self.assertIsNone(self.page.evaluate("window.__pwned"))

    def test_trace_outlines_the_source_and_back_returns_focus(self) -> None:
        self.run_sql("SELECT label FROM spans WHERE label LIKE 'TDWI%'")
        self.page.click("#sqlResult .sql-row-btn")
        traced = self.page.evaluate("[...document.querySelectorAll('.traced')].map(e => e.textContent)")
        self.assertEqual(1, len(traced))
        self.assertIn("TDWI Upside", traced[0])
        self.assertTrue(self.page.is_visible("#backToQuery"))
        self.page.click("#backToQuery")
        self.assertEqual("sql-row-btn", self.page.evaluate("document.activeElement.className"))

    def test_trace_brings_a_quote_slide_forward(self) -> None:
        self.run_sql("SELECT outlet FROM featured WHERE outlet LIKE 'Informatics%'")
        self.page.click("#sqlResult .sql-row-btn")
        active = self.page.evaluate(
            "[...document.querySelectorAll('#quoteCarousel .slide')].findIndex(s => s.classList.contains('on'))"
        )
        self.assertEqual(2, active)

    def test_tab_completes_and_otherwise_moves_focus(self) -> None:
        self.page.fill("#sqlInput", "SELECT * FROM wr")
        self.page.press("#sqlInput", "End")
        self.page.press("#sqlInput", "Tab")
        self.assertEqual("SELECT * FROM writing ", self.page.input_value("#sqlInput"))
        self.page.press("#sqlInput", "Tab")
        self.assertNotEqual("sqlInput", self.page.evaluate("document.activeElement.id"))

    def test_history_walks_back_and_restores_the_draft(self) -> None:
        self.run_sql("SHOW TABLES")
        self.run_sql("DESCRIBE spans")
        self.page.fill("#sqlInput", "draft")
        self.page.press("#sqlInput", "Home")
        self.page.press("#sqlInput", "ArrowUp")
        self.assertEqual("DESCRIBE spans", self.page.input_value("#sqlInput"))
        self.page.press("#sqlInput", "ArrowDown")
        self.assertEqual("draft", self.page.input_value("#sqlInput"))

    def test_palette_runs_sql(self) -> None:
        self.page.keyboard.press("Control+K")
        self.page.fill("#paletteInput", "select name from skills limit 3")
        first = self.page.inner_text("#paletteList li >> nth=0")
        self.assertTrue(first.startswith("Run SQL:"))
        self.page.keyboard.press("Enter")
        self.assertEqual(3, self.page.evaluate(ROWS))
        self.assertTrue(self.page.evaluate("document.getElementById('palette').hidden"))

    def test_query_is_kept_in_the_url(self) -> None:
        self.run_sql("SELECT name FROM skills LIMIT 1")
        self.assertEqual(
            "#q=" + urllib.parse.quote("SELECT name FROM skills LIMIT 1", safe="*'()"),
            self.page.evaluate("location.hash"),
        )


class QueryDeepLinkTest(BrowserTestCase):
    page_suffix = "#q=" + urllib.parse.quote("SELECT company FROM roles ORDER BY months DESC LIMIT 2")

    def test_deep_link_runs_on_arrival(self) -> None:
        self.assertEqual(
            "SELECT company FROM roles ORDER BY months DESC LIMIT 2",
            self.page.input_value("#sqlInput"),
        )
        self.assertEqual(2, self.page.evaluate(ROWS))


class QueryPhoneTest(BrowserTestCase):
    viewport = {"width": 360, "height": 800}

    def test_wide_results_scroll_inside_their_box(self) -> None:
        self.page.fill("#sqlInput", "SELECT * FROM featured")
        self.page.press("#sqlInput", "Enter")
        widths = self.page.evaluate(
            """() => ({
                doc: document.documentElement.scrollWidth,
                body: document.body.scrollWidth,
                inner: document.getElementById('sqlResult').scrollWidth,
                box: document.getElementById('sqlResult').clientWidth
            })"""
        )
        self.assertLessEqual(widths["doc"], 361)
        self.assertLessEqual(widths["body"], 361)
        self.assertGreater(widths["inner"], widths["box"])
        # Dates stay on one line instead of breaking mid-value. A Range
        # over the cell's text returns one client rect per line box.
        lines = self.page.evaluate(
            """() => [...document.querySelectorAll('#sqlResult td.sql-date')].map(td => {
                const r = document.createRange();
                r.selectNodeContents(td);
                return r.getClientRects().length;
            })"""
        )
        self.assertEqual([1, 1, 1], lines)

    def test_header_stays_compact(self) -> None:
        height = self.page.evaluate("document.querySelector('.site-header').offsetHeight")
        self.assertLessEqual(height, 100)


if __name__ == "__main__":
    unittest.main(verbosity=2)
