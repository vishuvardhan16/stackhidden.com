"""Featured quote carousel behaviour and accessibility state."""

from __future__ import annotations

import unittest

from helpers import BrowserTestCase


class CarouselTest(BrowserTestCase):
    def test_dots_track_the_active_slide_and_next_advances(self) -> None:
        carousel = self.page.locator("#quoteCarousel")
        carousel.scroll_into_view_if_needed()

        dots_wrap = carousel.locator(".carousel-dots")
        dots = carousel.locator(".carousel-dot")
        slides = carousel.locator(".slide")

        self.assertEqual("group", dots_wrap.get_attribute("role"))
        self.assertEqual(2, dots.count())
        self.assertEqual(2, slides.count())
        self.assertEqual("true", dots.nth(0).get_attribute("aria-current"))
        self.assertIsNone(dots.nth(1).get_attribute("aria-current"))
        self.assertIn("on", slides.nth(0).get_attribute("class") or "")
        self.assertEqual("false", slides.nth(0).get_attribute("aria-hidden"))

        self.page.click("#quoteNext")

        self.assertEqual("true", dots.nth(1).get_attribute("aria-current"))
        self.assertIsNone(dots.nth(0).get_attribute("aria-current"))
        self.assertIn("on", slides.nth(1).get_attribute("class") or "")
        self.assertNotIn("on", (slides.nth(0).get_attribute("class") or "").split())
        self.assertEqual("false", slides.nth(1).get_attribute("aria-hidden"))
        self.assertEqual("true", slides.nth(0).get_attribute("aria-hidden"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
