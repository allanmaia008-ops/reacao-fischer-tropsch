import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from plataforma_ltft import LTFTCase, build_target_plan, plan_product_target
from plataforma_ltft.product_targets import mathematical_alpha_orientation, normalize_target, target_fraction


class ProductTargetTests(unittest.TestCase):
    def test_aliases_and_exact_hydrocarbon(self):
        self.assertEqual(normalize_target("diesel"), "C12-C20")
        self.assertEqual(normalize_target("C8"), "C8")

    def test_exact_hydrocarbon_has_analytical_asf_optimum(self):
        orientation = mathematical_alpha_orientation("C8")
        self.assertAlmostEqual(orientation["finite_optimum"], 7 / 9, places=4)

    def test_band_optimum_beats_neighbouring_values(self):
        optimum = mathematical_alpha_orientation("C5-C11")["finite_optimum"]
        self.assertGreaterEqual(target_fraction(optimum, "C5-C11"), target_fraction(optimum - 0.02, "C5-C11"))
        self.assertGreaterEqual(target_fraction(optimum, "C5-C11"), target_fraction(optimum + 0.02, "C5-C11"))

    def test_plan_orients_but_blocks_final_recommendation(self):
        case = LTFTCase(active_family="Co", desired_product="C21+")
        plan = build_target_plan(case)
        self.assertTrue(plan["recommendation_blocked"])
        self.assertEqual(plan["asf_orientation"]["direction"], "aumentar_alpha")
        self.assertIn("Co", plan["catalyst_orientation"]["candidate_families"])

    def test_product_can_be_planned_before_catalyst(self):
        plan = plan_product_target("gasolina")
        self.assertEqual(plan["desired_product"], "C5-C11")
        self.assertIsNone(plan["catalyst_orientation"]["selected_family"])

    def test_invalid_target_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize_target("querosene puro")
