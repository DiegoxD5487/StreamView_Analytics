"""Pruebas para la página de decisiones; los registros fuente no deben alterarse."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core import load_data, filter_data, portfolio_metrics
from analytics import (opportunities,comparable_movies,languages_for_chart,
                       most_common_genre,most_common_country)
ROOT=Path(__file__).resolve().parents[1]

class TestAnalytics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df=load_data(ROOT/'data'/'STREAMVIEW_POWERBI.csv')
    def test_top_categories(self):
        self.assertEqual(most_common_genre(self.df)[0],'Drama')
        self.assertEqual(most_common_country(self.df)[0],'United States of America')
    def test_country_changes_other_metrics(self):
        one=filter_data(self.df,country='Japan')
        two=filter_data(self.df,country='United States of America')
        self.assertTrue(0<len(one)<len(self.df))
        self.assertTrue(0<len(two)<len(self.df))
        self.assertNotEqual(portfolio_metrics(one)['total'],portfolio_metrics(two)['total'])
    def test_opportunity_has_explicit_coverage(self):
        table=opportunities(self.df,min_titles=100)
        self.assertTrue((table['Contenidos']>=100).all())
        self.assertTrue(table['Índice orientativo'].between(0,100).all())
    def test_finance_comparable_removes_symbolic_budgets(self):
        original=self.df.copy()
        films=comparable_movies(self.df,min_budget=1_000_000,min_votes=100)
        self.assertTrue((films['budget']>=1_000_000).all())
        self.assertTrue((films['vote_count']>=100).all())
        self.assertLess(float(films['multiplo'].max()),1000)
        self.assertTrue(self.df.equals(original))
    def test_minimum_language_sample(self):
        l=languages_for_chart(self.df,min_titles=30)
        self.assertTrue((l.contenidos>=30).all())
        self.assertTrue(l.idioma_etiqueta.str.contains(r'\(').all())

if __name__=='__main__':
    unittest.main()
