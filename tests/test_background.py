"""The hero background (Nov 8, 2026): the lineage network loop behind the top
of the page.

Four videos (dark and light, wide and narrow) and their four stills. The
still is CSS, so it shows with no JavaScript; app.js gives the video a src
only when it may play. These tests pin what a visitor gets: the right file
for the theme and the width and nothing else downloaded; no video at all
under reduced motion, the footer's Reduce motion, Data Saver, or 2G; the
file swapped, and the stale one hidden at once, when the theme flips or the
width crosses 920px; a pause whenever the layer is off screen or the tab is
hidden; a layer that runs edge to edge from the top of the page and stays
out of print, forced colours, and the accessibility tree; and text that
keeps its contrast over the still in both themes at desktop and phone size.

The checks assert requests, src values, and play/pause calls, never decoded
frames: the Chromium that CI installs may have no H.264 decoder.
"""

from __future__ import annotations

import base64
import re
import unittest

from helpers import ROOT, BrowserTestCase


FILES = {
    ("dark", False): "hero-network-dark.mp4",
    ("light", False): "hero-network-light.mp4",
    ("dark", True): "hero-network-dark-narrow.mp4",
    ("light", True): "hero-network-light-narrow.mp4",
}

# Every play() and pause() call, per element id, without changing either.
MEDIA_LOG = """
window.__media = [];
(() => { const P = HTMLMediaElement.prototype, play = P.play, pause = P.pause;
  P.play = function () { window.__media.push([this.id, 'play']); return play.call(this); };
  P.pause = function () { window.__media.push([this.id, 'pause']); return pause.call(this); };
})();
"""
LAST_CALL = "(window.__media.filter(c => c[0] === 'heroBgVideo').pop() || [null, null])[1]"


class BackgroundCase(BrowserTestCase):
    color_scheme = "dark"

    def open_page(self, suffix: str = "") -> None:
        if not hasattr(self, "requested"):
            self.requested: list[str] = []
            self.page.on("request", lambda r: self.requested.append(r.url))
            self.context.add_init_script(MEDIA_LOG)
        super().open_page(suffix)

    def videos_asked_for(self) -> list[str]:
        return sorted({name for name in FILES.values() for u in self.requested if u.endswith("/" + name)})

    def stills_asked_for(self) -> list[str]:
        return sorted({u.rsplit("/", 1)[1] for u in self.requested if "/hero-network-" in u and u.endswith(".webp")})

    def src(self) -> str | None:
        return self.page.evaluate("document.getElementById('heroBgVideo').getAttribute('src')")

    def still(self) -> str:
        return self.page.evaluate("getComputedStyle(document.getElementById('heroBg'), '::before').backgroundImage")

    def wait_for_still_shown(self) -> None:
        self.page.wait_for_function("document.getElementById('heroBg').classList.contains('still')", timeout=5000)

    def showing_video(self) -> bool:
        return self.page.evaluate("document.getElementById('heroBg').classList.contains('playing')")

    def pretend_playing(self) -> None:
        # The playing event, as a browser with a decoder would fire it.
        self.page.evaluate("document.getElementById('heroBgVideo').dispatchEvent(new Event('playing'))")

    def wait_for_last_call(self, call: str) -> None:
        self.page.wait_for_function(f"{LAST_CALL} === '{call}'", timeout=4000)

    def toggle_motion(self) -> None:
        # Pressed in place: a real click would scroll to the footer, and the
        # layer off screen pauses for that reason instead.
        self.page.evaluate("document.getElementById('motionBtn').click()")

    def flip_theme(self) -> dict:
        # The state straight after the theme changes, before any media event
        # (a task) can run: a decoding browser starts the new file within a
        # few milliseconds, so a later look could not tell "hidden at once"
        # from "never hidden".
        return self.page.evaluate(
            """async () => { document.getElementById('theme-toggle').click(); await Promise.resolve();
                 const bg = document.getElementById('heroBg');
                 return {showing: bg.classList.contains('playing'), still: getComputedStyle(bg, '::before').backgroundImage,
                         src: document.getElementById('heroBgVideo').getAttribute('src')}; }"""
        )


