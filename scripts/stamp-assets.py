#!/usr/bin/env python3
"""Stamp style.css and app.js into index.html with their content version.

index.html asks for the stylesheet and the script as style.css?v=<hash>
and app.js?v=<hash>, where <hash> is the first 10 hex digits of the
file's SHA-256. GitHub Pages lets browsers and its own CDN reuse a file
for up to 10 minutes, so without a version a fresh page could arrive
with the stylesheet from before a deploy. On Nov 8, 2026 that is what
broke the live hero for the owner: the new background layer, styled by
nothing, took the hero's first column. With the version in the address,
a new page can only ever load the files it was written against.

Run it after editing style.css or app.js, from the repository root:

  python3 scripts/stamp-assets.py

tests/test_static.py fails until the stamps match the files.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


def version(name: str) -> str:
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()[:10]


def stamp(html: str) -> str:
    for name, attr in (("style.css", "href"), ("app.js", "src")):
        pattern = rf'{attr}="{re.escape(name)}(\?v=[0-9a-f]*)?"'
        if len(re.findall(pattern, html)) != 1:
            raise SystemExit(f"expected exactly one {attr}=\"{name}...\" in index.html")
        html = re.sub(pattern, f'{attr}="{name}?v={version(name)}"', html)
    return html


def main() -> None:
    html = INDEX.read_text(encoding="utf-8")
    new = stamp(html)
    if new == html:
        print("index.html already matches style.css and app.js")
        return
    INDEX.write_text(new, encoding="utf-8")
    print(f"stamped style.css?v={version('style.css')} and app.js?v={version('app.js')}")


if __name__ == "__main__":
    main()
