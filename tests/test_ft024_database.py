import csv
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FT024DatabaseTests(unittest.TestCase):
    def test_database_has_traceable_measurements_without_false_validation(self):
        with (ROOT / "data/evidence/ft024_cobalt_cerium_measurements.csv").open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 374)
        self.assertEqual(len({row["run_id"] for row in rows}), 52)
        self.assertGreaterEqual(len(rows), 100)
        self.assertTrue(all(row["source_doi"] and row["source_locator"] for row in rows))
        self.assertTrue(all(row["external_validation_eligible"] == "False" for row in rows))
        strict = {row["run_id"] for row in rows if row["compatibility_class"] == "strict_same_catalyst_same_study"}
        self.assertEqual(len(strict), 22)

    def test_manifest_distinguishes_measurements_from_runs(self):
        manifest = json.loads((ROOT / "data/evidence/ft024_cobalt_cerium_measurements.manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["measurement_rows"], 374)
        self.assertEqual(manifest["unique_experimental_runs"], 52)
        self.assertEqual(manifest["externally_validating_runs"], 0)
        self.assertTrue(manifest["recommendation_blocked"])

if __name__ == "__main__": unittest.main()
