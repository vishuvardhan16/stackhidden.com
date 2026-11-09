#!/usr/bin/env python3
"""Make assets/corner-friend.webp: the owner's drawing, cut out of its backdrop.

The corner friend is the owner's own drawing (an anime-style boy against a
golden, sunlit bokeh). On the site the gold clashed with the cool page, so
the boy is lifted out of it and the page shows through instead
(docs/the-cursor-bot.md, "How he blends into the page").

    python3 scripts/cut-corner-friend.py path/to/original-drawing.png

The original is the owner's file (514 by 355 pixels, sha256 checked below)
and is not kept in the repo. Needs: pip install "rembg[cpu]" scipy pillow.
The first run downloads the isnet-anime model (176MB) to ~/.rembg.

Steps, and why:
1. Mask. rembg's isnet-anime model, trained on anime illustration, gives
   each pixel how much of it is the boy (0 to 1). Hair strands survive.
2. Firm up both ends. Under 5% is stray bokeh, not hair; left in, it shows
   as specks on the light theme. At the other end the model rarely says
   a full 100%: inside him it says 98 to 99%, which would let the page
   show faintly through his face. From 97% up counts as fully him. Gaps
   between hair strands stay soft, as drawn.
3. Take the gold out of the edges. A pixel that is part hair, part backdrop
   was painted as C = a*F + (1 - a)*B. B, the backdrop just behind it, is
   estimated from nearby pure-backdrop pixels (a tight blur weighted to
   them), and the hair's own colour is solved: F = (C - (1 - a)*B) / a.
   Every backdrop here is brighter than the hair in front of it, so F is
   held at or below C; that stops a too-dark estimate of B leaving a pale
   fringe. Pixels that are fully the boy keep their painted colour, so the
   face and eyes (and the blink lids sampled from them) are untouched.
4. Crop and scale exactly as the framed version was: the square
   (150, 0)-(450, 300), down to 240 pixels, Lanczos, in premultiplied
   alpha so no backdrop colour creeps back in. The lids in index.html are
   drawn in this 240-pixel space, so they still sit on the eyes.
5. WebP, quality 88, with lossless alpha so fine hair edges stay exact.

With rembg 2.0.87, onnxruntime 1.29.0, scipy 1.18, numpy 2.5 and Pillow
12.3 (libwebp 1.6.0) this reproduces the committed file byte for byte.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from rembg import new_session, remove
from scipy.ndimage import gaussian_filter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "corner-friend.webp"
ORIGINAL_SHA256 = "d6be42e6ab4fc6b20073ffc6c58cdaf91d9bb2dbbd7067c3f61f23b7965fd950"
CROP = (150, 0, 450, 300)
SIZE = 240
FAINT = 0.05       # mask values under this are stray bokeh
SURE = 0.97        # mask values from this up are fully him
BACKDROP_BLUR = 5  # px; how far round an edge to look for the backdrop
SOLID = 0.985      # after step 2, at or above this a pixel keeps its paint
MIN_ALPHA = 0.12   # floor for the division in step 3, so it stays stable


def cut(src: Path) -> Image.Image:
    im = Image.open(src).convert("RGB")
    mask = remove(im, session=new_session("isnet-anime"), only_mask=True)
    c = np.asarray(im, float) / 255
    a = np.asarray(mask.convert("L"), float) / 255

    backdrop = (a < 0.03).astype(float)
    weight = gaussian_filter(backdrop, BACKDROP_BLUR) + 1e-6
    b = np.stack([gaussian_filter(c[..., i] * backdrop, BACKDROP_BLUR) / weight for i in range(3)], -1)

    a = np.clip((a - FAINT) / (SURE - FAINT), 0, 1)
    f = np.clip((c - (1 - a[..., None]) * b) / np.maximum(a, MIN_ALPHA)[..., None], 0, 1)
    f = np.minimum(f, c)
    f = np.where(a[..., None] >= SOLID, c, f)

    rgba = Image.fromarray(np.uint8(np.round(np.dstack([f, a]) * 255)), "RGBA")
    return rgba.crop(CROP).convert("RGBa").resize((SIZE, SIZE), Image.LANCZOS).convert("RGBA")


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.split("\n\n")[1].strip(), file=sys.stderr)
        return 2
    src = Path(sys.argv[1])
    digest = hashlib.sha256(src.read_bytes()).hexdigest()
    if digest != ORIGINAL_SHA256:
        print(f"note: {src} is not the original drawing (sha256 {digest[:12]}...); "
              "the crop box and the lids in index.html are fitted to that one.", file=sys.stderr)
    cut(src).save(OUT, "WEBP", quality=88, alpha_quality=100, method=6)
    print(f"{OUT.relative_to(ROOT)}: {OUT.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
