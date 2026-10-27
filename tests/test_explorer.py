"""Interactive lineage explorer behaviour."""

from __future__ import annotations

import unittest

from helpers import BrowserTestCase


class LineageExplorerTest(BrowserTestCase):
    def test_nine_nodes_and_hover_lights_only_connected_edges(self) -> None:
        nodes = self.page.locator("#lineageSvg .lnode")
        self.assertEqual(9, nodes.count())

        ingest = self.page.locator('#lineageSvg .lnode[data-node="ingest"]')
        ingest.scroll_into_view_if_needed()
        ingest.hover()
        self.page.wait_for_function(
            "() => document.getElementById('e-feed-ingest').classList.contains('lit')"
        )

        connected = self.page.locator("#e-feed-ingest")
        unrelated = self.page.locator("#e-lake-api")
        self.assertIn("lit", connected.get_attribute("class") or "")
        self.assertIn("dim", unrelated.get_attribute("class") or "")
        self.assertIn(
            "Ingest - first stage under our control.",
            self.page.locator("#lineageDetail").inner_text(),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
