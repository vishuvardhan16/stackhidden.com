"""Static guarantees for stackhidden.com.

These tests use only the Python standard library.  They protect the owner's
standing content rules and the page's published counts without needing a
browser, which makes them the fastest and most stable part of the suite.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
STYLE = ROOT / "style.css"
SCRIPT = ROOT / "app.js"
NOT_FOUND = ROOT / "404.html"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def section(source: str, section_id: str) -> str:
    match = re.search(
        rf'<section id="{re.escape(section_id)}"[^>]*>(.*?)</section>',
        source,
        flags=re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"Section #{section_id} was not found")
    return match.group(1)


def list_items(section_html: str, list_class: str) -> list[str]:
    match = re.search(
        rf'<ul class="{re.escape(list_class)}">(.*?)</ul>',
        section_html,
        flags=re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"List .{list_class} was not found")
    return re.findall(r"<li>", match.group(1))


class StaticContentRulesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.index = read(INDEX)
        cls.style = read(STYLE)
        cls.script = read(SCRIPT)
        cls.sources = {
            "index.html": cls.index,
            "style.css": cls.style,
            "app.js": cls.script,
            "404.html": read(NOT_FOUND),
        }

    def test_forbidden_senior_word_is_absent_from_site_sources(self) -> None:
        for filename, source in self.sources.items():
            with self.subTest(filename=filename):
                self.assertNotIn("Senior", source)

    def test_no_portrait_file_or_reference(self) -> None:
        self.assertFalse((ROOT / "assets" / "profile.jpg").exists())
        for filename, source in self.sources.items():
            with self.subTest(filename=filename):
                self.assertNotIn("profile.jpg", source)
                self.assertNotIn("assets/profile", source)

    def test_social_preview_uses_the_designed_share_card(self) -> None:
        og_images = re.findall(
            r'<meta property="og:image" content="([^"]+)"', self.index
        )
        self.assertTrue(og_images, "No og:image declaration was found")
        self.assertEqual(
            "https://stackhidden.com/assets/og-card.png",
            og_images[0],
        )
        self.assertTrue((ROOT / "assets" / "og-card.png").is_file())

    def test_charset_is_declared_within_the_first_1024_bytes(self) -> None:
        index_bytes = INDEX.read_bytes()
        match = re.search(rb"<meta\s+charset\s*=", index_bytes, flags=re.IGNORECASE)
        self.assertIsNotNone(match, "No charset declaration was found")
        self.assertLess(match.start(), 1024)

    def test_exactly_four_case_files_with_expected_ids(self) -> None:
        case_ids = re.findall(
            r'<article class="panel case" id="(case-[^"]+)">', self.index
        )
        self.assertEqual(
            [
                "case-orchestration",
                "case-insights-api",
                "case-icm",
                "case-mosaic",
            ],
            case_ids,
        )

    def test_amazon_experience_has_ten_points(self) -> None:
        experience = section(self.index, "experience")
        self.assertEqual(10, len(list_items(experience, "points")))

    def test_what_i_work_on_has_48_skill_chips(self) -> None:
        work = section(self.index, "work")
        self.assertEqual(48, len(list_items(work, "chips")))

    def test_karyna_naminas_is_credited_on_her_articles(self) -> None:
        # Karyna Naminas, CEO of Label Your Data, wrote both Label Your
        # Data articles that quoted him, and the page must say so. Until
        # Nov 6, 2026 a two-sentence note under the carousel did; at the
        # owner's request the credit moved onto the two slides it
        # belongs to, as a byline on the date line, and the note went.
        featured = section(self.index, "featured")
        slides = re.findall(r'<figure class="slide">(.*?)</figure>', featured, flags=re.DOTALL)
        self.assertEqual(6, len(slides))
        for slide in slides:
            outlet = re.search(r'<p class="pub-name">([^<]+)</p>', slide).group(1)
            with self.subTest(outlet=outlet):
                bylined = re.search(
                    r'<p class="meta pub-date">[^<]+ &middot; <span class="byline">By Karyna Naminas</span></p>',
                    slide,
                )
                if outlet == "Label Your Data":
                    self.assertIsNotNone(bylined)
                else:
                    self.assertNotIn("Naminas", slide)
        self.assertNotIn("featured-note", featured)

    def test_featured_quotes_are_text_behind_read_my_quote(self) -> None:
        # Nov 6, 2026, at the owner's request: each Featured slide leads
        # with the article's headline, and the quote opens from "Read my
        # quote". The quotes are text, each citing its article, and the
        # only images left in the section are the caption logos.
        featured = section(self.index, "featured")
        self.assertEqual(6, featured.count('<details class="slide-quote">'))
        self.assertEqual(6, featured.count("<summary><span class=\"sq-closed\">Read my quote</span>"))
        self.assertEqual(6, len(re.findall(r'<blockquote cite="https://[^"]+"><p>', featured)))
        for tag in re.findall(r"<img\b[^>]*>", featured):
            with self.subTest(img=tag):
                self.assertIn('class="pub-logo"', tag)

    def test_hero_flow_absent(self) -> None:
        # The hero flow diagram was removed at the owner's direction on
        # Oct 27, 2026: its stage names described his internal platform
        # too closely for a public page. Guard against it coming back.
        self.assertNotIn('hero-flow', self.index)
        self.assertNotIn('hfPackets', self.index)


def theme_tokens(source: str, selector: str) -> dict[str, str]:
    """The colour tokens in the first rule whose selector starts with
    ``selector``, as {name: value}."""

    match = re.search(r"(?m)^" + re.escape(selector) + r"\s*\{([^}]*)\}", source)
    if match is None:
        raise AssertionError(f"No rule for {selector}")
    return dict(re.findall(r"--([a-z0-9]+):\s*(#[0-9a-fA-F]{3,8})", match.group(1)))


class FinishingTouchesTest(unittest.TestCase):
    """robots.txt, sitemap.xml, the 404 page, and the home-screen icon (v5)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.index = read(INDEX)
        cls.style = read(STYLE)
        cls.not_found = read(NOT_FOUND)

    def test_robots_allows_everything_and_names_the_sitemap(self) -> None:
        robots = read(ROOT / "robots.txt")
        self.assertIn("User-agent: *\nAllow: /", robots)
        self.assertNotIn("Disallow", robots)
        self.assertIn("Sitemap: https://stackhidden.com/sitemap.xml", robots)

    def test_sitemap_lists_the_canonical_page(self) -> None:
        import xml.etree.ElementTree as ET

        tree = ET.parse(ROOT / "sitemap.xml")
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [el.text for el in tree.getroot().findall("s:url/s:loc", ns)]
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', self.index).group(1)
        self.assertEqual([canonical], locs)

    def test_404_page_is_noindex_and_uses_only_absolute_urls(self) -> None:
        # GitHub Pages serves 404.html at whatever depth was asked for,
        # so a relative URL would break on /a/b/c.
        self.assertIn('<meta name="robots" content="noindex">', self.not_found)
        urls = re.findall(r'(?:href|src)="([^"]*)"', self.not_found)
        self.assertTrue(urls)
        for url in urls:
            with self.subTest(url=url):
                self.assertTrue(url.startswith("/"), url)

    def test_404_section_links_point_at_real_sections(self) -> None:
        ids = set(re.findall(r'id="([^"]+)"', self.index))
        for anchor in re.findall(r'href="/#([a-z-]+)"', self.not_found):
            with self.subTest(anchor=anchor):
                self.assertIn(anchor, ids)

    def test_404_colours_match_the_site_theme(self) -> None:
        for selector in (':root,:root[data-theme="dark"]', ':root[data-theme="light"]'):
            with self.subTest(theme=selector):
                site = theme_tokens(self.style.replace(":root, :root", ":root,:root"), selector)
                page = theme_tokens(self.not_found, selector)
                self.assertTrue(page)
                for name, value in page.items():
                    self.assertEqual(site.get(name), value, name)

    def test_theme_colour_tags_agree_with_app_js(self) -> None:
        script = read(SCRIPT)
        for source in (self.index, self.not_found):
            light = re.search(r'name="theme-color" content="(#\w+)" media="\(prefers-color-scheme: light\)"', source).group(1)
            dark = re.search(r'name="theme-color" content="(#\w+)" media="\(prefers-color-scheme: dark\)"', source).group(1)
            self.assertIn(f"light: '{light}', dark: '{dark}'", script)

    def test_home_screen_icon_is_a_180px_png(self) -> None:
        data = (ROOT / "assets" / "apple-touch-icon.png").read_bytes()
        self.assertEqual(b"\x89PNG\r\n\x1a\n", data[:8])
        width, height = int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
        self.assertEqual((180, 180), (width, height))
        self.assertIn('<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">', self.index)


