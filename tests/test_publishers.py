"""Publisher mastheads and the Featured carousel's sizing (v5, Nov 2026).

Published Writing, Speaking, and the Featured In captions share one
masthead: publisher name, a pill for the kind of piece, then the date,
with a logo slot the owner fills with official files.  These tests pin
the structure, the logo slot's behaviour, the date order of the writing,
the aligned links, and that no caption, and no open quote, ever runs
under the carousel's controls at any width.
"""

from __future__ import annotations

import base64
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
OPEN_QUOTE_GAP = """() => {
    const controls = document.querySelector('#quoteCarousel .carousel-controls').getBoundingClientRect();
    return controls.top - document.querySelector('#quoteCarousel .slide.on blockquote').getBoundingClientRect().bottom;
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
        self.assertEqual(4 + 2 + 6, len(heads))
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
        # alt, like every other filled slot. The file carries empty
        # canvas either side of a compact mark, so style.css frames it
        # to its artwork at --h:34px in a 2:1 box, and it declares 68 by
        # 34, the shape it is shown at (Nov 4, 2026). A sixth
        # caption (Tech Magazine) joined on Nov 4, 2026, so this test
        # now reads the fifth caption rather than the last.
        state = self.page.evaluate(
            """() => {
                const caps = [...document.querySelectorAll('#featured figcaption')];
                const img = caps[4].querySelector('.pub-mark img');
                return img ? { src: img.getAttribute('src'), alt: img.getAttribute('alt'),
                               width: img.getAttribute('width'), height: img.getAttribute('height') } : null;
            }"""
        )
        self.assertEqual(
            {"src": "assets/logos/ctosync.svg", "alt": "", "width": "68", "height": "34"},
            state,
        )

    def test_tech_magazine_caption_shows_its_official_logo(self) -> None:
        # Tech Magazine's slot was filled on Nov 4, 2026 with the
        # publisher's official header artwork. The header file is an
        # SVG export of roughly 1 MB carrying an embedded raster
        # image, so the caption carries a transparent PNG rendered
        # from that official file (assets/logos/techmagazine.png,
        # scaled to 403x84, three times its shown height) instead, per
        # the PNG route in
        # docs/publisher-logos.md. Its declared size follows the v5
        # logo system (--h:28px in style.css), so it declares 134 by
        # 28, the file's proportions at that height.
        state = self.page.evaluate(
            """() => {
                const caps = [...document.querySelectorAll('#featured figcaption')];
                const img = caps[caps.length - 1].querySelector('.pub-mark img');
                return img ? { src: img.getAttribute('src'), alt: img.getAttribute('alt'),
                               width: img.getAttribute('width'), height: img.getAttribute('height') } : null;
            }"""
        )
        self.assertEqual(
            {"src": "assets/logos/techmagazine.png", "alt": "", "width": "134", "height": "28"},
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
             "How Software Leaders Make Room for Technical Debt", "How Software Product Teams Prioritize Customer Requests"],
            column("SELECT title FROM featured"),
        )


ROWS = """() => {
    const out = {};
    for (const [sec, n] of [['writing', 3], ['speaking', 2]]) {
        const cards = [...document.querySelectorAll('#' + sec + ' .pub-card')].slice(0, n);
        out[sec] = {
            heads: cards.map(c => Math.round(c.querySelector('.pub-head').getBoundingClientRect().height)),
            dates: cards.map(c => Math.round(c.querySelector('.pub-date').getBoundingClientRect().top)),
            box: parseFloat(getComputedStyle(document.getElementById(sec)).getPropertyValue('--logo-box'))
        };
    }
    return out;
}"""
VISIBLE_LOGOS = """() => [...document.querySelectorAll('.pub-logo')]
    .filter(i => getComputedStyle(i).display !== 'none')
    .map(i => ({
        src: i.getAttribute('src'),
        loaded: i.complete && i.naturalWidth > 0,
        h: getComputedStyle(i).getPropertyValue('--h').trim(),
        bg: getComputedStyle(i).backgroundColor,
        height: Math.round(i.getBoundingClientRect().height),
        box: parseFloat(getComputedStyle(i.closest('section')).getPropertyValue('--logo-box'))
    }))"""


class LogoSystemLightTest(BrowserTestCase):
    """The official logos: loaded, deliberately sized, rows aligned."""

    color_scheme = "light"

    def setUp(self) -> None:
        super().setUp()
        # Logos are lazy-loaded (v5): bring each section near the viewport
        # so the browser fetches them, then wait for the visible ones.
        for sec in ("writing", "featured", "speaking"):
            self.page.evaluate(f"document.getElementById('{sec}').scrollIntoView({{block:'center'}})")
            self.page.wait_for_timeout(60)
        try:
            self.page.wait_for_function(
                """() => [...document.querySelectorAll('.pub-logo')]
                    .filter(i => getComputedStyle(i).display !== 'none')
                    .every(i => i.complete && i.naturalWidth > 0)""",
                timeout=5000,
            )
        except Exception:
            pass  # the per-logo assertion below names the one that failed

    def test_every_logo_loads_and_has_its_own_size(self) -> None:
        logos = self.page.evaluate(VISIBLE_LOGOS)
        self.assertGreaterEqual(len(logos), 8)
        for logo in logos:
            with self.subTest(src=logo["src"]):
                self.assertTrue(logo["loaded"], "logo file did not load")
                # A new logo needs its own --h line in style.css.
                self.assertTrue(logo["h"], "no --h sizing rule for this logo")

    def test_cards_in_a_row_align_whatever_logo_they_carry(self) -> None:
        rows = self.page.evaluate(ROWS)
        for sec, row in rows.items():
            with self.subTest(section=sec):
                self.assertEqual({row["box"]}, set(row["heads"]), row)
                self.assertEqual(1, len(set(row["dates"])), row)


class LogoSystemDarkTest(LogoSystemLightTest):
    color_scheme = "dark"

    def test_chips_in_a_section_match_the_logo_box(self) -> None:
        for logo in self.page.evaluate(VISIBLE_LOGOS):
            with self.subTest(src=logo["src"]):
                if logo["bg"] in ("rgba(0, 0, 0, 0)", "transparent"):
                    continue  # carries its own background, or made for dark
                self.assertEqual(logo["box"], logo["height"])
                self.assertIn(logo["bg"], ("rgb(255, 255, 255)", "rgb(232, 72, 68)"))


class LogoPhoneTest(BrowserTestCase):
    viewport = {"width": 360, "height": 800}

    def test_pills_stay_inside_their_cards_in_both_themes(self) -> None:
        for theme in ("light", "dark"):
            with self.subTest(theme=theme):
                self.page.evaluate(f"document.documentElement.setAttribute('data-theme', '{theme}')")
                over = self.page.evaluate(
                    """() => [...document.querySelectorAll('.pub-kind')].filter(p => {
                        const box = p.closest('.card, figcaption').getBoundingClientRect();
                        return p.getBoundingClientRect().right > box.right + 0.5;
                    }).map(p => p.textContent)"""
                )
                self.assertEqual([], over)
                self.assertLessEqual(self.page.evaluate("document.body.scrollWidth"), 361)


class DarkLogoPlateTest(BrowserTestCase):
    color_scheme = "dark"

    def test_logos_sit_on_a_light_plate_in_dark_mode(self) -> None:
        self.page.evaluate(INSERT_LOGO, PLACEHOLDER)
        self.assertEqual(
            "rgb(255, 255, 255)",
            self.page.evaluate("getComputedStyle(document.querySelector('.pub-logo')).backgroundColor"),
        )


# The first column of a logo's box, from the left, that holds artwork:
# the box is screenshotted, decoded on a canvas (a data URL never taints
# it), and each column compared with the page just left of the box.
ARTWORK_START = """async ([shot, bg]) => {
    const img = new Image(); img.src = 'data:image/png;base64,' + shot; await img.decode();
    const c = document.createElement('canvas'); c.width = img.width; c.height = img.height;
    const g = c.getContext('2d'); g.drawImage(img, 0, 0);
    const d = g.getImageData(0, 0, c.width, c.height).data;
    for (let x = 0; x < c.width; x++)
        for (let y = 0; y < c.height; y++) {
            const i = (y * c.width + x) * 4;
            if (Math.abs(d[i] - bg[0]) + Math.abs(d[i + 1] - bg[1]) + Math.abs(d[i + 2] - bg[2]) > 120) return x;
        }
    return -1;
}"""


class LogoArtworkAlignmentTest(BrowserTestCase):
    """Each logo's artwork, not only its box, starts at its caption's edge."""

    color_scheme = "light"
    reduced_motion = "reduce"

    def test_every_logo_starts_at_the_left_edge_of_its_masthead(self) -> None:
        # The CTO Sync file carries 31% empty canvas on its left; shown as
        # is, its mark floated about 40px in from the caption link under
        # it while every other logo sat flush. style.css frames it to its
        # artwork, and this pins that for every logo on the page.
        self.page.add_style_tag(content="html{scroll-behavior:auto!important}")
        for sec in ("writing", "featured", "speaking"):
            self.page.evaluate(f"document.getElementById('{sec}').scrollIntoView({{block:'center'}})")
            self.page.wait_for_timeout(80)
        self.page.wait_for_function(
            "[...document.querySelectorAll('.pub-logo')].filter(i => getComputedStyle(i).display !== 'none').every(i => i.complete && i.naturalWidth)",
            timeout=5000,
        )
        count = self.page.evaluate("document.querySelectorAll('.pub-logo').length")
        checked = 0
        for i in range(count):
            logo = self.page.locator(".pub-logo").nth(i)
            if not logo.is_visible():
                continue
            src = logo.get_attribute("src")
            with self.subTest(src=src, index=i):
                if self.page.evaluate("(i) => !!document.querySelectorAll('.pub-logo')[i].closest('.carousel')", i):
                    dot = self.page.evaluate(
                        "(i) => [...document.querySelectorAll('#quoteCarousel .slide')].indexOf(document.querySelectorAll('.pub-logo')[i].closest('.slide'))", i)
                    self.page.evaluate(f"document.querySelectorAll('#quoteCarousel .carousel-dot')[{dot}].click()")
                    self.page.wait_for_timeout(120)
                logo.scroll_into_view_if_needed()
                box = logo.bounding_box()
                # The page colour just left of the box is the background.
                left = self.page.screenshot(clip={"x": box["x"] - 4, "y": box["y"] + box["height"] / 2, "width": 1, "height": 1})
                bg = self.page.evaluate(
                    """async (shot) => { const img = new Image(); img.src = 'data:image/png;base64,' + shot; await img.decode();
                        const c = document.createElement('canvas'); c.width = 1; c.height = 1; const g = c.getContext('2d');
                        g.drawImage(img, 0, 0); return [...g.getImageData(0, 0, 1, 1).data].slice(0, 3); }""",
                    base64.b64encode(left).decode(),
                )
                shot = logo.screenshot()
                start = self.page.evaluate(ARTWORK_START, [base64.b64encode(shot).decode(), bg])
                self.assertGreaterEqual(start, 0, "no artwork found")
                self.assertLessEqual(start, 4, f"artwork starts {start}px into the box")
                checked += 1
        self.assertGreaterEqual(checked, 10)


class CarouselFitTest(BrowserTestCase):
    def test_captions_never_run_under_the_controls(self) -> None:
        for width, height in ((360, 800), (768, 1024), (1400, 900)):
            with self.subTest(width=width):
                self.page.set_viewport_size({"width": width, "height": height})
                self.reload_page()
                gaps = self.page.evaluate(CAPTION_GAPS)
                self.assertEqual(6, len(gaps))
                self.assertTrue(all(g >= 8 for g in gaps), gaps)

    def test_an_open_quote_never_runs_under_the_controls(self) -> None:
        # Since Nov 6, 2026 each slide's quote opens below its headline.
        # The stage grows to fit it, so the arrows and dots move down
        # rather than sit on the quote, for every slide at every width.
        for width, height in ((360, 800), (768, 1024), (1400, 900)):
            with self.subTest(width=width):
                self.page.set_viewport_size({"width": width, "height": height})
                self.reload_page()
                gaps = []
                for i in range(6):
                    self.page.evaluate(f"document.querySelectorAll('#quoteCarousel .carousel-dot')[{i}].click()")
                    self.page.evaluate("document.querySelector('#quoteCarousel .slide.on details').open = true")
                    gaps.append(self.page.evaluate(OPEN_QUOTE_GAP))
                self.assertTrue(all(g >= 8 for g in gaps), gaps)


if __name__ == "__main__":
    unittest.main(verbosity=2)
