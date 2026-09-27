import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from plataforma_ltft import LTFTCase, validate_case


class DomainTests(unittest.TestCase):
    def test_missing_inputs_block_screening_and_rate(self):
        result = validate_case(LTFTCase())
        self.assertFalse(result.valid_for_screening)
        self.assertFalse(result.valid_for_experimental_plan)
        self.assertFalse(result.valid_for_rate_calculation)
        self.assertIn("active_family", result.missing_screening_fields)

    def test_complete_screening_still_does_not_claim_kinetics(self):
        case = LTFTCase(
            composition="Co", active_family="Co", active_phase_hypothesis="Co0 a confirmar",
            support="Al2O3", active_metal_loading_wt_pct=20, temperature_c=220,
            pressure_bar=20, h2_co_molar_ratio=2, desired_product="C12-C20",
        )
        result = validate_case(case)
        self.assertTrue(result.valid_for_screening)
        self.assertFalse(result.valid_for_experimental_plan)
        self.assertFalse(result.valid_for_rate_calculation)

    def test_invalid_family_and_units_are_rejected(self):
        case = LTFTCase(
            composition="Ni", active_family="Ni", active_phase_hypothesis="hipótese",
            support="SiO2", active_metal_loading_wt_pct=-5, temperature_c=220,
            pressure_bar=0, h2_co_molar_ratio=2, desired_product="produto inventado",
        )
        result = validate_case(case)
        self.assertFalse(result.valid_for_screening)
        self.assertGreaterEqual(len(result.errors), 4)

    def test_complete_experimental_contract_passes_plan_gate_not_kinetics(self):
        case = LTFTCase(
            composition="Co", active_family="Co", active_phase_hypothesis="Co0 a confirmar",
            support="Al2O3", active_metal_loading_wt_pct=20, promoter="Ru",
            promoter_loading_wt_pct=0.5, precursor="precursor registrado",
            activation_gas="H2", activation_temperature_c=400, activation_duration_h=10,
            reactor_type="leito fixo", temperature_c=220, pressure_bar=20,
            h2_co_molar_ratio=2, feed_composition_mol_fraction={"H2": 2/3, "CO": 1/3},
            feed_flow_mol_s=0.001, ghsv_h_1=500, bed_volume_ml=1,
            time_on_stream_h=24, desired_product="C12-C20",
        )
        result = validate_case(case)
        self.assertTrue(result.valid_for_screening)
        self.assertTrue(result.valid_for_experimental_plan)
        self.assertFalse(result.valid_for_rate_calculation)
        self.assertFalse(result.errors)

    def test_feed_and_space_velocity_cross_validation(self):
        case = LTFTCase(
            composition="Co", active_family="Co", active_phase_hypothesis="Co0",
            support="Al2O3", active_metal_loading_wt_pct=20, temperature_c=220,
            pressure_bar=20, h2_co_molar_ratio=2,
            feed_composition_mol_fraction={"H2": 0.5, "CO": 0.5},
            ghsv_h_1=500, desired_product="C5+",
        )
        result = validate_case(case)
        self.assertTrue(any("diverge" in error for error in result.errors))
        self.assertTrue(any("bed_volume_ml" in error for error in result.errors))

    def test_promoter_requires_loading(self):
        result = validate_case(LTFTCase(promoter="K"))
        self.assertIn("Promotor e promoter_loading_wt_pct devem ser informados juntos.", result.errors)


if __name__ == "__main__":
    unittest.main()
