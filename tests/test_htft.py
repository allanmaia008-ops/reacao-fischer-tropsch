import unittest
from plataforma_ltft.htft import route_model, validate_htft_case

class HTFTTests(unittest.TestCase):
    def test_valid_htft_case_routes_to_diagnostic_only(self):
        case = {"case_id":"HT-001","desired_product":"C5-C12","temperature_c":320,"catalyst_family":"Fe","oxygenate_policy":"track","coke_tracking":"required","secondary_reactions":["wgs"]}
        report = route_model(case)
        self.assertTrue(report["valid"])
        self.assertEqual(report["model_family"], "HTFT_diagnostic")
        self.assertFalse(report["ltft_execution_allowed"])

    def test_ltft_temperature_is_rejected(self):
        case = {"case_id":"HT-002","desired_product":"C5-C12","temperature_c":220,"catalyst_family":"Fe","oxygenate_policy":"track","coke_tracking":"required","secondary_reactions":[]}
        self.assertTrue(validate_htft_case(case))
