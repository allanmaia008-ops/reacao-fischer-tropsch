import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from plataforma_ltft.advanced_asf import (
    AdvancedASFContract,
    advanced_carbon_fraction,
    advanced_distribution,
    advanced_tail_fraction,
    validate_advanced_asf_contract,
)
from plataforma_ltft.asf import carbon_fraction


class AdvancedASFTests(unittest.TestCase):
    def test_single_matches_reference_asf(self):
        contract = AdvancedASFContract(model_type="single", alpha=0.85)
        for carbon_number in (1, 2, 10, 60):
            self.assertAlmostEqual(
                advanced_carbon_fraction(contract, carbon_number),
                carbon_fraction(0.85, carbon_number),
            )

    def test_dual_mixture_closes_with_analytic_tail(self):
        contract = AdvancedASFContract(
            model_type="dual_mixture", alpha_1=0.72, alpha_2=0.88,
            mixture_fraction=0.35,
        )
        report = advanced_distribution(contract, max_carbon=40)
        self.assertAlmostEqual(report["closure"], 1.0)
        self.assertGreater(report["tail"]["carbon_fraction"], 0)

    def test_segmented_distribution_is_independent_of_display_cutoff(self):
        contract = AdvancedASFContract(
            model_type="segmented", alpha_1=0.72, alpha_2=0.9,
            transition_carbon=10,
        )
        short = advanced_distribution(contract, max_carbon=20)
        long = advanced_distribution(contract, max_carbon=60)
        for index in range(20):
            self.assertAlmostEqual(
                short["points"][index]["carbon_fraction"],
                long["points"][index]["carbon_fraction"],
            )
        self.assertAlmostEqual(short["closure"], 1.0)
        self.assertAlmostEqual(long["closure"], 1.0)

    def test_c1_and_c2_corrections_are_explicit_and_renormalized(self):
        base = AdvancedASFContract(model_type="single", alpha=0.8)
        corrected = AdvancedASFContract(
            model_type="single", alpha=0.8, methane_factor=1.5, c2_factor=0.5,
        )
        self.assertGreater(advanced_carbon_fraction(corrected, 1), advanced_carbon_fraction(base, 1))
        self.assertLess(advanced_carbon_fraction(corrected, 2), advanced_carbon_fraction(base, 2))
        self.assertAlmostEqual(advanced_tail_fraction(corrected, 1), 1.0)

    def test_conditional_parameters_are_validated(self):
        invalid = AdvancedASFContract(
            model_type="dual_mixture", alpha_1=0.7, alpha_2=0.9,
            mixture_fraction=None, transition_carbon=10,
        )
        errors = validate_advanced_asf_contract(invalid)
        self.assertTrue(any("mixture_fraction" in error for error in errors))
        self.assertTrue(any("transition_carbon" in error for error in errors))
