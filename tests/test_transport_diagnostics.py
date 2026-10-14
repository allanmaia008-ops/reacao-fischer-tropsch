import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from plataforma_ltft.transport_diagnostics import (
    TransportDiagnosticsContract, assess_transport_diagnostics,
    validate_transport_diagnostics_contract,
)


def complete_contract(**changes):
    values = dict(
        observed_rate_mol_m3_s=0.01, particle_radius_m=5e-5,
        surface_reactant_concentration_mol_m3=10.0,
        bulk_reactant_concentration_mol_m3=10.0,
        effective_diffusivity_m2_s=1e-6, reaction_order_abs=1.0,
        external_mass_transfer_coefficient_m_s=0.1,
        reaction_enthalpy_abs_j_mol=165000.0, activation_energy_j_mol=80000.0,
        temperature_k=493.15, external_heat_transfer_coefficient_w_m2_k=1000.0,
        source_ids=("synthetic-test",),
    )
    values.update(changes)
    values["field_sources"] = {name: "synthetic-test" for name, value in values.items() if name not in {"source_ids", "relative_uncertainty_fraction"} and value is not None}
    return TransportDiagnosticsContract(**values)


class TransportDiagnosticsTests(unittest.TestCase):
    def test_complete_low_rate_case_passes_all_screening_criteria(self):
        report = assess_transport_diagnostics(complete_contract())
        self.assertEqual(report["overall_status"], "passed_all_assessed")
        self.assertTrue(report["all_transport_criteria_passed"])
        self.assertFalse(report["kinetic_interpretation_approved"])
        self.assertAlmostEqual(report["criteria"]["weisz_prater"]["value"], 2.5e-6)
        self.assertAlmostEqual(report["criteria"]["mears_mass"]["value"], 5.0e-7)
        expected_heat = 165000.0 * 0.01 * 5e-5 * 80000.0 / (1000.0 * 8.314462618 * 493.15**2)
        self.assertAlmostEqual(report["criteria"]["mears_heat"]["value"], expected_heat)

    def test_high_rate_case_fails_and_does_not_release_recommendation(self):
        report = assess_transport_diagnostics(complete_contract(observed_rate_mol_m3_s=1000.0))
        self.assertEqual(report["overall_status"], "failed")
        self.assertTrue(any(item["status"] == "failed" for item in report["criteria"].values()))
        self.assertTrue(report["recommendation_blocked"])

    def test_missing_inputs_are_not_interpreted_as_pass(self):
        contract = TransportDiagnosticsContract(source_ids=("planned-case",), field_sources={})
        report = assess_transport_diagnostics(contract)
        self.assertEqual(report["overall_status"], "incomplete")
        self.assertTrue(all(item["status"] == "not_assessable_missing_inputs" for item in report["criteria"].values()))

    def test_invalid_values_and_missing_provenance_are_rejected(self):
        contract = TransportDiagnosticsContract(observed_rate_mol_m3_s=-1, source_ids=("source",), field_sources={})
        errors = validate_transport_diagnostics_contract(contract)
        self.assertTrue(any("positivo" in error for error in errors))
        self.assertTrue(any("field_sources" in error for error in errors))

    def test_uncertainty_interval_can_cross_limit(self):
        contract = complete_contract(
            observed_rate_mol_m3_s=0.1,
            relative_uncertainty_fraction={"effective_diffusivity_m2_s": 0.9},
        )
        report = assess_transport_diagnostics(contract)
        interval = report["criteria"]["weisz_prater"]["sensitivity_interval"]
        self.assertLess(interval["lower"], interval["upper"])
        self.assertAlmostEqual(report["criteria"]["weisz_prater"]["value"], 2.5e-5)

