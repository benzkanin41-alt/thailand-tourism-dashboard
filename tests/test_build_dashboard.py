from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "work"))

import build_dashboard


class CountryDetailTemplateTests(unittest.TestCase):
    def test_country_detail_panel_has_required_interactions(self) -> None:
        template = build_dashboard.HTML_TEMPLATE

        for marker in [
            'id="countryDetailPanel"',
            'id="countryRankTable"',
            'id="countryMonthlyTable"',
            "data-country-select=",
            "function renderCountryDetail()",
            "function countrySnapshot()",
            ".country-summary { grid-template-columns: 1fr; }",
            "overflow-wrap: anywhere;",
        ]:
            self.assertIn(marker, template)


if __name__ == "__main__":
    unittest.main()
