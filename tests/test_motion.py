"""Motion behaviour for the bot and the animated lineage core."""

from __future__ import annotations

import re
import unittest

from helpers import BrowserTestCase


def core_frame(page) -> str:
    return page.evaluate("() => document.getElementById('coreAnim').toDataURL()")


def bot_sleep_state(page) -> dict[str, str]:
    """The corner friend asleep: dimmed, "z z" showing, no breathing, standing straight."""
    return page.evaluate(
        """() => ({
            zz: getComputedStyle(document.querySelector('#cursorBot .bot-zz')).display,
            dimmed: getComputedStyle(document.querySelector('#cursorBot .bot-face')).filter !== 'none',
            breathing: getComputedStyle(document.querySelector('#cursorBot .bot-float')).animationName,
            lean: document.querySelector('#cursorBot .bot-head').style.transform
        })"""
    )


ASLEEP = {"zz": "block", "dimmed": True, "breathing": "none", "lean": ""}

# Records every class the corner friend takes on, from page load.
MOOD_LOG = """
window.__moods = [];
document.addEventListener('DOMContentLoaded', () => {
  const b = document.getElementById('cursorBot');
  new MutationObserver(() => { for (const c of b.classList) window.__moods.push(c); })
    .observe(b, { attributes: true, attributeFilter: ['class'] });
});
"""


def bot_center(page) -> tuple[float, float]:
    box = page.locator("#cursorBot").bounding_box()
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


class NormalMotionTest(BrowserTestCase):
    def open_page(self, suffix: str = "") -> None:
        self.context.add_init_script(MOOD_LOG)
        super().open_page(suffix)

    def test_bot_leans_and_shifts_toward_the_pointer(self) -> None:
        head = self.page.locator("#cursorBot .bot-head")

        def pose_after_move(x: int, y: int) -> tuple[float, float]:
            # Wait for him to settle (his pose unchanged for 250ms), not a
            # fixed time: a busy machine draws fewer frames. The check is
            # synchronous on purpose: wait_for_function treats a returned
            # promise as truthy and stops at once.
            self.page.mouse.move(x, y, steps=12)
            self.page.evaluate("window.__pose = null")
            self.page.wait_for_function(
                """() => { const t = document.querySelector('#cursorBot .bot-head').style.transform, now = performance.now();
                     if (!window.__pose || window.__pose.t !== t) { window.__pose = {t, since: now}; return false; }
                     return now - window.__pose.since > 250; }""",
                polling=50, timeout=6000,
            )
            transform = head.evaluate("el => el.style.transform")
            match = re.search(r"translate\((-?[0-9.]+)px, (-?[0-9.]+)px\) rotate\((-?[0-9.]+)deg\)", transform)
            self.assertIsNotNone(match, transform)
            return float(match.group(1)), float(match.group(3))

        left_shift, left_lean = pose_after_move(90, 110)
        right_shift, right_lean = pose_after_move(1390, 110)
        self.assertLess(left_shift, 0)
        self.assertLess(left_lean, 0)
        self.assertGreater(right_shift, 0)
        self.assertGreater(right_lean, 0)

    def test_bot_laughs_when_the_pointer_comes_near(self) -> None:
        # Away from him nothing happens; within 140px his eyes squint into
        # crescents and he hops, and the crescents show while he laughs.
        self.page.mouse.move(200, 200)
        self.page.wait_for_timeout(300)
        self.assertNotIn("happy", self.page.evaluate("window.__moods"))
        x, y = bot_center(self.page)
        self.page.mouse.move(x - 60, y - 60, steps=6)
        # While he laughs, the crescents fade fully in and he hops. Waited
        # for, not timed: on a slow frame the 0.14s fade is still under way.
        self.page.wait_for_function(
            """() => { const b = document.getElementById('cursorBot');
                 return b.classList.contains('happy')
                   && getComputedStyle(b.querySelector('.bot-squint')).opacity === '1'
                   && getComputedStyle(b.querySelector('.bot-hop')).animationName === 'bot-hop'; }""",
            timeout=2500,
        )
        self.page.wait_for_function("!document.getElementById('cursorBot').classList.contains('happy')", timeout=3000)

    def test_bot_blinks_and_the_lids_hide_between_blinks(self) -> None:
        # The painted lids cover the drawing's eyes only during a blink.
        # Read in one step with "no blink under way": read separately, a
        # blink could start between the two.
        self.page.wait_for_function(
            """() => !document.getElementById('cursorBot').className
                 && [...document.querySelectorAll('#cursorBot .bot-blink, #cursorBot .bot-squint')].every(g => getComputedStyle(g).opacity === '0')""",
            timeout=3000,
        )
        self.page.wait_for_function("window.__moods.includes('blink')", timeout=7000)

    def test_core_canvas_draws_changing_frames(self) -> None:
        first = core_frame(self.page)
        self.page.wait_for_timeout(500)
        second = core_frame(self.page)
        self.assertNotEqual(first, second)

    def test_footer_toggle_puts_the_bot_to_sleep(self) -> None:
        self.page.mouse.move(90, 110, steps=6)
        self.page.wait_for_timeout(600)
        self.page.evaluate("document.getElementById('motionBtn').click()")
        self.assertEqual("reduced", self.page.locator("html").get_attribute("data-motion"))
        self.page.wait_for_timeout(400)
        self.assertEqual(ASLEEP, bot_sleep_state(self.page))
        # Asleep, the pointer coming near does not wake him.
        x, y = bot_center(self.page)
        self.page.evaluate("window.__moods = []")
        self.page.mouse.move(x - 40, y - 40, steps=6)
        self.page.wait_for_timeout(400)
        self.assertEqual([], self.page.evaluate("window.__moods"))
        # Motion back on: he leans again, one loop, not two.
        self.page.evaluate("document.getElementById('motionBtn').click()")
        self.page.mouse.move(90, 110, steps=6)
        self.page.wait_for_timeout(900)
        self.assertIn("rotate(", self.page.evaluate("document.querySelector('#cursorBot .bot-head').style.transform"))


class ReducedMotionTest(BrowserTestCase):
    reduced_motion = "reduce"

    def test_emulated_reduced_motion_stills_the_core_and_sleeps_bot(self) -> None:
        self.page.evaluate("() => window.scrollTo(0, 0)")
        self.page.wait_for_timeout(300)

        first_core = core_frame(self.page)
        self.page.wait_for_timeout(700)
        second_core = core_frame(self.page)

        self.assertEqual(first_core, second_core)

        self.assertEqual(ASLEEP, bot_sleep_state(self.page))
        x, y = bot_center(self.page)
        self.page.mouse.move(x - 40, y - 40, steps=6)
        self.page.wait_for_timeout(400)
        self.assertFalse(self.page.evaluate("document.getElementById('cursorBot').classList.contains('happy')"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
