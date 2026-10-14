import json
import unittest
from pathlib import Path

from plataforma_ltft.asf_measurement import (
    ASFMeasurementContract,
    compare_asf_to_measurement,
    validate_asf_measurement_contract,
)

ROOT = Path(__file__).resolve().parents[1]


def demonstration() -> ASFMeasurementContract:
    payload = json.loads((ROOT / "examples" / "comparacao_asf_medicao_sintetica.json").read_text(encoding="utf-8"))
    return ASFMeasurementContract(**payload)


class ASFMeasurementTests(unittest.TestCase):
    def test_synthetic_band_comparison_reports_residuals_and_uncertainty(self):
        report = compare_asf_to_measurement(demonstration())
        self.assertEqual(report["metrics"]["point_count"], 5)
        self.assertEqual(report["metrics"]["closure_status"], "accepted")
        self.assertIsNotNone(report["metrics"]["chi_square"])
        self.assertIsNotNone(report["diagnostics"]["C1_residual"])
        self.assertIsNotNone(report["diagnostics"]["tail_residual"])
        self.assertFalse(report["allowed_for_model_validation"])
        self.assertTrue(report["recommendation_blocked"])

    def test_approved_complete_distribution_can_be_used_for_validation(self):
        contract = demonstration()
        approved = ASFMeasurementContract(**{**contract.__dict__, "evidence_status": "approved"})
        self.assertTrue(compare_asf_to_measurement(approved)["allowed_for_model_validation"])

    def test_partial_carbon_number_distribution_does_not_claim_closure(self):
        contract = ASFMeasurementContract(
            comparison_id="partial",
            alpha=0.8,
            representation="carbon_number",
            measured_fractions={"C1": 0.05, "C2": 0.04},
            measurement_basis="carbon_fraction_hydrocarbons",
            evidence_status="verified",
            source_ids=("source-1",),
        )
        report = compare_asf_to_measurement(contract)
        self.assertEqual(report["metrics"]["closure_status"], "not_assessable_partial_distribution")
        self.assertIsNotNone(report["diagnostics"]["C2_residual"])

    def test_incompatible_basis_and_uncertainty_without_measurement_are_rejected(self):
        contract = demonstration()
        invalid = ASFMeasurementContract(**{
            **contract.__dict__,
            "measurement_basis": "mass_fraction",
            "measured_uncertainty": {"C60": 0.1},
        })
        errors = validate_asf_measurement_contract(invalid)
        self.assertTrue(any("measurement_basis" in error for error in errors))
        self.assertTrue(any("sem medição" in error for error in errors))

    def test_labels_must_match_representation(self):
        contract = demonstration()
        invalid = ASFMeasurementContract(**{
            **contract.__dict__, "representation": "carbon_number"
        })
        self.assertTrue(any("Rótulos incompatíveis" in error for error in validate_asf_measurement_contract(invalid)))
