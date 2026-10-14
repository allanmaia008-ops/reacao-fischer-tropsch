import csv
import hashlib
import io
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from plataforma_ltft.domain import LTFTCase
from plataforma_ltft.reporting import build_export_artifacts, generate_scientific_report
from plataforma_ltft.screening import run_screening


def result_fixture():
    return run_screening(LTFTCase(
        composition="Co", active_family="Co", active_phase_hypothesis="Co0",
        support="Al2O3", active_metal_loading_wt_pct=20.0,
        temperature_c=220.0, pressure_bar=20.0, h2_co_molar_ratio=2.0,
        desired_product="C12-C20", ft_regime="LTFT",
    ), 0.85)


class ReportingTests(unittest.TestCase):
    def test_export_is_deterministic_and_manifest_hashes_match(self):
        first = build_export_artifacts(result_fixture())
        second = build_export_artifacts(result_fixture())
        self.assertEqual(first, second)
        manifest = json.loads(first["manifesto_exportacao_v1.json"].decode("utf-8"))
        raw_result = json.loads(first["resultado_ft_v1.json"].decode("utf-8"))["result"]
        canonical = (json.dumps(raw_result, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        self.assertEqual(hashlib.sha256(canonical).hexdigest(), manifest["result_sha256"])
        for item in manifest["files"]:
            self.assertEqual(hashlib.sha256(first[item["name"]]).hexdigest(), item["sha256"])

    def test_csv_is_machine_readable_and_keeps_version_and_block(self):
        artifacts = build_export_artifacts(result_fixture())
        text = artifacts["resumo_ft_v1.csv"].decode("utf-8-sig")
        row = next(csv.DictReader(io.StringIO(text)))
        self.assertEqual(row["export_contract_version"], "1.0.0")
        self.assertEqual(row["recommendation_blocked"], "true")
        self.assertEqual(row["desired_product"], "C12-C20")

    def test_json_round_trip_preserves_nulls_and_result(self):
        artifacts = build_export_artifacts(result_fixture())
        payload = json.loads(artifacts["resultado_ft_v1.json"].decode("utf-8"))
        self.assertIsNone(payload["result"]["CO_conversion_pct"])
        self.assertEqual(payload["result"]["alpha_origin"], "informado_pelo_usuario")

    def test_report_declares_assumptions_evidence_gaps_and_limitations(self):
        report = generate_scientific_report(result_fixture())
        self.assertIn("## Premissas declaradas", report)
        self.assertIn("Nenhuma fonte experimental aprovada", report)
        self.assertIn("Conversão de CO: não calculada", report)
        self.assertIn("Recomendação bloqueada: **sim**", report)
        self.assertIn("revisão humana permanece obrigatória", report)

    def test_incomplete_result_is_rejected(self):
        with self.assertRaises(ValueError):
            build_export_artifacts({"schema_version": "2.0.0"})
