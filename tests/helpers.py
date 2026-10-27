"""Shared browser-test support for the stackhidden.com test suite.

The site has no build step and no application server of its own.  Locally,
tests therefore load the repository's index.html through a file:// URL.  CI
sets BASE_URL to a disposable local HTTP server instead; the tests do not
care which transport delivered the same three site files.
"""

from __future__ import annotations

import os
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
LOCAL_CHROMIUM = (
    Path.home()
    / ".cache/ms-playwright/chromium_headless_shell-1248"
    / "chrome-headless-shell-linux64/chrome-headless-shell"
)


def chromium_launch_kwargs() -> dict[str, str]:
    """Return the local Chromium path when present.

    The development VM pins a Playwright headless-shell build.  CI installs
    its own Chromium with ``playwright install``, so a missing pinned path
    must fall back to Playwright's normal browser discovery.
    """

    configured = os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
    if configured:
        return {"executable_path": configured}
    if LOCAL_CHROMIUM.exists():
        return {"executable_path": str(LOCAL_CHROMIUM)}
    return {}


def page_url(suffix: str = "") -> str:
    """Build the page URL from BASE_URL, or the local file by default."""

    base_url = os.environ.get("BASE_URL")
    if base_url:
        if base_url.endswith((".html", "/")):
            return f"{base_url}{suffix}"
        return f"{base_url}/{suffix}"
    return f"{(ROOT / 'index.html').resolve().as_uri()}{suffix}"


class BrowserTestCase(unittest.TestCase):
    """A Playwright test case with page-error collection in every test."""

    viewport = {"width": 1400, "height": 900}
    color_scheme: str | None = None
    reduced_motion: str | None = None
    page_suffix = ""

    @classmethod
    def setUpClass(cls) -> None:
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(
            **chromium_launch_kwargs(),
            args=["--no-sandbox"],
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self) -> None:
        context_options: dict[str, object] = {"viewport": self.viewport}
        if self.color_scheme is not None:
            context_options["color_scheme"] = self.color_scheme
        if self.reduced_motion is not None:
            context_options["reduced_motion"] = self.reduced_motion

        self.context = self.browser.new_context(**context_options)
        self.page = self.context.new_page()
        self.page.set_default_timeout(7_500)
        self.page.set_default_navigation_timeout(15_000)
        self.page_errors: list[str] = []
        self.page.on("pageerror", lambda error: self.page_errors.append(str(error)))
        self.page.on(
            "console",
            lambda message: self.page_errors.append(message.text)
            if message.type == "error"
            else None,
        )
        self.open_page(self.page_suffix)

    def tearDown(self) -> None:
        errors = list(self.page_errors)
        self.context.close()
        if errors:
            raise AssertionError(f"Browser errors were reported: {errors}")

    def open_page(self, suffix: str = "") -> None:
        self.page.goto(page_url(suffix), wait_until="load")
        self.page.wait_for_timeout(300)

    def reload_page(self) -> None:
        self.page.reload(wait_until="load")
        self.page.wait_for_timeout(300)
