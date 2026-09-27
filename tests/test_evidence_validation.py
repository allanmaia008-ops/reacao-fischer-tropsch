import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from plataforma_ltft.domain import LTFTCase
from plataforma_ltft.evidence_validation import audit_evidence_directory, write_audit_report


class EvidenceValidationTests(unittest.TestCase):
    def setUp(self):
        self.evidence = ROOT / "data" / "evidence"

    def test_current_csvs_are_structurally_valid_but_not_approved(self):
        report = audit_evidence_directory(self.evidence)
        self.assertEqual(report["summary"]["dataset_count"], 3)
        self.assertEqual(report["summary"]["structurally_valid_count"], 3)
        self.assertEqual(report["summary"]["approved_for_model_use_count"], 0)
        self.assertFalse(report["summary"]["g2_ready"])
        self.assertEqual(report["summary"]["error_count"], 0)
        self.assertGreater(report["summary"]["warning_count"], 0)
        self.assertTrue(all(not item["allowed_to_change_ranking"] for item in report["datasets"]))

    def test_selectivity_rows_close_at_100_percent(self):
        report = audit_evidence_directory(self.evidence)
        selectivity = next(item for item in report["datasets"] if "selectivity" in item["filename"])
        self.assertEqual(selectivity["metrics"]["selectivity_closure_pct"], [100.0] * 5)
        self.assertEqual(selectivity["metrics"]["missing_counts"]["CTY_mol_CO_gCo_h"], 4)

    def test_compatibility_is_context_only_not_transferability(self):
        case = LTFTCase(active_family="Co", promoter="Ru", promoter_loading_wt_pct=0.5)
        report = audit_evidence_directory(self.evidence, case)
        mello = [item for item in report["datasets"] if item["filename"].startswith("ltft_mello")]
        self.assertTrue(all(item["compatibility"]["status"] == "context_only" for item in mello))

    def test_bad_selectivity_closure_is_detected_without_editing_source(self):
        with tempfile.TemporaryDirectory() as folder:
            copied = Path(folder) / "evidence"
            shutil.copytree(self.evidence, copied)
            path = copied / "ltft_mello_2017_selectivity.csv"
            original = path.read_text(encoding="utf-8")
            path.write_text(original.replace("14.7,12.8,42.0,30.5", "14.7,12.8,42.0,20.5", 1), encoding="utf-8")
            report = audit_evidence_directory(copied)
            selectivity = next(item for item in report["datasets"] if "selectivity" in item["filename"])
            self.assertEqual(selectivity["status"], "invalid")
            self.assertTrue(any(issue["code"] == "selectivity_closure" for issue in selectivity["issues"]))
            self.assertEqual(self.evidence.joinpath("ltft_mello_2017_selectivity.csv").read_text(encoding="utf-8"), original)

    def test_report_is_written_as_json(self):
        with tempfile.TemporaryDirectory() as folder:
            target = write_audit_report(self.evidence, Path(folder) / "audit.json")
            self.assertEqual(json.loads(target.read_text(encoding="utf-8"))["schema_version"], "1.0.0")