class DesktopDarkTest(BackgroundCase):
    def test_plays_the_dark_desktop_file_and_nothing_else(self) -> None:
        self.wait_for_last_call("play")
        self.assertEqual("assets/hero-network-dark.mp4", self.src())
        self.page.wait_for_timeout(500)
        self.assertEqual(["hero-network-dark.mp4"], self.videos_asked_for())
        self.assertEqual(["hero-network-dark.webp"], self.stills_asked_for())
        self.assertIn("hero-network-dark.webp", self.still())
        self.wait_for_still_shown()

    def test_the_still_waits_for_app_js_then_fades_in(self) -> None:
        # Loaded with the stylesheet, the still shared a slow phone's
        # bandwidth with app.js and held back the first paint (Nov 8,
        # 2026). Now nothing asks for it until app.js has arrived, here
        # held back 600ms. Then it fades in, and fades in again when a
        # theme flip picks the other still.
        import time

        context = self.browser.new_context(viewport=self.viewport, color_scheme="dark")
        # Over HTTP (as in CI) app.js arrives 600ms late; a file:// page
        # cannot be routed, and there the order alone is checked.
        context.route("**/app.js?v=*", lambda route: (time.sleep(0.6), route.continue_()))
        page = context.new_page()
        events: list[str] = []
        page.on("requestfinished", lambda r: events.append("app.js in") if "/app.js?v=" in r.url else None)
        page.on("request", lambda r: events.append("still asked") if r.url.endswith("/hero-network-dark.webp") else None)
        try:
            page.goto(self.page.url, wait_until="load")
            page.wait_for_function("document.getElementById('heroBg').classList.contains('still')", timeout=5000)
            self.assertEqual(["app.js in", "still asked"], events[:2])
            fade = page.evaluate("getComputedStyle(document.getElementById('heroBg'), '::before').transitionDuration")
            self.assertEqual("0.6s", fade)
            flipped = page.evaluate(
                """async () => { document.getElementById('theme-toggle').click(); await Promise.resolve();
                     return document.getElementById('heroBg').classList.contains('still'); }"""
            )
            self.assertFalse(flipped)  # hidden until the light still is in
            page.wait_for_function("document.getElementById('heroBg').classList.contains('still')", timeout=5000)
        finally:
            context.close()

    def test_theme_flip_hides_the_stale_video_and_plays_the_other_file(self) -> None:
        self.wait_for_last_call("play")
        self.pretend_playing()
        self.assertTrue(self.showing_video())
        after = self.flip_theme()
        # At once: the dark video no longer covers the light still.
        self.assertFalse(after["showing"])
        self.assertIn("hero-network-light.webp", after["still"])
        self.assertEqual("assets/hero-network-light.mp4", after["src"])
        self.wait_for_last_call("play")
        self.page.wait_for_timeout(300)
        self.assertIn("hero-network-light.mp4", self.videos_asked_for())
        # A late playing event from the old file must not bring it back.
        self.page.evaluate(
            "document.getElementById('heroBg').classList.remove('playing'); document.getElementById('heroBgVideo').setAttribute('src', 'assets/hero-network-dark.mp4')"
        )
        self.pretend_playing()
        self.assertFalse(self.showing_video())

    def test_theme_flip_with_motion_off_downloads_nothing_new(self) -> None:
        self.wait_for_last_call("play")
        self.pretend_playing()
        self.toggle_motion()
        self.wait_for_last_call("pause")
        self.assertTrue(self.showing_video())  # paused on its frame, like the figure
        after = self.flip_theme()
        self.assertFalse(after["showing"])
        self.assertIn("hero-network-light.webp", after["still"])
        self.assertEqual("assets/hero-network-dark.mp4", after["src"])
        self.page.wait_for_timeout(500)
        self.assertNotIn("hero-network-light.mp4", self.videos_asked_for())
        # Motion back on: the light file now loads and plays.
        self.toggle_motion()
        self.wait_for_last_call("play")
        self.assertEqual("assets/hero-network-light.mp4", self.src())

    def test_footer_toggle_pauses_and_resumes(self) -> None:
        self.wait_for_last_call("play")
        self.toggle_motion()
        self.wait_for_last_call("pause")
        self.toggle_motion()
        self.wait_for_last_call("play")

    def test_pauses_off_screen_and_resumes_on_return(self) -> None:
        self.wait_for_last_call("play")
        self.page.add_style_tag(content="html{scroll-behavior:auto!important}")
        self.page.evaluate("window.scrollTo(0, document.getElementById('contact').getBoundingClientRect().top + scrollY)")
        self.wait_for_last_call("pause")
        self.page.evaluate("window.scrollTo(0, 0)")
        self.wait_for_last_call("play")

    def test_pauses_while_the_tab_is_hidden(self) -> None:
        self.wait_for_last_call("play")
        self.page.evaluate("Object.defineProperty(document, 'hidden', {configurable: true, get: () => true}); document.dispatchEvent(new Event('visibilitychange'))")
        self.wait_for_last_call("pause")
        self.page.evaluate("Object.defineProperty(document, 'hidden', {configurable: true, get: () => false}); document.dispatchEvent(new Event('visibilitychange'))")
        self.wait_for_last_call("play")

    def test_crossing_920px_swaps_to_the_narrow_file(self) -> None:
        self.wait_for_last_call("play")
        self.pretend_playing()
        self.page.set_viewport_size({"width": 900, "height": 900})
        self.page.wait_for_function("document.getElementById('heroBgVideo').getAttribute('src') === 'assets/hero-network-dark-narrow.mp4'", timeout=4000)
        self.assertFalse(self.showing_video())
        self.assertIn("hero-network-dark-narrow.webp", self.still())
        self.page.set_viewport_size({"width": 1400, "height": 900})
        self.page.wait_for_function("document.getElementById('heroBgVideo').getAttribute('src') === 'assets/hero-network-dark.mp4'", timeout=4000)

    def test_layer_runs_edge_to_edge_from_the_top_of_the_page(self) -> None:
        box = self.page.evaluate(
            """() => { const b = document.getElementById('heroBg').getBoundingClientRect(), t = document.querySelector('.hero-text').getBoundingClientRect(),
                 s = document.querySelector('.hero-side').getBoundingClientRect(), hd = document.querySelector('.site-header').getBoundingClientRect();
               return {top: b.top + scrollY, left: b.left, right: b.right, bottom: b.bottom + scrollY, vw: document.documentElement.clientWidth,
                       content: Math.max(t.bottom, s.bottom) + scrollY, header: hd.bottom,
                       z: getComputedStyle(document.getElementById('heroBg')).zIndex, heroStack: getComputedStyle(document.querySelector('.hero')).isolation}; }"""
        )
        self.assertLessEqual(box["top"], 0)  # under the header, from the very top
        self.assertLessEqual(box["left"], 0)
        self.assertGreaterEqual(box["right"], box["vw"])
        self.assertGreaterEqual(box["bottom"], box["content"])  # on desktop it covers the hero
        self.assertEqual("-1", box["z"])
        self.assertEqual("auto", box["heroStack"])
        widths = self.page.evaluate("[document.documentElement.scrollWidth, document.body.scrollWidth, innerWidth]")
        self.assertLessEqual(max(widths[:2]), widths[2])

    def test_hidden_from_assistive_tech_and_the_keyboard(self) -> None:
        state = self.page.evaluate(
            """() => { const bg = document.getElementById('heroBg'), v = document.getElementById('heroBgVideo');
               return {hidden: bg.getAttribute('aria-hidden'), controls: v.controls, tab: v.tabIndex, events: getComputedStyle(bg).pointerEvents, muted: v.muted}; }"""
        )
        self.assertEqual({"hidden": "true", "controls": False, "tab": -1, "events": "none", "muted": True}, state)
        tree = self.page.accessibility.snapshot(interesting_only=False) if hasattr(self.page, "accessibility") else None
        if tree is not None:
            self.assertNotIn("heroBgVideo", str(tree))

    def test_gone_in_print_and_forced_colours(self) -> None:
        self.page.emulate_media(media="print")
        self.assertEqual("none", self.page.evaluate("getComputedStyle(document.getElementById('heroBg')).display"))
        self.page.emulate_media(media="screen", forced_colors="active")
        self.assertEqual("none", self.page.evaluate("getComputedStyle(document.getElementById('heroBg')).display"))
        self.page.emulate_media(media="screen", forced_colors="none")
        self.assertEqual("block", self.page.evaluate("getComputedStyle(document.getElementById('heroBg')).display"))


