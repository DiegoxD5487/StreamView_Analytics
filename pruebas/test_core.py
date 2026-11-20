"""Pruebas básicas de reproducibilidad de StreamView (stdlib unittest)."""
from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import load_data, filter_data, portfolio_metrics, genre_aggregates  # noqa: E402


class TestStreamView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = load_data(ROOT / "data" / "STREAMVIEW_POWERBI.csv")

    def test_catalog_unique_records(self):
        self.assertEqual(len(self.df), 31991)
        self.assertTrue(self.df.content_id.is_unique)

    def test_content_types(self):
        counts = portfolio_metrics(self.df)
        self.assertEqual(counts["movies"], 16000)
        self.assertEqual(counts["series"], 15991)

    def test_fundamental_metrics(self):
        counts = portfolio_metrics(self.df)
        self.assertTrue(math.isclose(counts["rating"], 5.6881186, rel_tol=1e-5))
        self.assertTrue(math.isclose(counts["popularity"], 42.6254292, rel_tol=1e-5))
        self.assertTrue(math.isclose(counts["revenue_budget_ratio"], 2.9165544, rel_tol=1e-5))
        self.assertEqual(counts["financial_titles"], 3540)

    def test_filters(self):
        self.assertEqual(len(filter_data(self.df, types=["Movie"])), 16000)
        self.assertEqual(len(filter_data(self.df, types=["TV Show"])), 15991)
        self.assertEqual(len(filter_data(self.df, types=[])), 0)
        self.assertGreater(len(filter_data(self.df, years=(2010, 2010))), 0)

    def test_aggregations(self):
        metrics = genre_aggregates(self.df)
        self.assertGreater(len(metrics), 10)
        self.assertEqual(metrics["contenidos"].sum() +
                         self.df.genre_principal.eq("No informado").sum(), len(self.df))


if __name__ == "__main__":
    unittest.main()
