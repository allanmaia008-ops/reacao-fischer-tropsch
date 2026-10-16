import json
from pathlib import Path
import unittest
from plataforma_ltft.htft_evidence import audit_htft_corpus, htft_dataset_route

ROOT = Path(__file__).resolve().parents[1]

class HTFTEvidenceTests(unittest.TestCase):
    def test_corpus_is_separate_closed_and_contextual_only(self):
        report = audit_htft_corpus(ROOT/'data/htft')
        self.assertTrue(report['valid'])
        self.assertTrue(report['approved_internal_contextual'])
        self.assertEqual(report['dataset_count'], 1)
        self.assertEqual(report['row_count'], 8)
        self.assertTrue(report['recommendation_blocked'])
        self.assertTrue(all(not d['allowed_for_automatic_calibration'] for d in report['datasets']))

    def test_cross_regime_and_catalyst_routing_remains_blocked(self):
        manifest = json.loads((ROOT/'data/htft/manifest.json').read_text(encoding='utf-8'))
        metadata = next(iter(manifest['datasets'].values()))
        valid = htft_dataset_route({'catalyst': {'family':'Fe-K'}}, metadata)
        self.assertTrue(valid['compatible_for_context'])
        self.assertFalse(valid['ltft_model_allowed'])
        invalid = htft_dataset_route({'catalyst': {'family':'Co'}}, metadata)
        self.assertFalse(invalid['compatible_for_context'])
        self.assertIn('catalyst_family_mismatch', invalid['reasons'])
