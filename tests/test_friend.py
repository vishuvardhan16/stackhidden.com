"""How the corner friend sits on the page: no frame, the page's own light.

Nov 8, 2026: the owner's drawing is cut out of its golden backdrop and sits
on the page with no frame, ring, or disc (docs/the-cursor-bot.md). How he
moves is checked in test_motion.py; this module checks how he looks.
"""

from __future__ import annotations

import base64
import unittest

from helpers import ROOT, BrowserTestCase

# Holds him still and takes away everything round the drawing that is
# there on purpose: the sparkles, the "z z", and the shadow under him,
# which by design lands right next to his silhouette. What is left in the
# frame is the drawing itself, and any frame, ring, or backdrop. The page
# behind him is held still too: every transition and animation stops (the
# sections fade in for a moment after load), and the layers that move on
# their own (the hero loop, the graph canvas, the cursor glow) are hidden.
STILL = """
*,*::before,*::after{animation:none!important;transition:none!important}
#cursorBot .bot-head{transform:none!important}
#cursorBot .bot-spark,#cursorBot .bot-zz{visibility:hidden!important}
#cursorBot .bot-hop{filter:none!important}
#heroBg,#graph,#cursorGlow{visibility:hidden!important}
"""

# Compares two captures of the frame, one with the drawing and one without,
# using the drawing's own transparency, scaled to the frame on screen. A
# pixel is "clear" when the drawing is fully transparent there and for 3px
# round, and "solid" when it is fully opaque there and for 3px round and
# inside the band the fade leaves alone (6% to 80% down). The margin is
# 3px because the browser shrinks the 240px drawing to 100 or 76 with a
# filter that reaches about that far from a hair; at 2px a faint edge of
# hair still showed. Returns the largest difference over clear pixels, the
# median over solid ones (each as the biggest channel gap), and what share
# of the frame each kind covers.
COMPARE = r"""async ([withPng, withoutPng, drawingWebp]) => {
  const load = async src => { const i = new Image(); i.src = src; await i.decode(); return i; };
  const [a, b, d] = await Promise.all([load('data:image/png;base64,' + withPng),
    load('data:image/png;base64,' + withoutPng), load('data:image/webp;base64,' + drawingWebp)]);
  const w = a.naturalWidth, h = a.naturalHeight;
  const px = img => { const c = document.createElement('canvas'); c.width = w; c.height = h;
    const g = c.getContext('2d'); g.drawImage(img, 0, 0, w, h); return g.getImageData(0, 0, w, h).data; };
  const A = px(a), B = px(b), D = px(d), R = 3;
  const around = (x, y, test) => { for (let j = -R; j <= R; j++) for (let i = -R; i <= R; i++) {
    const xx = x + i, yy = y + j; if (xx < 0 || yy < 0 || xx >= w || yy >= h) continue;
    if (!test(D[(yy * w + xx) * 4 + 3])) return false; } return true; };
  let clear = 0, worstClear = 0; const solid = [];
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const k = (y * w + x) * 4;
    const gap = Math.max(Math.abs(A[k] - B[k]), Math.abs(A[k + 1] - B[k + 1]), Math.abs(A[k + 2] - B[k + 2]));
    if (around(x, y, v => v === 0)) { clear++; worstClear = Math.max(worstClear, gap); }
    else if (y > h * 0.06 && y < h * 0.8 && around(x, y, v => v === 255)) solid.push(gap);
  }
  solid.sort((p, q) => p - q);
  return { clear: clear / (w * h), solid: solid.length / (w * h), worstClear, medianSolid: solid[solid.length >> 1] || 0 };
}"""


class FriendBlendTest(BrowserTestCase):
    color_scheme = "dark"
    accent = "rgba(110, 168, 254"  # dark theme --accent, as the glow's colour

    def frame_capture(self) -> str:
        box = self.page.locator("#cursorBot .bot-frame").bounding_box()
        clip = {k: round(box[k]) for k in ("x", "y", "width", "height")}
        return base64.b64encode(self.page.screenshot(clip=clip)).decode()

    def test_the_page_shows_wherever_the_drawing_is_clear(self) -> None:
        self.page.add_style_tag(content=STILL)
        self.page.wait_for_function("document.querySelector('#cursorBot .bot-face').complete")
        self.page.wait_for_timeout(100)
        with_him = self.frame_capture()
        self.page.add_style_tag(content="#cursorBot .bot-frame{visibility:hidden!important}")
        self.page.wait_for_timeout(100)
        without_him = self.frame_capture()
        self.page.wait_for_timeout(100)
        self.assertEqual(without_him, self.frame_capture(),
                         "the page behind him moved between captures; hide the new moving layer in STILL")
        drawing = base64.b64encode((ROOT / "assets" / "corner-friend.webp").read_bytes()).decode()
        r = self.page.evaluate(COMPARE, [with_him, without_him, drawing])
        # Even with the 3px margin, about a fifth of the frame is clear of
        # him (17% at phone size). A picture with a backdrop has none, and
        # then the check below would prove nothing.
        self.assertGreater(r["clear"], 0.10, r)
        self.assertGreater(r["solid"], 0.10, r)
        # Round him: exactly the page (0 when measured), give or take rounding.
        self.assertLessEqual(r["worstClear"], 2, r)
        # And he is really there. Not every pixel of him stands out (his
        # near-black hair is within a few levels of the dark page), so this
        # asks that the middle of them does: 55 in dark, 215 in light when
        # measured. A picture that failed to load scores 0.
        self.assertGreaterEqual(r["medianSolid"], 40, r)

    def test_his_glow_pool_and_shadow_take_the_page_colours(self) -> None:
        # Behind him: a glow in the theme's accent, over a pool of the page's
        # own background colour, which fades text out before it reaches him
        # and must match the page exactly, or it would show as a smudge on
        # bare page. The pool is read against the live --bg token, so a new
        # page colour that leaves the pool behind fails here.
        look = self.page.evaluate(
            """() => ({
                glow: getComputedStyle(document.querySelector('#cursorBot .bot-head'), '::before').backgroundImage,
                bg: getComputedStyle(document.documentElement).getPropertyValue('--bg').trim(),
                shadow: getComputedStyle(document.querySelector('#cursorBot .bot-hop')).filter,
                frame: (s => [s.borderTopWidth, s.boxShadow, s.backgroundColor])(getComputedStyle(document.querySelector('#cursorBot .bot-frame')))
            })"""
        )
        self.assertEqual(2, look["glow"].count("radial-gradient"), look["glow"])
        glow, pool = look["glow"].split("radial-gradient")[1:]
        self.assertIn(self.accent, glow)
        r, g, b = (int(look["bg"][i:i + 2], 16) for i in (1, 3, 5))
        self.assertIn(f"rgba({r}, {g}, {b}, 0.95)", pool)
        self.assertIn("drop-shadow", look["shadow"])
        self.assertEqual(["0px", "none", "rgba(0, 0, 0, 0)"], look["frame"])


class FriendBlendLightTest(FriendBlendTest):
    color_scheme = "light"
    accent = "rgba(31, 95, 208"  # light theme --accent


class FriendBlendPhoneTest(FriendBlendTest):
    viewport = {"width": 390, "height": 844}


class FriendBlendAsleepTest(FriendBlendTest):
    # Asleep he dims, but stays cut out: still no box round him.
    color_scheme = "light"
    accent = "rgba(31, 95, 208"
    reduced_motion = "reduce"


if __name__ == "__main__":
    unittest.main()
