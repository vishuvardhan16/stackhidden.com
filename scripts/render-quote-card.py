#!/usr/bin/env python3
"""Render a Featured In quote card as lossless WebP.

    python3 scripts/render-quote-card.py assets/quote-<slug>.webp "Quote text, as published."

The cards for the Informatics Magazine, CTO Sync, and Tech Magazine quotes
are made for this site in the style of the Label Your Data quote blocks:
1720 by 366, white, the quote in italics under an opening mark, then the
credit line with a closing mark at the right. There is no photo, by the
owner's rule for this site. Every card comes from this one template, so
the carousel reads as a set: same typeface, sizes, and positions. The two
quote lines are balanced, so no card ends on a stub of a line.

The quote text is passed exactly as published, spelling included
("favour", "prioritise"). The credit line defaults to the one on every
card; --name and --title change it.

Needs Playwright with a Chromium (the test suite's) and Pillow. The type
is Arial, or a metric-compatible substitute such as Liberation Sans, so
line breaks fall where they do on the existing cards.
"""

from __future__ import annotations

import argparse
import html
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))

from helpers import chromium_launch_kwargs  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

WIDTH, HEIGHT = 1720, 366

TEMPLATE = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:{w}px;height:{h}px;background:#fff;overflow:hidden}}
body{{position:relative;font-family:Arial,"Liberation Sans",Helvetica,sans-serif;color:#191919}}
.open,.close{{position:absolute;font-weight:700;line-height:1;color:#191919}}
.open{{left:-5px;top:{open_top}px;font-size:{mark}px}}
.close{{right:31px;top:{close_top}px;font-size:{mark}px;font-style:italic}}
.quote{{position:absolute;left:8px;top:{quote_top}px;width:1610px;margin:0;font-style:italic;font-size:{quote_size}px;line-height:{quote_lh}px;text-wrap:balance}}
.name{{position:absolute;left:209px;top:{name_top}px;margin:0;font-weight:700;font-size:{name_size}px;line-height:1.15;color:#191919}}
.title{{position:absolute;left:209px;top:{title_top}px;margin:0;font-size:{title_size}px;line-height:1.15;color:#6e6e6e}}
</style></head><body>
<span class="open">&ldquo;</span>
<p class="quote">{quote}</p>
<p class="name">{name}</p>
<p class="title">{title}</p>
<span class="close">&rdquo;</span>
</body></html>"""

LAYOUT = dict(open_top=-6, mark=96, close_top=254, quote_top=54, quote_size=44, quote_lh=58,
              name_top=238, name_size=46, title_top=296, title_size=44)


def render(out: Path, quote: str, name: str, title: str, layout: dict = LAYOUT) -> None:
    from PIL import Image

    page_html = TEMPLATE.format(w=WIDTH, h=HEIGHT, quote=html.escape(quote), name=html.escape(name),
                                title=html.escape(title), **layout)
    with tempfile.TemporaryDirectory() as tmp:
        png = Path(tmp) / "card.png"
        with sync_playwright() as p:
            browser = p.chromium.launch(**chromium_launch_kwargs(), args=["--no-sandbox"])
            page = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT}, device_scale_factor=1)
            page.set_content(page_html)
            lines = page.evaluate("Math.round(document.querySelector('.quote').getBoundingClientRect().height / %d)" % layout["quote_lh"])
            if lines > 2:
                raise SystemExit(f"quote runs to {lines} lines; the card holds two")
            page.screenshot(path=str(png), clip={"x": 0, "y": 0, "width": WIDTH, "height": HEIGHT})
            browser.close()
        Image.open(png).convert("RGB").save(out, "WEBP", lossless=True, method=6)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out", type=Path)
    ap.add_argument("quote")
    ap.add_argument("--name", default="Vishnuvardhan Reddy Kaithapuram")
    ap.add_argument("--title", default="Software Development Engineer, Amazon")
    args = ap.parse_args()
    render(args.out, args.quote, args.name, args.title)
    print(f"wrote {args.out}, {args.out.stat().st_size} bytes")


if __name__ == "__main__":
    main()
