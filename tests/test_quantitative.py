import unittest
from plataforma_ltft.quantitative import one_at_a_time_sensitivity, quantitative_readiness

class QuantitativeTests(unittest.TestCase):
    def test_model_gate_blocks_without_external_validation(self):
        report = quantitative_readiness({"valid_for_rate_calculation": False, "blocking_reasons": ["draft"]}, external_validation=False, uncertainty_defined=False)
        self.assertEqual(report["status"], "blocked")
        self.assertTrue(report["recommendation_blocked"])

    def test_sensitivity_marks_out_of_range_point(self):
        report = one_at_a_time_sensitivity({"temperature_c": 220.0}, {"temperature_c": 50.0}, lambda x: x["temperature_c"] * 2, valid_ranges={"temperature_c": (180.0, 260.0)})
        self.assertFalse(report["rows"][0]["within_declared_range"])
        self.assertEqual(report["rows"][0]["local_sensitivity"], 2.0)
