import json
from pathlib import Path
import tempfile
import unittest

from jsonschema import Draft202012Validator
from plataforma_ltft.dft_parser import parse_vasp_outcar
from plataforma_ltft.dft_reporting import (
    build_dft_report,
    render_dft_report_markdown,
    write_dft_report,
)

ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_OUTCAR = """aborting loop because EDIFF is reached
free energy TOTEN = -10.123 eV
POSITION (Angst) TOTAL-FORCE (eV/Angst)
---
0.0 0.0 0.0 0.01 0.0 0.0
---
reached required accuracy - stopping structural energy minimisation
General timing and accounting informations for this job:
"""


class DFTReportingTests(unittest.TestCase):
    def setUp(self):
        self.structure = json.loads((ROOT / "examples/dft_structure_synthetic_v1.json").read_text(encoding="utf-8"))
        self.protocol = json.loads((ROOT / "examples/dft_surface_vasp_synthetic_v1.json").read_text(encoding="utf-8"))
        self.result = parse_vasp_outcar(SYNTHETIC_OUTCAR, synthetic=True, force_threshold_ev_angstrom=0.03)
        self.manifest = {
            "input_set_id": "ft038-synthetic-001",
            "adapter_version": "1.0.0",
            "method_fingerprint_sha256": "b" * 64,
            "source": {"contract_fingerprint_sha256": "c" * 64},
            "files": [],
            "required_external_files": [{"path": "POTCAR", "status": "missing"}],
            "execution_status": "synthetic_test",
            "recommendation_blocked": True,
        }

    def build(self):
        return build_dft_report(
            self.result,
            report_id="ft-dft-synthetic-001",
            structure_contract=self.structure,
            surface_protocol=self.protocol,
            input_manifest=self.manifest,
            source_citation="Internal synthetic fixture only.",
        )

    def test_builds_schema_valid_report_and_keeps_scientific_blocks(self):
        report = self.build()
        schema = json.loads((ROOT / "schemas/ft-dft-report-v1.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(list(Draft202012Validator(schema).iter_errors(report)), [])
        self.assertTrue(report["synthetic"])
        self.assertTrue(report["recommendation_blocked"])
        self.assertTrue(report["independent_review_required"])
        self.assertIn("not experimental evidence", " ".join(report["limitations"]))

    def test_markdown_is_explicit_about_synthetic_and_blocked_status(self):
        markdown = render_dft_report_markdown(self.build())
        self.assertIn("Synthetic record: **yes**", markdown)
        self.assertIn("Recommendation status: **BLOCKED**", markdown)
        self.assertIn("SHA-256", markdown)

    def test_writer_emits_json_and_markdown_without_overwrite(self):
        report = self.build()
        with tempfile.TemporaryDirectory() as directory:
            paths = write_dft_report(report, Path(directory) / "report")
            self.assertTrue(all(path.exists() for path in paths))
            with self.assertRaises(FileExistsError):
                write_dft_report(report, Path(directory) / "report")

    def test_report_rejects_unblocked_inputs(self):
        self.manifest["recommendation_blocked"] = False
        with self.assertRaisesRegex(ValueError, "input manifest"):
            self.build()


if __name__ == "__main__":
    unittest.main()
