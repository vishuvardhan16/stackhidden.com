"""Responsive layout checks at phone, tablet, and desktop widths."""

from __future__ import annotations

import unittest

from helpers import BrowserTestCase


class LayoutTest(BrowserTestCase):
    def test_no_horizontal_overflow_and_key_hero_content_is_visible(
        self,
    ) -> None:
        viewports = [
            (360, 800),
            (768, 1024),
            (1400, 900),
        ]
        for width, height in viewports:
            with self.subTest(width=width, height=height):
                self.page.set_viewport_size({"width": width, "height": height})
                self.reload_page()

                metrics = self.page.evaluate(
                    """() => ({
                        innerWidth: window.innerWidth,
                        documentWidth: document.documentElement.scrollWidth,
                        bodyWidth: document.body.scrollWidth
                    })"""
                )
                self.assertLessEqual(metrics["documentWidth"], width + 1)
                self.assertLessEqual(metrics["bodyWidth"], width + 1)
                self.assertEqual(width, metrics["innerWidth"])

                figure = self.page.locator(".hero-figure")
                figure.scroll_into_view_if_needed()
                self.assertTrue(figure.is_visible())
                box = figure.bounding_box()
                self.assertIsNotNone(box)
                self.assertGreater(box["width"], 0)
                self.assertLessEqual(box["width"], width)

                note = self.page.locator(".featured-note")
                note.scroll_into_view_if_needed()
                self.assertTrue(note.is_visible())
                self.assertIn("Karyna Naminas", note.inner_text())


if __name__ == "__main__":
    unittest.main(verbosity=2)
