import json
import unittest
from pathlib import Path

from plataforma_ltft.elemental_balance import (
    ElementalBalanceContract, calculate_elemental_balance,
    validate_elemental_balance_contract,
)
ROOT = Path(__file__).resolve().parents[1]


def demonstration() -> ElementalBalanceContract:
    payload = json.loads((ROOT / "examples" / "balanco_elementar_demonstracao.json").read_text(encoding="utf-8"))
    return ElementalBalanceContract(**payload)


class ElementalBalanceTests(unittest.TestCase):
    def test_demonstration_closes_carbon_hydrogen_and_oxygen(self):
        report = calculate_elemental_balance(demonstration())
        self.assertTrue(report["all_assessable_balances_accepted"])
        for element in ("C", "H", "O"):
            self.assertAlmostEqual(report["balances"][element]["closure_pct"], 100.0)
            self.assertEqual(report["balances"][element]["status"], "accepted")
            self.assertGreater(report["balances"][element]["closure_uncertainty_pct"], 0.0)

    def test_configurable_tolerance_rejects_imbalanced_carbon(self):
        contract = demonstration()
        outlet = dict(contract.outlet_molar_flow_mol_s)
        outlet["CH4"] = 0.1
        changed = ElementalBalanceContract(**{**contract.__dict__, "outlet_molar_flow_mol_s": outlet, "tolerance_pct": 1.0})
        report = calculate_elemental_balance(changed)
        self.assertEqual(report["balances"]["C"]["status"], "rejected")
        self.assertGreater(report["balances"]["C"]["absolute_deviation_pct"], 1.0)

    def test_mismatched_bases_and_unknown_species_are_rejected(self):
        contract = demonstration()
        invalid = ElementalBalanceContract(**{
            **contract.__dict__, "outlet_basis": "dry_gas",
            "outlet_molar_flow_mol_s": {**contract.outlet_molar_flow_mol_s, "C3H8": 0.1},
        })
        errors = validate_elemental_balance_contract(invalid)
        self.assertTrue(any("mesma base" in error for error in errors))
        self.assertTrue(any("C3H8" in error for error in errors))

    def test_hydrogen_and_oxygen_are_not_assessed_on_dry_basis(self):
        contract = demonstration()
        dry = ElementalBalanceContract(**{**contract.__dict__, "inlet_basis": "dry_gas", "outlet_basis": "dry_gas"})
        report = calculate_elemental_balance(dry)
        self.assertEqual(report["balances"]["H"]["status"], "not_assessable_on_dry_basis")
        self.assertEqual(report["balances"]["O"]["status"], "not_assessable_on_dry_basis")

    def test_uncertainty_for_unknown_species_is_rejected(self):
        contract = demonstration()
        invalid = ElementalBalanceContract(**{
            **contract.__dict__,
            "inlet_molar_flow_uncertainty_mol_s": {"unknown": 0.1},
        })
        self.assertTrue(any("espécie ausente" in error for error in validate_elemental_balance_contract(invalid)))