class StaleStylesheetTest(BackgroundCase):
    # Reduced motion, so the hero intro (which restarts when a stylesheet
    # is swapped in) cannot move a box mid-measurement.
    reduced_motion = "reduce"

    def test_the_hero_holds_its_layout_under_an_older_stylesheet(self) -> None:
        # Nov 8, 2026: just after the deploy, the owner's browser ran the
        # new page with its cached stylesheet from before the background.
        # Styled by nothing, the layer was a grid item: it took the hero's
        # first column, the text moved right, and the panel dropped below.
        # The versioned stylesheet link stops the mismatch; the layer's
        # inline position keeps the hero whole even if one happens.
        def boxes() -> dict:
            return self.page.evaluate(
                """() => { const r = s => document.querySelector(s).getBoundingClientRect(), h = r('.hero'), t = r('.hero-text'), d = r('.hero-side');
                     return {textLeft: Math.round(t.left - h.left), textTop: Math.round(t.top - h.top), sideTop: Math.round(d.top - h.top), sideLeft: Math.round(d.left - h.left)}; }"""
            )

        current = boxes()
        older = re.sub(r"[^{}]*#heroBg[^{}]*\{[^{}]*\}", "", (ROOT / "style.css").read_text(encoding="utf-8"))
        older = older.replace(".hero{position:relative;", ".hero{")
        self.assertNotIn("heroBg", older)
        self.page.evaluate(
            """css => { document.querySelector('link[rel=stylesheet]').remove(); const s = document.createElement('style'); s.textContent = css; document.head.appendChild(s); }""",
            older,
        )
        self.page.wait_for_timeout(200)
        self.assertEqual(current, boxes())
        layer = self.page.evaluate("(() => { const b = document.getElementById('heroBg'); return [getComputedStyle(b).position, getComputedStyle(b).zIndex]; })()")
        self.assertEqual(["absolute", "-1"], layer)


