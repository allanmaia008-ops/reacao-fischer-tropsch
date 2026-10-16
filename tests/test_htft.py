import json
import unittest
from pathlib import Path
from plataforma_ltft.htft import route_model, validate_htft_case

ROOT = Path(__file__).resolve().parents[1]


class HTFTTests(unittest.TestCase):
    def valid_case(self):
        return json.loads((ROOT / "examples/htft_light_olefins_v1.json").read_text(encoding="utf-8"))

    def test_valid_htft_case_routes_to_diagnostic_only(self):
        report = route_model(self.valid_case())
        self.assertTrue(report["valid"])
        self.assertEqual(report["model_family"], "HTFT_diagnostic")
        self.assertEqual(report["target"], "light_olefins_C2_C4")
        self.assertEqual(report["tracked_carbon_numbers"], [2, 3, 4])
        self.assertFalse(report["ltft_execution_allowed"])
        self.assertTrue(report["recommendation_blocked"])

    def test_ltft_temperature_and_cobalt_are_rejected(self):
        case = self.valid_case(); case["temperature_c"] = 220; case["catalyst"]["family"] = "Co"
        errors = validate_htft_case(case)
        self.assertTrue(any("280–350" in error for error in errors))
        self.assertTrue(any("catalyst.family" in error for error in errors))

    def test_required_metrics_reactions_and_gate_cannot_be_omitted(self):
        case = self.valid_case()
        case["analytics"]["coke"] = False
        case["analytics"]["olefin_paraffin_by_carbon"] = [2, 3]
        case["secondary_reactions"].remove("wgs")
        case["recommendation_blocked"] = False
        errors = validate_htft_case(case)
        self.assertTrue(any("analytics.coke" in error for error in errors))
        self.assertTrue(any("C2, C3 e C4" in error for error in errors))
        self.assertTrue(any("wgs" in error for error in errors))
        self.assertTrue(any("recommendation_blocked" in error for error in errors))
