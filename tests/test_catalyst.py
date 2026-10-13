import copy
import json
import unittest
from pathlib import Path

from plataforma_ltft.catalyst import CATALYST_SCHEMA_VERSION, validate_catalyst

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = (
    "catalisador_co_v1.json",
    "catalisador_fe_v1.json",
    "catalisador_co_fe_exploratorio_v1.json",
)


def load_example(name):
    return json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))


class CatalystContractTests(unittest.TestCase):
    def test_examples_pass_cross_field_validation(self):
        for name in EXAMPLES:
            with self.subTest(name=name):
                result = validate_catalyst(load_example(name))
                self.assertTrue(result.valid, result.errors)

    def test_contract_version_is_explicit(self):
        self.assertEqual(CATALYST_SCHEMA_VERSION, "1.0.0")
        data = load_example(EXAMPLES[0])
        data["schema_version"] = "2.0.0"
        self.assertFalse(validate_catalyst(data).valid)

    def test_co_fe_requires_scientific_hypothesis(self):
        data = load_example(EXAMPLES[2])
        data["scientific_hypothesis"] = None
        result = validate_catalyst(data)
        self.assertIn("Catalisador Co-Fe exige scientific_hypothesis explícita.", result.errors)

    def test_measured_phase_requires_evidence(self):
        data = load_example(EXAMPLES[0])
        data["active_phase"] = {"label": "Co0", "status": "medida", "evidence_ids": []}
        result = validate_catalyst(data)
        self.assertIn("Fase medida exige ao menos um evidence_id.", result.errors)

    def test_hypothetical_phase_is_not_promoted_to_measurement(self):
        result = validate_catalyst(load_example(EXAMPLES[2]))
        self.assertTrue(result.valid)
        self.assertIn("Fase não medida sem evidência associada; permanece hipótese não verificada.", result.warnings)

    def test_loading_closure_and_duplicate_promoters(self):
        data = load_example(EXAMPLES[0])
        data["active_metal_loading_wt_pct"] = 99
        data["promoters"] = [
            {"name": "Ru", "loading_wt_pct": 1, "precursor": None},
            {"name": "ru", "loading_wt_pct": 1, "precursor": None},
        ]
        result = validate_catalyst(data)
        self.assertIn("Promotores não podem ser duplicados no mesmo lote.", result.errors)
        self.assertIn("A soma de metal ativo e promotores não pode exceder 100 % em massa.", result.errors)

    def test_provenance_and_preparation_are_required(self):
        data = copy.deepcopy(load_example(EXAMPLES[1]))
        data["preparation_steps"] = []
        data["provenance"]["license"] = ""
        result = validate_catalyst(data)
        self.assertIn("preparation_steps deve conter ao menos uma etapa.", result.errors)
        self.assertIn("provenance.license deve ser não vazio.", result.errors)


if __name__ == "__main__":
    unittest.main()