class DesktopLightTest(BackgroundCase):
    color_scheme = "light"

    def test_plays_the_light_desktop_file_and_nothing_else(self) -> None:
        self.wait_for_last_call("play")
        self.assertEqual("assets/hero-network-light.mp4", self.src())
        self.page.wait_for_timeout(500)
        self.assertEqual(["hero-network-light.mp4"], self.videos_asked_for())
        self.assertEqual(["hero-network-light.webp"], self.stills_asked_for())


class PhoneTest(BackgroundCase):
    viewport = {"width": 390, "height": 844}

    def test_plays_the_narrow_file_and_nothing_else(self) -> None:
        self.wait_for_last_call("play")
        self.assertEqual("assets/hero-network-dark-narrow.mp4", self.src())
        self.page.wait_for_timeout(500)
        self.assertEqual(["hero-network-dark-narrow.mp4"], self.videos_asked_for())
        self.assertEqual(["hero-network-dark-narrow.webp"], self.stills_asked_for())

    def test_is_a_band_about_one_screen_high(self) -> None:
        box = self.page.evaluate(
            "(() => { const b = document.getElementById('heroBg').getBoundingClientRect(); return {top: b.top + scrollY, bottom: b.bottom + scrollY, left: b.left, right: b.right, vw: document.documentElement.clientWidth, vh: innerHeight}; })()"
        )
        self.assertLessEqual(box["top"], 0)
        self.assertLessEqual(box["left"], 0)
        self.assertGreaterEqual(box["right"], box["vw"])
        self.assertGreaterEqual(box["bottom"], box["vh"])
        self.assertLessEqual(box["bottom"], 1100)
        widths = self.page.evaluate("[document.documentElement.scrollWidth, document.body.scrollWidth, innerWidth]")
        self.assertLessEqual(max(widths[:2]), widths[2])


