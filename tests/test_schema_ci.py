import json
import tempfile
import unittest
from pathlib import Path

from tools.validate_schemas import validate_repository


ROOT = Path(__file__).resolve().parents[1]


class SchemaCITests(unittest.TestCase):
    def test_repository_schemas_and_examples_pass(self):
        report = validate_repository(ROOT)
        self.assertTrue(report.valid, report.issues)
        self.assertEqual(report.schema_count, 13)
        self.assertEqual(report.example_count, 12)

    def test_duplicate_schema_id_fails_the_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "schemas").mkdir()
            (root / "examples").mkdir()
            schema = {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "$id": "urn:test:duplicate",
                "type": "object",
            }
            for name in ("a.schema.json", "b.schema.json"):
                (root / "schemas" / name).write_text(json.dumps(schema), encoding="utf-8")
            report = validate_repository(root)
            self.assertFalse(report.valid)
            self.assertTrue(any("duplicado" in issue for issue in report.issues))


if __name__ == "__main__":
    unittest.main()
