import unittest

from plataforma_ltft.htft_validation import assess_htft_validation


class HTFTValidationTests(unittest.TestCase):
    def test_incomplete_validation_stays_blocked(self):
        result = assess_htft_validation({"regime": "HTFT", "model": {"model_id": "m", "version": "0", "frozen": False},
                                         "external_dataset": {"dataset_id": "d", "row_count": 0},
                                         "evaluation": {"metrics": ["conversion"]}, "independent_review": {"status": "pending"}})
        self.assertFalse(result["validation_gate_passed"])
        self.assertIn("model_not_frozen", result["reasons"])
        self.assertIn("independent_review_not_approved", result["reasons"])
        self.assertTrue(result["recommendation_blocked"])

    def test_complete_contract_passes_gate_but_not_auto_recommendation(self):
        result = assess_htft_validation({"regime": "HTFT", "model": {"model_id": "m", "version": "1", "frozen": True},
            "external_dataset": {"dataset_id": "external", "row_count": 5, "independent_from_calibration": True, "compatibility_review": "accepted"},
            "evaluation": {"metrics": ["conversion"], "uncertainty_method": "bootstrap", "residual_analysis": True},
            "independent_review": {"independent": True, "reviewer_id": "reviewer-1", "status": "approved"}})
        self.assertTrue(result["validation_gate_passed"])
        self.assertFalse(result["automatic_recommendation_allowed"])


if __name__ == "__main__": unittest.main()
