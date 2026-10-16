import unittest
from plataforma_ltft.applicability import assess_case_applicability, assess_case_compatibility
from plataforma_ltft.domain import LTFTCase

class ApplicabilityTests(unittest.TestCase):
    def test_current_corpus_gate_blocks_even_contextual_case(self):
        case = LTFTCase(active_family="Co", temperature_c=220, pressure_bar=20, h2_co_molar_ratio=2)
        report = assess_case_compatibility(case)
        self.assertEqual(report["compatibility"], "not_demonstrated")
        self.assertEqual(report["approval_status"], "approved_for_internal_contextual_use")
        self.assertTrue(report["recommendation_blocked"])
        self.assertEqual(report["approval_status"], "approved_for_internal_contextual_use")

    def test_out_of_domain_temperature_is_alerted(self):
        case = LTFTCase(active_family="Co", temperature_c=300, pressure_bar=20, h2_co_molar_ratio=2)
        report = assess_case_applicability(case, evidence_approved=True)
        self.assertEqual(report["status"], "blocked")
        self.assertTrue(any("HTFT" in alert for alert in report["alerts"]))
