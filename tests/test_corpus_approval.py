import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from plataforma_ltft.corpus_approval import assess_corpus_approval

class CorpusApprovalTests(unittest.TestCase):
    def test_user_approved_manifest_is_internal_approved(self):
        report = assess_corpus_approval(Path(__file__).parents[1] / "data/evidence/manifest.json")
        self.assertEqual(report["corpus_status"], "approved")
        self.assertEqual(report["approved_count"], 5)

