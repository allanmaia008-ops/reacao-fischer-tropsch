import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


class SchemaTests(unittest.TestCase):
    def test_all_schemas_are_valid_json_with_unique_ids(self):
        schemas = [json.loads(path.read_text(encoding="utf-8")) for path in sorted((ROOT / "schemas").glob("*.schema.json"))]
        self.assertEqual(len(schemas), 24)
        self.assertEqual(len({schema["$id"] for schema in schemas}), len(schemas))
        self.assertTrue(all(schema["$schema"].endswith("2020-12/schema") for schema in schemas))
        for schema in schemas:
            Draft202012Validator.check_schema(schema)

    def test_case_example_uses_declared_properties(self):
        schema = json.loads((ROOT / "schemas" / "ltft-case-v1.schema.json").read_text(encoding="utf-8"))
        example = json.loads((ROOT / "examples" / "caso_experimental_completo.json").read_text(encoding="utf-8"))["case"]
        self.assertFalse(set(example) - set(schema["properties"]))
        self.assertFalse(set(schema["required"]) - set(example))
        self.assertEqual(example["schema_version"], "1.0.0")

    def test_v2_examples_use_declared_properties(self):
        schema = json.loads((ROOT / "schemas" / "ft-case-v2.schema.json").read_text(encoding="utf-8"))
        for name in ("caso_htft_v2.json", "caso_transicao_v2.json"):
            example = json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))["case"]
            self.assertFalse(set(example) - set(schema["properties"]))
            self.assertFalse(set(schema["required"]) - set(example))
            self.assertEqual(example["schema_version"], "2.0.0")

    def test_case_schema_enforces_regime_temperature_and_htft_family(self):
        schema = json.loads((ROOT / "schemas" / "ft-case-v2.schema.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        transition = json.loads((ROOT / "examples" / "caso_transicao_v2.json").read_text(encoding="utf-8"))["case"]
        self.assertEqual(list(validator.iter_errors(transition)), [])
        wrong_regime = {**transition, "temperature_c": 280}
        self.assertTrue(list(validator.iter_errors(wrong_regime)))
        htft = json.loads((ROOT / "examples" / "caso_htft_v2.json").read_text(encoding="utf-8"))["case"]
        wrong_family = {**htft, "active_family": "Co"}
        self.assertTrue(list(validator.iter_errors(wrong_family)))

    def test_approved_evidence_requires_rights_and_use_scope(self):
        schema = json.loads((ROOT / "schemas" / "ltft-evidence-v1.schema.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        evidence = {
            "schema_version": "1.0.0", "evidence_id": "EV-SYN-001", "source": "Synthetic test record",
            "source_url_or_doi": None, "license": "internal_test_only", "evidence_status": "aprovado",
            "data": {}, "units": {}, "uncertainties": None, "conditions": None,
            "limitations": ["Synthetic test data; not scientific evidence."],
            "license_verified": True, "rights_note": "Synthetic record.", "review_status": "approved",
            "approval_basis": "Automated contract test.", "approved_uses": ["schema_test"],
            "prohibited_uses": ["scientific_claims"],
        }
        self.assertEqual(list(validator.iter_errors(evidence)), [])
        incomplete = {**evidence, "license_verified": False}
        self.assertTrue(list(validator.iter_errors(incomplete)))

    def test_result_schema_requires_asf_payload_and_hard_block(self):
        schema = json.loads((ROOT / "schemas" / "ft-result-v2.schema.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        result = {
            "schema_version": "2.0.0", "status": "distribuicao_asf_condicional", "ft_regime": "LTFT",
            "regime_envelope_version": "1.0.0", "recommendation_blocked": True,
            "recommendation_blocking_reason": "No validated kinetics.", "warning": "Conditional ASF only.",
            "case": {}, "alpha": 0.85, "alpha_origin": "informado_pelo_usuario",
            "product_basis": "carbon_fraction", "product_bands": {"C1": 0.1},
            "target_fraction": 0.1, "readiness": {}, "target_plan": {},
        }
        self.assertEqual(list(validator.iter_errors(result)), [])
        unblocked = {**result, "recommendation_blocked": False}
        self.assertTrue(list(validator.iter_errors(unblocked)))
        missing_payload = {key: value for key, value in result.items() if key != "alpha"}
        self.assertTrue(list(validator.iter_errors(missing_payload)))

    def test_catalyst_examples_validate_against_dedicated_schema(self):
        schema = json.loads((ROOT / "schemas" / "ft-catalyst-v1.schema.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        for name in (
            "catalisador_co_v1.json",
            "catalisador_fe_v1.json",
            "catalisador_co_fe_exploratorio_v1.json",
        ):
            example = json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))
            errors = sorted(validator.iter_errors(example), key=lambda error: list(error.path))
            self.assertEqual(errors, [], f"{name}: {[error.message for error in errors]}")
