"""Featured quote carousel behaviour and accessibility state.

Since Nov 6, 2026 each slide leads with the article: the publisher
masthead, the date, and the headline. The quote itself waits behind
"Read my quote", a native <details>. The owner asked for this because the
quote cards, with his name and title on every slide, were too much.
"""

from __future__ import annotations

import unittest

from helpers import BrowserTestCase


# Every slide in order: its headline, and the quote word for word as
# published, spelling included ("favour", "prioritise"). These are the
# quotes the slides' screenshots and quote cards showed before Nov 6, 2026.
SLIDES = [
    (
        "EU AI Act: Training Data Requirements in 2026",
        "In practice, most teams have a labeling pipeline and a policy document, but no lineage. "
        "They can't tell you where a given training row came from, what transformations it went "
        "through, or whether the distribution that produced it has drifted since. A policy on "
        "paper and a safeguard inside the pipeline are not the same thing.",
    ),
    (
        "Golden Dataset: How to Build Trusted AI Evaluation Data",
        "A golden dataset is one whose lineage is auditable and whose behavior is continuously "
        "validated against the world it claims to represent. If you can't reconstruct how a "
        "dataset was built or detect when it stops matching production reality, the label "
        "accuracy is decoration.",
    ),
    (
        "How Data Teams Balance Access and Privacy",
        "Take one defect - a column renamed by an upstream team, or the loss of 20% of a day's "
        "events due to partial outages.",
    ),
    (
        "How Analytics Teams Turn Data Into Everyday Decisions",
        "A dashboard becomes part of regular decisions when it stops being a place people visit "
        "and starts showing up where the decision already happens.",
    ),
    (
        "How Software Leaders Make Room for Technical Debt",
        "Technical debt gets roadmap space on our team because we stopped asking for it as a "
        "favour and started planning it as a category.",
    ),
    (
        "How Software Product Teams Prioritize Customer Requests",
        "We prioritise the roadmap by asking what each item makes possible, and what waiting costs.",
    ),
]

SLIDE_STATE = """() => [...document.querySelectorAll('#quoteCarousel .slide')].map(s => {
    const link = s.querySelector('figcaption .slide-title a');
    const quote = s.querySelector('details.slide-quote blockquote');
    return {
        title: link ? link.textContent.trim() : null,
        href: link ? link.href : null,
        cite: quote ? quote.cite : null,
        quote: quote ? quote.textContent.trim() : null,
        open: !!s.querySelector('details.slide-quote[open]'),
        pictures: [...s.querySelectorAll('img')].filter(i => !i.classList.contains('pub-logo')).length,
        text: s.textContent
    };
})"""
ACTIVE = "[...document.querySelectorAll('#quoteCarousel .slide')].findIndex(s => s.classList.contains('on'))"
TRACK_HEIGHT = "Math.round(document.querySelector('#quoteCarousel .carousel-track').getBoundingClientRect().height)"


class CarouselTest(BrowserTestCase):
    def test_dots_track_the_active_slide_and_next_advances(self) -> None:
        carousel = self.page.locator("#quoteCarousel")
        carousel.scroll_into_view_if_needed()

        dots_wrap = carousel.locator(".carousel-dots")
        dots = carousel.locator(".carousel-dot")
        slides = carousel.locator(".slide")

        self.assertEqual("group", dots_wrap.get_attribute("role"))
        # 6 slides since Nov 4, 2026: the two Label Your Data quotes,
        # two Informatics Magazine quotes, the CTO Sync quote, and the
        # Tech Magazine quote.
        self.assertEqual(6, dots.count())
        self.assertEqual(6, slides.count())
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


