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

                # The first slide is a Label Your Data article; its
                # byline credits the author at every width, inside the
                # slide. One synchronous call, so the carousel's timer
                # cannot move to the next slide between the click and the
                # measurement (the next slide carries the same byline,
                # which would hide a missing one).
                byline = self.page.evaluate(
                    """() => {
                        document.querySelectorAll('#quoteCarousel .carousel-dot')[0].click();
                        const slide = document.querySelector('#quoteCarousel .slide.on');
                        const b = slide.querySelector('.byline');
                        if (!b) return null;
                        const r = b.getBoundingClientRect();
                        return { text: b.innerText.toLowerCase(), width: r.width,
                                 inside: r.right <= slide.getBoundingClientRect().right + 0.5 };
                    }"""
                )
                self.assertIsNotNone(byline)
                self.assertEqual("by karyna naminas", byline["text"])
                self.assertGreater(byline["width"], 0)
                self.assertTrue(byline["inside"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
