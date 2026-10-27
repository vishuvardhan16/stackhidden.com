"""Engineering case files: in-place opening and deep links."""

from __future__ import annotations

import unittest

from helpers import BrowserTestCase


CASE_IDS = [
    "case-orchestration",
    "case-insights-api",
    "case-icm",
    "case-mosaic",
]


class CaseFilesTest(BrowserTestCase):
    def test_each_case_file_opens_and_closes_in_place(self) -> None:
        self.assertEqual(4, self.page.locator("article.case").count())

        for case_id in CASE_IDS:
            with self.subTest(case_id=case_id):
                article = self.page.locator(f"#{case_id}")
                body = article.locator(".case-body")
                toggle = article.locator(".case-toggle")

                self.assertFalse(body.is_visible())
                self.assertEqual("false", toggle.get_attribute("aria-expanded"))

                toggle.scroll_into_view_if_needed()
                toggle.click()
                self.assertTrue(body.is_visible())
                self.assertEqual("true", toggle.get_attribute("aria-expanded"))
                self.assertEqual("Close case file", toggle.inner_text())

                toggle.click()
                self.assertFalse(body.is_visible())
                self.assertEqual("false", toggle.get_attribute("aria-expanded"))


class ICMDeepLinkTest(BrowserTestCase):
    page_suffix = "#case=icm"

    def test_icm_deep_link_opens_only_the_icm_case(self) -> None:
        self.page.wait_for_function(
            "() => !document.querySelector('#case-icm .case-body').hidden"
        )
        for case_id in CASE_IDS:
            body = self.page.locator(f"#{case_id} .case-body")
            if case_id == "case-icm":
                self.assertTrue(body.is_visible())
            else:
                self.assertFalse(body.is_visible())


if __name__ == "__main__":
    unittest.main(verbosity=2)
