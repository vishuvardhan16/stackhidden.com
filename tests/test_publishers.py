"""Publisher mastheads and the Featured carousel's sizing (v5, Nov 2026).

Published Writing, Speaking, and the Featured In captions share one
masthead: publisher name, a pill for the kind of piece, then the date,
with a logo slot the owner fills with official files.  These tests pin
the structure, the logo slot's behaviour, the date order of the writing,
the aligned links, and that no caption ever runs under the carousel's
controls at any width.
"""

from __future__ import annotations

import re
import unittest

from helpers import BrowserTestCase


# A neutral grey bar, standing in for a logo file in tests. It is not any
# publisher's mark.
PLACEHOLDER = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' "
    "height='24'%3E%3Crect width='120' height='24' fill='%2394a3b8'/%3E%3C/svg%3E"
)
INSERT_LOGO = """(src) => {
    const slot = document.querySelector('#writing .pub-mark');
    const img = document.createElement('img');
    img.className = 'pub-logo'; img.src = src; img.alt = ''; img.width = 120; img.height = 24;
    slot.textContent = ''; slot.appendChild(img);
}"""
CAPTION_GAPS = """() => {
    const controls = document.querySelector('#quoteCarousel .carousel-controls').getBoundingClientRect();
    return [...document.querySelectorAll('#quoteCarousel .slide figcaption')]
        .map(c => controls.top - c.getBoundingClientRect().bottom);
}"""


class MastheadTest(BrowserTestCase):
    def test_every_entry_opens_with_a_masthead(self) -> None:
        heads = self.page.evaluate(
            """() => [...document.querySelectorAll('#writing .card, #speaking .talk, #featured figcaption')].map(el => ({
                name: (el.querySelector('.pub-name') || {}).textContent,
                kind: (el.querySelector('.pub-kind') || {}).textContent,
                slot: !!el.querySelector('.pub-mark')
            }))"""
        )
        self.assertEqual(4 + 2 + 5, len(heads))
        for head in heads:
            with self.subTest(head=head):
                self.assertTrue(head["name"] and head["kind"] and head["slot"])

    def test_empty_logo_slots_stay_collapsed_and_request_nothing(self) -> None:
        # Holds before and after the owner adds real logos: a slot without
        # an <img> is collapsed, and every logo file the page asks for
        # belongs to an <img> in a slot. (A logo file that is missing
        # fails the suite anyway: helpers.py treats the browser's 404
        # console error as a failure.)
        open_empty = self.page.evaluate(
            "[...document.querySelectorAll('.pub-mark')].filter(m => !m.querySelector('img') && getComputedStyle(m).display !== 'none').length"
        )
        self.assertEqual(0, open_empty)
        state = self.page.evaluate(
            """() => ({
                requested: performance.getEntriesByType('resource').map(r => r.name).filter(n => n.includes('/assets/logos/')),
                declared: [...document.querySelectorAll('.pub-mark img')].map(i => i.src)
            })"""
        )
        for url in state["requested"]:
            with self.subTest(url=url):
                self.assertIn(url, state["declared"])

    def test_cto_sync_caption_shows_its_official_logo(self) -> None:
        # CTO Sync's slot was filled on Nov 3, 2026 with the official
        # file from ctosync.com's site header (assets/logos/ctosync.svg),
        # so the fifth Featured caption carries that logo with an empty
        # alt, like every other filled slot.
        state = self.page.evaluate(
            """() => {
                const caps = [...document.querySelectorAll('#featured figcaption')];
                const img = caps[caps.length - 1].querySelector('.pub-mark img');
                return img ? { src: img.getAttribute('src'), alt: img.getAttribute('alt'),
                               width: img.getAttribute('width'), height: img.getAttribute('height') } : null;
            }"""
        )
        self.assertEqual(
            {"src": "assets/logos/ctosync.svg", "alt": "", "width": "105", "height": "24"},
            state,
        )

    def test_a_logo_replaces_the_name_visually_but_not_for_screen_readers(self) -> None:
        self.page.evaluate(INSERT_LOGO, PLACEHOLDER)
        state = self.page.evaluate(
            """() => {
                const card = document.querySelector('#writing .card');
                const name = card.querySelector('.pub-name');
                return { clip: getComputedStyle(name).clip, width: name.getBoundingClientRect().width,
                         text: card.textContent.includes('TDWI Upside'),
                         logo: card.querySelector('.pub-logo').getBoundingClientRect().height };
            }"""
        )
        self.assertEqual("rect(0px, 0px, 0px, 0px)", state["clip"])
        self.assertLessEqual(state["width"], 1)
        self.assertTrue(state["text"])
        self.assertGreater(state["logo"], 20)

    def test_writing_runs_in_date_order(self) -> None:
        dates = self.page.evaluate(
            "[...document.querySelectorAll('#writing .pub-date')].map(d => d.textContent.trim())"
        )
        months = ["January", "February", "March", "April", "May", "June", "July",
                  "August", "September", "October", "November", "December"]

        def key(text: str) -> tuple[int, int]:
            m = re.search(r"([A-Z][a-z]+) (\d+)?,? ?(\d{4})", text)
            return (months.index(m.group(1)), int(m.group(2) or 0))

        self.assertEqual(sorted(dates, key=key), dates)

    def test_closing_links_line_up_across_a_row(self) -> None:
        bottoms = self.page.evaluate(
            "[...document.querySelectorAll('#writing .pub-card')].slice(0, 3).map(c => Math.round(c.lastElementChild.getBoundingClientRect().bottom))"
        )
        self.assertEqual(1, len(set(bottoms)), bottoms)

    def test_console_tables_read_the_mastheads(self) -> None:
        def column(sql: str) -> list[str]:
            self.page.fill("#sqlInput", sql)
            self.page.press("#sqlInput", "Enter")
            return self.page.evaluate(
                "[...document.querySelectorAll('#sqlResult tbody tr')].map(tr => tr.cells[0].textContent)"
            )

        self.assertEqual(["TDWI Upside", "AI Loves Data", "ExchangeWire", "stackhidden.com"], column("SELECT outlet FROM writing"))
        self.assertEqual(["Marketplace Risk", "NICE-TEAS ASIA 2026"], column("SELECT venue FROM talks"))
        self.assertEqual(["delivered", "upcoming"], column("SELECT status FROM talks"))
        self.assertEqual(
            ["EU AI Act: Training Data Requirements in 2026", "Golden Dataset: How to Build Trusted AI Evaluation Data",
             "How Data Teams Balance Access and Privacy", "How Analytics Teams Turn Data Into Everyday Decisions",
             "How Software Leaders Make Room for Technical Debt"],
            column("SELECT title FROM featured"),
        )


class DarkLogoPlateTest(BrowserTestCase):
    color_scheme = "dark"

    def test_logos_sit_on_a_light_plate_in_dark_mode(self) -> None:
        self.page.evaluate(INSERT_LOGO, PLACEHOLDER)
        self.assertEqual(
            "rgb(255, 255, 255)",
            self.page.evaluate("getComputedStyle(document.querySelector('.pub-logo')).backgroundColor"),
        )


class CarouselFitTest(BrowserTestCase):
    def test_captions_never_run_under_the_controls(self) -> None:
        for width, height in ((360, 800), (768, 1024), (1400, 900)):
            with self.subTest(width=width):
                self.page.set_viewport_size({"width": width, "height": height})
                self.reload_page()
                gaps = self.page.evaluate(CAPTION_GAPS)
                self.assertEqual(5, len(gaps))
                self.assertTrue(all(g >= 8 for g in gaps), gaps)


if __name__ == "__main__":
    unittest.main(verbosity=2)
