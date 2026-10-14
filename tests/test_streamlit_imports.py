import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class StreamlitImportTests(unittest.TestCase):
    def test_app_imports_reporting_modules_directly(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("from plataforma_ltft.reporting import", source)
        self.assertNotIn("build_export_artifacts, generate_scientific_report,\n    plan_product_target", source)
        spec = importlib.util.spec_from_file_location("platform_app_import_check", ROOT / "app.py")
        self.assertIsNotNone(spec)

