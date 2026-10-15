import unittest
from plataforma_ltft.process_integration import economic_scenario, integrated_balance_gate, integrated_validation_gate

class ProcessIntegrationTests(unittest.TestCase):
    def test_balance_gate_requires_all_streams(self):
        report = integrated_balance_gate(syngas_closed=True, ft_closed=True, upgrading=False, oxygen_accounted=True)
        self.assertEqual(report["status"], "blocked")
        self.assertIn("upgrading", report["missing"])
    def test_economic_scenario_is_transparent(self):
        report = economic_scenario(capacity_kg_h=10, h2_cost_per_kg=2, electricity_cost_per_mwh=50, carbon_cost_per_t=0, capex=1000, opex_per_kg=1, product_price_per_kg=8)
        self.assertEqual(report["margin_per_h"], 50)
    def test_validation_gate_blocks_without_external_review(self):
        report = integrated_validation_gate(external_dataset=True, residuals_checked=True, uncertainty_checked=True, independent_review=False)
        self.assertEqual(report["status"], "blocked")
