"""Published Writing carousel behaviour and accessibility state.

Since Nov 20, 2026 Published Writing is a carousel like Featured In,
at the owner's request: one article per slide, auto-advancing every
5 seconds, with arrows (and dots until Nov 26, 2026, when a counter
replaced them), run by the same initializer as the quote carousel. The build-log card is not an article, so it stays
below the carousel as a plain card and is not a slide.
"""

from __future__ import annotations

import unittest

from helpers import BrowserTestCase


# Every article, oldest first: its title and its live link. The carousel
# shows them newest first since Nov 26, 2026 (SHOWN).
SLIDES = [
    (
        "From Reactive to Proactive: Automating Data Quality in Petabyte-Scale Analytics Pipelines",
        "https://tdwi.org/articles/2026/07/08/diq-all-automating-data-quality-in-petabytescale-analytics-pipelines.aspx",
    ),
    (
        "Batch to Streaming: What Actually Breaks and When It's Worth It",
        "https://roundtable.ailovesdata.com/batch-to-streaming-what-actually-breaks-and-when-its-worth-it",
    ),
    (
        "Building Advertiser Analytics in a Post-Identifier World",
        "https://www.exchangewire.com/blog/2026/08/27/building-advertiser-analytics-in-a-post-identifier-world/",
    ),
    (
        "The Agent Is a Workload: What Platform Teams Should Demand Before One Ships",
        "https://platformengineering.com/contributed-content/the-agent-is-a-workload-what-platform-teams-should-demand-before-one-ships/",
    ),
    (
        "Your Agent Is an API Client. Defend It Like One",
        "https://www.esecurityplanet.com/agentic-ai/your-agent-is-an-api-client-defend-it-like-one/",
    ),
    (
        "Your Agent's Tool Calls Will Run Twice: Idempotency and Evaluation Gates in Java Services",
        "https://foojay.io/today/agent-tool-calls-run-twice/",
    ),
    (
        "What Needs to Be in Place Before an Agent Answers the Customer",
        "https://www.destinationcrm.com/Articles/Web-Exclusives/Viewpoints/What-Needs-to-Be-in-Place-Before-an-Agent-Answers-the-Customer-177606.aspx",
    ),
]
SHOWN = SLIDES[::-1]

SLIDE_STATE = """() => [...document.querySelectorAll('#writingCarousel .slide')].map(s => {
    const link = s.querySelector('p:last-child a');
    return {
        title: s.querySelector('h3') ? s.querySelector('h3').textContent.trim() : null,
        href: link ? link.href : null,
        date: s.querySelector('.pub-date') ? s.querySelector('.pub-date').textContent.trim() : null,
        outlet: s.querySelector('.pub-name') ? s.querySelector('.pub-name').textContent.trim() : null,
    };
})"""
ACTIVE = "[...document.querySelectorAll('#writingCarousel .slide')].findIndex(s => s.classList.contains('on'))"


# The counter as a sighted visitor sees it: everything but the
# screen-reader words ("Quote", "of").
COUNT_SHOWN = """() => { const c = document.querySelector('#writingCarousel .carousel-count');
    return [...c.childNodes].filter(n => !(n.classList && n.classList.contains('sr-only'))).map(n => n.textContent).join('').replace(/\\s+/g, ' ').trim(); }"""

class WritingCarouselTest(BrowserTestCase):
    def test_the_counter_tracks_the_active_slide_and_next_advances(self) -> None:
        carousel = self.page.locator("#writingCarousel")
        carousel.scroll_into_view_if_needed()

        slides = carousel.locator(".slide")

        # 7 slides: the four November articles and the three
        # July-August articles, newest first.
        self.assertEqual(7, slides.count())
        self.assertEqual("1 / 7", self.page.evaluate(COUNT_SHOWN))
        self.assertIn("on", slides.nth(0).get_attribute("class") or "")
        self.assertEqual("false", slides.nth(0).get_attribute("aria-hidden"))

        self.page.click("#writingNext")

        self.assertEqual("2 / 7", self.page.evaluate(COUNT_SHOWN))
        self.assertIn("on", slides.nth(1).get_attribute("class") or "")
        self.assertNotIn("on", (slides.nth(0).get_attribute("class") or "").split())
        self.assertEqual("false", slides.nth(1).get_attribute("aria-hidden"))
        self.assertEqual("true", slides.nth(0).get_attribute("aria-hidden"))

    def test_slides_carry_the_articles_newest_first_with_live_links(self) -> None:
        slides = self.page.evaluate(SLIDE_STATE)
        self.assertEqual([title for title, _ in SHOWN], [s["title"] for s in slides])
        self.assertEqual(
            ["November 20, 2026", "November 19, 2026", "November 9, 2026", "November 9, 2026",
             "August 27, 2026", "August 25, 2026", "July 8, 2026"],
            [s["date"] for s in slides],
        )
        for s, (_, href) in zip(slides, SHOWN):
            with self.subTest(title=s["title"]):
                self.assertEqual(href, s["href"])
        # The build-log card is not a slide.
        self.assertEqual(
            ["stackhidden.com"],
            self.page.evaluate(
                "[...document.querySelectorAll('#writing .cards .card .pub-name')].map(n => n.textContent.trim())"
            ),
        )

    def test_the_keyboard_reaches_only_the_active_slide(self) -> None:
        # Off-stage slides are inert, so Tab goes from the active
        # slide's link to the arrows, never into a slide that is not
        # showing.
        self.assertEqual(
            [False, True, True, True, True, True, True],
            self.page.evaluate("[...document.querySelectorAll('#writingCarousel .slide')].map(s => s.inert)"),
        )
        self.page.focus("#writingCarousel .slide.on p:last-child a")
        self.page.keyboard.press("Tab")
        self.assertEqual("writingPrev", self.page.evaluate("document.activeElement.id"))

        # The next slide becomes the only reachable one.
        self.page.click("#writingNext")
        self.assertEqual(
            [True, False, True, True, True, True, True],
            self.page.evaluate("[...document.querySelectorAll('#writingCarousel .slide')].map(s => s.inert)"),
        )


class WritingAutoAdvanceTest(BrowserTestCase):
    """With motion on, the writing carousel moves on every 5 seconds."""

    def test_the_carousel_advances_on_its_own(self) -> None:
        self.page.add_style_tag(content="html{scroll-behavior:auto!important}")
        self.page.evaluate("document.getElementById('writingCarousel').scrollIntoView({block:'center'})")
        # Leave the carousel, so neither hover nor focus is what moves it.
        self.page.mouse.move(2, 2)
        self.page.evaluate("document.activeElement.blur()")
        self.assertEqual(0, self.page.evaluate(ACTIVE))
        self.page.wait_for_timeout(5600)
        self.assertEqual(1, self.page.evaluate(ACTIVE))
