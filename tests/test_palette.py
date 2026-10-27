"""Command palette behaviour."""

from __future__ import annotations

import unittest

from helpers import BrowserTestCase


class PaletteTest(BrowserTestCase):
    def test_ctrl_k_opens_a_populated_palette_and_escape_closes_it(self) -> None:
        palette = self.page.locator("#palette")
        self.assertTrue(palette.evaluate("element => element.hidden"))

        self.page.keyboard.press("Control+K")
        self.page.wait_for_selector("#paletteList li")
        self.assertTrue(palette.is_visible())
        self.assertFalse(palette.evaluate("element => element.hidden"))

        labels = self.page.locator("#paletteList li span").all_text_contents()
        self.assertEqual(16, len(labels))
        self.assertIn("Go to About", labels)
        self.assertIn("Case file: Custom Brands (ICM)", labels)
        self.assertIn("Toggle light / dark theme", labels)
        self.assertEqual(
            "paletteInput",
            self.page.evaluate("() => document.activeElement.id"),
        )

        self.page.keyboard.press("Escape")
        self.page.wait_for_function(
            "() => document.getElementById('palette').hidden"
        )
        self.assertFalse(palette.is_visible())


if __name__ == "__main__":
    unittest.main(verbosity=2)
