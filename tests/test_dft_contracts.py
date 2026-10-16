import json
from pathlib import Path
import unittest

from plataforma_ltft.dft_contracts import calculate_adsorption_energy, validate_structure_contract, validate_surface_protocol

ROOT = Path(__file__).resolve().parents[1]


class DFTContractTests(unittest.TestCase):
    def load(self, name): return json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))

    def test_structure_and_surface_examples_are_auditable(self):
        self.assertEqual(validate_structure_contract(self.load("dft_structure_synthetic_v1.json")), ())
        self.assertEqual(validate_surface_protocol(self.load("dft_surface_synthetic_v1.json")), ())

    def test_structure_requires_provenance_and_hash(self):
        item = self.load("dft_structure_synthetic_v1.json")
        item["structure_file"]["sha256"] = "bad"
        item["provenance"].pop("citation_or_uri")
        self.assertIn("invalid:structure_file.sha256", validate_structure_contract(item))
        self.assertIn("missing:provenance.citation_or_uri", validate_structure_contract(item))

    def test_adsorption_energy_requires_three_comparable_converged_runs(self):
        item = self.load("dft_adsorption_synthetic_v1.json")
        result = calculate_adsorption_energy(item)
        self.assertAlmostEqual(result["adsorption_energy_ev"], -1.2)
        self.assertTrue(result["recommendation_blocked"])
        item["energies"][1]["method_fingerprint"] = "3" * 64
        blocked = calculate_adsorption_energy(item)
        self.assertEqual(blocked["status"], "blocked")
        self.assertIn("incomparable_method_fingerprints", blocked["reasons"])


if __name__ == "__main__": unittest.main()
