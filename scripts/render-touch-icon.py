#!/usr/bin/env python3
"""Render assets/apple-touch-icon.png from assets/favicon.svg.

    python3 scripts/render-touch-icon.py

The home-screen icon is the favicon drawn full-bleed at 180x180: same
colours, letters, and proportions, with the rounded corners removed,
because iOS rounds the corners itself and turns a transparent corner
black. Rerun this whenever the favicon changes.

Needs Playwright with a Chromium (the test suite's). Pillow is optional:
when it is installed, the PNG is reduced to a small palette, which keeps
the flat two-colour icon near 1 KB.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))

from helpers import chromium_launch_kwargs  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

SIZE = 180
OUT = ROOT / "assets" / "apple-touch-icon.png"


def main() -> None:
    svg = (ROOT / "assets" / "favicon.svg").read_text(encoding="utf-8")
    svg = re.sub(r'\srx="[^"]*"', "", svg, count=1)
    svg = svg.replace("<svg ", f'<svg width="{SIZE}" height="{SIZE}" ', 1)
    with sync_playwright() as p:
        browser = p.chromium.launch(**chromium_launch_kwargs(), args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": SIZE, "height": SIZE}, device_scale_factor=1)
        page.set_content(f'<html><body style="margin:0">{svg}</body></html>')
        page.screenshot(path=str(OUT), clip={"x": 0, "y": 0, "width": SIZE, "height": SIZE})
        browser.close()
    try:
        from PIL import Image
    except ImportError:
        print(f"wrote {OUT.relative_to(ROOT)} (install Pillow for a smaller file)")
        return
    Image.open(OUT).convert("RGB").quantize(colors=64).save(OUT, optimize=True)
    print(f"wrote {OUT.relative_to(ROOT)}, {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