class ReducedMotionTest(BackgroundCase):
    reduced_motion = "reduce"

    def test_shows_the_still_and_downloads_no_video(self) -> None:
        self.page.wait_for_timeout(1200)
        self.assertIsNone(self.src())
        self.assertEqual([], self.videos_asked_for())
        self.assertIn("hero-network-dark.webp", self.still())
        self.wait_for_still_shown()
        # Shown at once: no fade under reduced motion.
        self.assertEqual("0s", self.page.evaluate("getComputedStyle(document.getElementById('heroBg'), '::before').transitionDuration"))
        self.assertEqual("1", self.page.evaluate("getComputedStyle(document.getElementById('heroBg'), '::before').opacity"))
        self.assertFalse(self.showing_video())
        self.assertEqual("0", self.page.evaluate("getComputedStyle(document.getElementById('heroBgVideo')).opacity"))

    def test_theme_flip_still_downloads_no_video(self) -> None:
        self.flip_theme()
        self.page.wait_for_timeout(800)
        self.assertIsNone(self.src())
        self.assertEqual([], self.videos_asked_for())
        self.assertIn("hero-network-light.webp", self.still())


class StoredReduceMotionTest(BackgroundCase):
    def open_page(self, suffix: str = "") -> None:
        # A returning visitor who chose Reduce motion in the footer.
        self.context.add_init_script("try { localStorage.setItem('motion', 'reduced'); } catch (e) {}")
        super().open_page(suffix)

    def test_downloads_no_video(self) -> None:
        self.page.wait_for_timeout(1200)
        self.assertIsNone(self.src())
        self.assertEqual([], self.videos_asked_for())


class NoScriptTest(BackgroundCase):
    def test_shows_the_dark_still_at_once_without_javascript(self) -> None:
        # No script means the dark theme; the <noscript> style shows the
        # still, and nothing can ask for a video.
        for width, still in ((1400, "hero-network-dark.webp"), (390, "hero-network-dark-narrow.webp")):
            with self.subTest(width=width):
                context = self.browser.new_context(viewport={"width": width, "height": 900}, java_script_enabled=False)
                asked: list[str] = []
                page = context.new_page()
                page.on("request", lambda r: asked.append(r.url))
                try:
                    page.goto(self.page.url, wait_until="load")
                    bg = page.locator("#heroBg")
                    image = bg.evaluate("el => getComputedStyle(el, '::before').backgroundImage")
                    opacity = bg.evaluate("el => getComputedStyle(el, '::before').opacity")
                    self.assertIn(still, image)
                    self.assertEqual("1", opacity)
                    self.assertTrue(any(u.endswith("/" + still) for u in asked))
                    self.assertFalse(any(u.endswith(".mp4") and "hero-network" in u for u in asked))
                finally:
                    context.close()


class SaveDataTest(BackgroundCase):
    connection = "({ saveData: true, effectiveType: '4g' })"

    def open_page(self, suffix: str = "") -> None:
        self.context.add_init_script(f"Object.defineProperty(navigator, 'connection', {{ get: () => {self.connection} }})")
        super().open_page(suffix)

    def test_shows_the_still_and_downloads_no_video(self) -> None:
        self.page.wait_for_timeout(1200)
        self.assertIsNone(self.src())
        self.assertEqual([], self.videos_asked_for())
        self.assertIn("hero-network-dark.webp", self.still())


class SlowConnectionTest(SaveDataTest):
    connection = "({ saveData: false, effectiveType: 'slow-2g' })"


