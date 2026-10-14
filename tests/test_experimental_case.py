import json
import unittest
from pathlib import Path

from plataforma_ltft import LTFTCase, experimental_case_summary, migrate_case_v1_to_v2


ROOT = Path(__file__).resolve().parents[1]


def complete_case() -> LTFTCase:
    payload = json.loads((ROOT / "examples" / "caso_experimental_completo.json").read_text(encoding="utf-8"))
    return LTFTCase(**migrate_case_v1_to_v2(payload["case"]))


class ExperimentalCaseTests(unittest.TestCase):
    def test_complete_case_has_all_groups_and_plan_gate(self):
        summary = experimental_case_summary(complete_case())
        self.assertEqual(
            set(summary["groups"]),
            {"catalyst_and_activation", "reactor", "feed", "operating_conditions", "scientific_scope"},
        )
        self.assertTrue(summary["readiness"]["valid_for_experimental_plan"])
        self.assertFalse(summary["readiness"]["valid_for_rate_calculation"])
        self.assertEqual(summary["record_status"], "planned_case_not_experimental_evidence")

    def test_fingerprint_is_deterministic_and_sensitive_to_inputs(self):
        case = complete_case()
        first = experimental_case_summary(case)["case_fingerprint_sha256"]
        second = experimental_case_summary(case)["case_fingerprint_sha256"]
        changed = LTFTCase(**{**case.__dict__, "time_on_stream_h": 48})
        self.assertEqual(first, second)
        self.assertNotEqual(first, experimental_case_summary(changed)["case_fingerprint_sha256"])

    def test_summary_never_invents_experimental_outputs(self):
        outputs = experimental_case_summary(complete_case())["outputs"]
        self.assertTrue(all(value is None for value in outputs.values()))

