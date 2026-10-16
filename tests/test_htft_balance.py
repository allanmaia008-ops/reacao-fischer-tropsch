import json
from pathlib import Path
import unittest
from plataforma_ltft.htft_balance import calculate_htft_balance

ROOT = Path(__file__).resolve().parents[1]

class HTFTBalanceTests(unittest.TestCase):
    def case(self): return json.loads((ROOT/'examples/htft_balance_closed_v1.json').read_text(encoding='utf-8'))

    def test_closes_carbon_hydrogen_oxygen_with_co2_water_and_coke(self):
        result = calculate_htft_balance(self.case())
        self.assertEqual(result['status'], 'closed')
        self.assertTrue(result['co2_water_coke_measured'])
        self.assertTrue(all(v['within_tolerance'] for v in result['balances'].values()))

    def test_unidentified_and_missing_water_force_review(self):
        case = self.case(); del case['outlet']['species_mol_h']['H2O']; case['outlet']['unidentified_atoms_mol_h']={'C':1}
        result = calculate_htft_balance(case)
        self.assertEqual(result['status'], 'review_required')
        self.assertFalse(result['co2_water_coke_measured'])

    def test_ltft_and_negative_flow_are_rejected(self):
        case = self.case(); case['regime']='LTFT'
        with self.assertRaises(ValueError): calculate_htft_balance(case)
        case = self.case(); case['inlet']['species_mol_h']['CO']=-1
        with self.assertRaises(ValueError): calculate_htft_balance(case)