# Contrast of the hero's text over the still, read in the page: the text is
# made transparent, the page is captured, and a canvas reads the pixels
# behind every line of each block. A block passes when 99% of those pixels
# give the text at least 4.5:1 (3:1 for large text, WCAG's 24px, or 18.66px
# bold), with 0.1 to spare. The still stands in for the whole loop: measured
# frame by frame (every 1/6 s) on Nov 8, 2026, at 1400 and 390px in both
# themes, no moment scored lower than the still. With no tint the phone
# checks fail in both themes and
# desktop fails in light; dark desktop holds 4.5:1 even untinted, so its
# tint is for calm, not legibility. A light narrow tint of 0.30 also fails.
TEXT_RECTS = r"""() => { const out = [];
  for (const sel of ['.hero .eyebrow', '.hero h1', '.hero .role', '.hero .hero-stack', '.hero .lede']) {
    document.querySelectorAll(sel).forEach((el, k) => {
      const rects = [], w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
      while (w.nextNode()) { const r = document.createRange(); r.selectNodeContents(w.currentNode);
        for (const b of r.getClientRects()) if (b.width > 2 && b.top >= 0 && b.bottom <= innerHeight) rects.push([b.left, b.top, b.width, b.height]); }
      const cs = getComputedStyle(el), size = parseFloat(cs.fontSize), bold = +cs.fontWeight >= 700;
      if (rects.length) out.push({name: sel.replace('.hero ', '') + (k ? ' ' + (k + 1) : ''), color: cs.color, need: (size >= 24 || (size >= 18.66 && bold)) ? 3 : 4.5, rects});
    }); }
  return out; }"""
MEASURE = r"""async ([png, blocks]) => {
  const img = new Image(); img.src = 'data:image/png;base64,' + png; await img.decode();
  const c = document.createElement('canvas'); c.width = img.naturalWidth; c.height = img.naturalHeight;
  const g = c.getContext('2d'); g.drawImage(img, 0, 0);
  const lin = v => { v /= 255; return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
  const lum = (r, gg, b) => 0.2126 * lin(r) + 0.7152 * lin(gg) + 0.0722 * lin(b);
  return blocks.map(bk => {
    const [r, gg, b] = bk.color.match(/[\d.]+/g).map(Number), lt = lum(r, gg, b), ratios = [];
    for (const [x, y, w, h] of bk.rects) {
      const d = g.getImageData(Math.round(x), Math.round(y), Math.max(1, Math.round(w)), Math.max(1, Math.round(h))).data;
      for (let i = 0; i < d.length; i += 4) { const l = lum(d[i], d[i + 1], d[i + 2]); ratios.push((Math.max(l, lt) + 0.05) / (Math.min(l, lt) + 0.05)); }
    }
    ratios.sort((a, b) => a - b);
    return {name: bk.name, need: bk.need, p1: ratios[Math.floor(ratios.length * 0.01)]};
  }); }"""


class ContrastCase(BackgroundCase):
    reduced_motion = "reduce"  # the still, which is also the video's first frame

    def contrast(self) -> list[dict]:
        self.wait_for_still_shown()
        blocks = self.page.evaluate(TEXT_RECTS)
        self.page.add_style_tag(content=".hero-text,.hero-text *{color:transparent!important;transition:none!important} #cursorBot{display:none!important}")
        self.page.wait_for_timeout(200)
        png = base64.b64encode(self.page.screenshot()).decode()
        return self.page.evaluate(MEASURE, [png, blocks])

    def test_text_keeps_its_contrast_over_the_still(self) -> None:
        results = self.contrast()
        self.assertGreaterEqual(len(results), 5)
        for r in results:
            with self.subTest(block=r["name"]):
                self.assertGreaterEqual(r["p1"], r["need"] + 0.1, r)


class ContrastLightTest(ContrastCase):
    color_scheme = "light"


class ContrastPhoneTest(ContrastCase):
    viewport = {"width": 390, "height": 844}


class ContrastPhoneLightTest(ContrastCase):
    viewport = {"width": 390, "height": 844}
    color_scheme = "light"


if __name__ == "__main__":
    unittest.main(verbosity=2)
