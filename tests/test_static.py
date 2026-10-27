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

    def test_karyna_naminas_credit_line_is_present(self) -> None:
        self.assertIn(
            "Both articles were written by Karyna Naminas, CEO of Label Your "
            "Data, who quoted me as an expert source.",
            self.index,
        )

    def test_hero_flow_absent(self) -> None:
        # The hero flow diagram was removed at the owner's direction on
        # Oct 27, 2026: its stage names described his internal platform
        # too closely for a public page. Guard against it coming back.
        self.assertNotIn('hero-flow', self.index)
        self.assertNotIn('hfPackets', self.index)