class HeadlineFirstTest(BrowserTestCase):
    """Each slide leads with the article; its quote opens on request."""

    # Hold the slides still: these tests are about what a slide shows.
    reduced_motion = "reduce"

    def setUp(self) -> None:
        super().setUp()
        self.page.add_style_tag(content="html{scroll-behavior:auto!important}")
        self.page.evaluate("document.getElementById('quoteCarousel').scrollIntoView({block:'center'})")

    def summary_text(self) -> str:
        return self.page.inner_text("#quoteCarousel .slide.on summary").strip()

    def quote_visible(self) -> bool:
        return self.page.is_visible("#quoteCarousel .slide.on blockquote")

    def test_slides_lead_with_the_headline_and_no_picture_of_the_quote(self) -> None:
        slides = self.page.evaluate(SLIDE_STATE)
        self.assertEqual([title for title, _ in SLIDES], [s["title"] for s in slides])
        for s in slides:
            with self.subTest(title=s["title"]):
                # The headline links to the article the quote cites.
                self.assertTrue(s["href"].startswith("https://"))
                self.assertEqual(s["href"], s["cite"])
                # No screenshot or quote card: the only image is the logo.
                self.assertEqual(0, s["pictures"])
                # His name and title are not repeated on every slide.
                self.assertNotIn("Kaithapuram", s["text"])
                self.assertNotIn("Software Development Engineer", s["text"])
                # Every quote starts closed.
                self.assertFalse(s["open"])
        self.assertEqual("Read my quote", self.summary_text())
        self.assertFalse(self.quote_visible())

    def test_every_quote_is_word_for_word_as_published(self) -> None:
        quotes = [s["quote"] for s in self.page.evaluate(SLIDE_STATE)]
        self.assertEqual([quote for _, quote in SLIDES], quotes)

    def test_read_my_quote_opens_and_closes_the_quote(self) -> None:
        self.page.click("#quoteCarousel .slide.on summary")
        self.assertTrue(self.quote_visible())
        self.assertEqual("Hide quote", self.summary_text())
        self.assertEqual(SLIDES[0][1], self.page.inner_text("#quoteCarousel .slide.on blockquote").strip("“” \n"))
        self.page.click("#quoteCarousel .slide.on summary")
        self.assertFalse(self.quote_visible())
        self.assertEqual("Read my quote", self.summary_text())

    def test_the_keyboard_reaches_only_the_active_slide(self) -> None:
        # Off-stage slides are inert, so Tab goes from the active slide's
        # headline to its toggle and then to the arrows, never into a
        # slide that is not showing.
        self.assertEqual(
            [False, True, True, True, True, True],
            self.page.evaluate("[...document.querySelectorAll('#quoteCarousel .slide')].map(s => s.inert)"),
        )
        self.page.focus("#quoteCarousel .slide.on .slide-title a")
        self.page.keyboard.press("Tab")
        self.assertEqual("SUMMARY", self.page.evaluate("document.activeElement.tagName"))
        self.assertTrue(self.page.evaluate("document.activeElement.closest('.slide').classList.contains('on')"))
        self.page.keyboard.press("Enter")
        self.assertTrue(self.quote_visible())
        self.page.keyboard.press("Enter")
        self.assertFalse(self.quote_visible())
        self.page.keyboard.press("Tab")
        self.assertEqual("quotePrev", self.page.evaluate("document.activeElement.id"))

        # The next slide becomes the only reachable one.
        self.page.click("#quoteNext")
        self.assertEqual(
            [True, False, True, True, True, True],
            self.page.evaluate("[...document.querySelectorAll('#quoteCarousel .slide')].map(s => s.inert)"),
        )

    def test_moving_on_closes_the_quote_and_the_stage_settles(self) -> None:
        closed = self.page.evaluate(TRACK_HEIGHT)
        self.page.click("#quoteCarousel .slide.on summary")
        self.assertGreater(self.page.evaluate(TRACK_HEIGHT), closed)
        self.page.click("#quoteNext")
        self.assertEqual([False] * 6, [s["open"] for s in self.page.evaluate(SLIDE_STATE)])
        self.assertEqual(closed, self.page.evaluate(TRACK_HEIGHT))
        self.page.click("#quotePrev")
        self.assertEqual("Read my quote", self.summary_text())


class QuoteHoldsTheSlideTest(BrowserTestCase):
    """With motion on, an open quote stops the carousel moving on."""

    def test_an_open_quote_holds_its_slide(self) -> None:
        self.page.add_style_tag(content="html{scroll-behavior:auto!important}")
        self.page.evaluate("document.getElementById('quoteCarousel').scrollIntoView({block:'center'})")
        self.page.click("#quoteCarousel .slide.on summary")
        # Leave the carousel, so neither hover nor focus is what holds it.
        self.page.mouse.move(2, 2)
        self.page.evaluate("document.activeElement.blur()")
        self.page.wait_for_timeout(5600)
        self.assertEqual(0, self.page.evaluate(ACTIVE))
        self.assertTrue(self.page.is_visible("#quoteCarousel .slide.on blockquote"))
        # Closed again, the carousel moves on as before.
        self.page.evaluate("document.querySelector('#quoteCarousel .slide.on details').open = false")
        self.page.wait_for_function(f"({ACTIVE}) === 1", timeout=6500)


class PrintTest(BrowserTestCase):
    """A printed page carries every quote, and printing changes nothing."""

    reduced_motion = "reduce"

    def test_every_quote_prints_and_the_page_is_restored_after(self) -> None:
        # The visitor has the first quote open before printing.
        self.page.evaluate("document.querySelector('#quoteCarousel .slide.on details').open = true")
        self.page.emulate_media(media="print")
        self.page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
        printed = self.page.evaluate(
            # checkVisibility(), not the box: the content of a closed
            # <details> keeps its layout box but is not rendered.
            """() => [...document.querySelectorAll('#quoteCarousel .slide')].map(s => ({
                quote: s.querySelector('blockquote').checkVisibility(),
                toggle: getComputedStyle(s.querySelector('summary')).display
            }))"""
        )
        self.assertEqual([{"quote": True, "toggle": "none"}] * 6, printed)
        self.page.evaluate("window.dispatchEvent(new Event('afterprint'))")
        self.page.emulate_media(media="screen")
        self.assertEqual(
            [True, False, False, False, False, False],
            [s["open"] for s in self.page.evaluate(SLIDE_STATE)],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