class LoadingRulesTest(unittest.TestCase):
    """Mobile loading (v5): every image is sized and lazy, the loop waits."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.index = read(INDEX)

    def test_every_image_is_sized_lazy_and_async(self) -> None:
        # Nothing on the page above the fold is an <img>: the hero figure
        # is a video poster. A new image above the fold should drop
        # loading="lazy" and say why here.
        markup = re.sub(r"<!--.*?-->", "", self.index, flags=re.DOTALL)
        imgs = re.findall(r"<img\b[^>]*>", markup)
        self.assertGreaterEqual(len(imgs), 13)
        for tag in imgs:
            with self.subTest(img=re.search(r'src="([^"]+)"', tag).group(1)):
                self.assertRegex(tag, r'\swidth="\d+"')
                self.assertRegex(tag, r'\sheight="\d+"')
                self.assertIn('loading="lazy"', tag)
                self.assertIn('decoding="async"', tag)

    def test_every_referenced_asset_exists(self) -> None:
        for path in re.findall(r'(?:src|poster|href)="(assets/[^"]+)"', self.index):
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).is_file(), path)

    def test_the_hero_loop_waits_for_app_js(self) -> None:
        video = re.search(r'<video id="heroVideo"[^>]*>', self.index).group(0)
        self.assertIn('preload="none"', video)
        self.assertNotIn("autoplay", video)

    def test_logo_files_stay_light(self) -> None:
        # The first Tech Magazine PNG was 1200x250, 72 KB, for a logo shown
        # 28px tall: more than every other logo on the page put together.
        # A raster logo needs about 2x to 3x its shown height and no more.
        html = read(INDEX)
        for path in sorted((ROOT / "assets" / "logos").iterdir()):
            with self.subTest(logo=path.name):
                self.assertLessEqual(path.stat().st_size, 24 * 1024)
                if path.suffix != ".png":
                    continue
                data = path.read_bytes()
                natural = int.from_bytes(data[20:24], "big")
                shown = re.search(rf'src="assets/logos/{re.escape(path.name)}"[^>]*height="(\d+)"', html)
                self.assertIsNotNone(shown, "PNG logo not on the page")
                self.assertLessEqual(natural, 3.2 * int(shown.group(1)))

    def test_quote_images_stay_light(self) -> None:
        for path in sorted((ROOT / "assets").glob("quote-*.webp")):
            with self.subTest(image=path.name):
                self.assertLessEqual(path.stat().st_size, 40 * 1024)
