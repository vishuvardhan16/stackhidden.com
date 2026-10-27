"""Theme behaviour: initial render, toggle, and local persistence."""

from __future__ import annotations

import unittest

from helpers import BrowserTestCase


class ThemeTest(BrowserTestCase):
    # Pin the browser's colour-scheme preference so the site's documented
    # default (dark unless the visitor prefers light) is deterministic.
    color_scheme = "dark"

    def test_default_theme_renders(self) -> None:
        self.assertEqual(
            "dark", self.page.locator("html").get_attribute("data-theme")
        )
        self.assertTrue(self.page.locator("h1").is_visible())
        background = self.page.evaluate(
            "() => getComputedStyle(document.body).backgroundImage"
        )
        self.assertIn("linear-gradient", background)

    def test_toggle_flips_theme_and_persists_across_reload(self) -> None:
        initial = self.page.locator("html").get_attribute("data-theme")
        self.page.click("#theme-toggle")
        self.page.wait_for_function(
            "expected => document.documentElement.getAttribute('data-theme') === expected",
            arg="light" if initial == "dark" else "dark",
        )

        flipped = self.page.locator("html").get_attribute("data-theme")
        self.assertNotEqual(initial, flipped)
        self.assertEqual(
            flipped,
            self.page.evaluate("() => localStorage.getItem('theme')"),
        )

        self.reload_page()
        self.assertEqual(
            flipped, self.page.locator("html").get_attribute("data-theme")
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
