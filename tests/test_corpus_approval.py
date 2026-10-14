import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from plataforma_ltft.corpus_approval import assess_corpus_approval

class CorpusApprovalTests(unittest.TestCase):
    def test_current_manifest_is_explicitly_blocked(self):
        report = assess_corpus_approval(Path(__file__).parents[1] / "data/evidence/manifest.json")
        self.assertEqual(report["corpus_status"], "blocked")
        self.assertEqual(report["approved_count"], 0)
        self.assertTrue(all(row["missing_requirements"] for row in report["datasets"]))

