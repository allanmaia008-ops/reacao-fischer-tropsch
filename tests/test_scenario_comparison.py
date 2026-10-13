import unittest

from plataforma_ltft.scenario_comparison import compare_asf_scenarios


class ScenarioComparisonTests(unittest.TestCase):
    def test_compares_two_or_three_scenarios_on_same_basis(self):
        comparison = compare_asf_scenarios([0.80, 0.85, 0.90], "C12-C20")
        self.assertEqual(len(comparison["summaries"]), 3)
        self.assertEqual(len(comparison["curve"]), 180)
        self.assertEqual(comparison["basis"], "fracao_do_carbono_nos_hidrocarbonetos")
        self.assertTrue(comparison["recommendation_blocked"])

    def test_rejects_wrong_count_and_duplicate_alpha(self):
        with self.assertRaises(ValueError):
            compare_asf_scenarios([0.85], "C12-C20")
        with self.assertRaises(ValueError):
            compare_asf_scenarios([0.85, 0.85], "C12-C20")


if __name__ == "__main__":
    unittest.main()
