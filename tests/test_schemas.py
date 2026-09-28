import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SchemaTests(unittest.TestCase):
    def test_all_schemas_are_valid_json_with_unique_ids(self):
        schemas = [json.loads(path.read_text(encoding="utf-8")) for path in sorted((ROOT / "schemas").glob("*.schema.json"))]
        self.assertEqual(len(schemas), 5)
        self.assertEqual(len({schema["$id"] for schema in schemas}), 5)
        self.assertTrue(all(schema["$schema"].endswith("2020-12/schema") for schema in schemas))

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
