import unittest
from plataforma_ltft.domain import LTFTCase
from plataforma_ltft.experimental_planning import generate_experimental_plan, validate_pilot_record

class ExperimentalPlanningTests(unittest.TestCase):
    def test_plan_requires_human_review(self):
        plan = generate_experimental_plan(LTFTCase(desired_product="C12-C20"))
        self.assertTrue(plan["review_required"])
        self.assertTrue(plan["recommendation_blocked"])

    def test_pilot_without_raw_data_is_blocked(self):
        report = validate_pilot_record({"pilot_id": "P-1", "protocol_id": "FT-026-1", "execution_confirmed": True})
        self.assertEqual(report["status"], "blocked")
        self.assertFalse(report["record_is_evidence"])
