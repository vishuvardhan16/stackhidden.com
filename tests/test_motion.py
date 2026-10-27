"""Motion behaviour for the bot and the animated lineage core."""

from __future__ import annotations

import re
import unittest

from helpers import BrowserTestCase


def core_frame(page) -> str:
    return page.evaluate("() => document.getElementById('coreAnim').toDataURL()")


def bot_display_state(page) -> dict[str, str]:
    return page.evaluate(
        """() => ({
            pupil: getComputedStyle(document.querySelector('#cursorBot .bot-pupil')).display,
            closed: getComputedStyle(document.querySelector('#cursorBot .bot-closed')).display
        })"""
    )


class NormalMotionTest(BrowserTestCase):
    def test_bot_pupils_move_toward_the_pointer(self) -> None:
        pupil = self.page.locator("#cursorBot .bot-pupil").first

        def gaze_after_move(x: int, y: int) -> tuple[float, float]:
            self.page.mouse.move(x, y, steps=12)
            self.page.wait_for_timeout(900)
            transform = pupil.get_attribute("transform")
            self.assertIsNotNone(transform)
            match = re.search(
                r"translate\((-?[0-9.]+)[ ,]+(-?[0-9.]+)\)", transform or ""
            )
            self.assertIsNotNone(match)
            return float(match.group(1)), float(match.group(2))

        left_x, left_y = gaze_after_move(90, 110)
        right_x, right_y = gaze_after_move(1390, 110)

        self.assertLess(left_x, 0)
        self.assertGreater(right_x, 0)
        self.assertLess(left_y, 0)
        self.assertLess(right_y, 0)


    def test_core_canvas_draws_changing_frames(self) -> None:
        first = core_frame(self.page)
        self.page.wait_for_timeout(500)
        second = core_frame(self.page)
        self.assertNotEqual(first, second)

    def test_footer_toggle_puts_the_bot_to_sleep(self) -> None:
        self.page.click("#motionBtn")
        self.assertEqual(
            "reduced",
            self.page.locator("html").get_attribute("data-motion"),
        )
        self.page.evaluate("() => window.scrollTo(0, 0)")
        self.page.wait_for_timeout(400)

        display = bot_display_state(self.page)
        self.assertEqual("none", display["pupil"])
        self.assertEqual("block", display["closed"])


class ReducedMotionTest(BrowserTestCase):
    reduced_motion = "reduce"

    def test_emulated_reduced_motion_stills_the_core_and_sleeps_bot(self) -> None:
        self.page.evaluate("() => window.scrollTo(0, 0)")
        self.page.wait_for_timeout(300)

        first_core = core_frame(self.page)
        self.page.wait_for_timeout(700)
        second_core = core_frame(self.page)

        self.assertEqual(first_core, second_core)

        display = bot_display_state(self.page)
        self.assertEqual("none", display["pupil"])
        self.assertEqual("block", display["closed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
