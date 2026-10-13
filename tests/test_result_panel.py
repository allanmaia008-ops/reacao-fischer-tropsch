import unittest

from plataforma_ltft.result_panel import (
    DISPLAY_MAX_CARBON,
    carbon_curve,
    curve_closure,
    readiness_rows,
    target_bounds,
)


class ResultPanelTests(unittest.TestCase):
    def test_target_bounds_support_ranges_and_exact_carbon(self):
        self.assertEqual(target_bounds("C12-C20"), (12, 20))
        self.assertEqual(target_bounds("C21+"), (21, DISPLAY_MAX_CARBON))
        self.assertEqual(target_bounds("C37"), (37, 37))

    def test_curve_marks_only_the_selected_target(self):
        curve = carbon_curve(0.85, "C5-C11")
        self.assertEqual(len(curve), DISPLAY_MAX_CARBON)
        highlighted = [row["carbon_number"] for row in curve if row["target_group"] == "Faixa-alvo"]
        self.assertEqual(highlighted, list(range(5, 12)))
        self.assertTrue(all(row["carbon_fraction"] > 0 for row in curve))

    def test_curve_closes_with_analytic_infinite_tail(self):
        closure = curve_closure(0.85)
        self.assertGreater(closure["C1-C60"], 0)
        self.assertGreater(closure["C61+"], 0)
        self.assertAlmostEqual(closure["total"], 1.0, places=12)

    def test_readiness_is_presented_without_hiding_blocks(self):
        rows = readiness_rows({
            "valid_for_screening": True,
            "valid_for_experimental_plan": False,
            "valid_for_rate_calculation": False,
        })
        self.assertEqual(rows[0]["Estado"], "Disponível")
        self.assertEqual([row["Estado"] for row in rows[1:]], ["Bloqueado", "Bloqueado"])


if __name__ == "__main__":
    unittest.main()
