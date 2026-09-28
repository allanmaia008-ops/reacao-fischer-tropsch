import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from plataforma_ltft.worker import execute


class WorkerTests(unittest.TestCase):
    def test_invalid_case_is_rejected_before_output(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                execute(ROOT / "examples" / "caso_invalido.json", Path(folder))

    def test_product_first_mode_needs_no_preselected_catalyst(self):
        with tempfile.TemporaryDirectory() as folder:
            result = execute(ROOT / "examples" / "planejar_produto.json", Path(folder))
            data = json.loads(result.read_text(encoding="utf-8"))
            self.assertEqual(data["status"], "orientacao_por_produto")
            self.assertEqual(data["target_plan"]["desired_product"], "C12-C20")
            self.assertIsNone(data["target_plan"]["catalyst_orientation"]["selected_family"])
            self.assertEqual(data["schema_version"], "2.0.0")
            self.assertEqual(data["ft_regime"], "nao_definido")
            self.assertTrue(data["recommendation_blocked"])

    def test_worker_writes_auditable_result(self):
        with tempfile.TemporaryDirectory() as folder:
            result = execute(ROOT / "examples" / "caso_co.json", Path(folder))
            data = json.loads(result.read_text(encoding="utf-8"))
            self.assertEqual(data["status"], "distribuicao_asf_condicional")
            self.assertIsNone(data["CO_conversion_pct"])
            self.assertEqual(data["alpha_origin"], "informado_pelo_usuario")
            self.assertEqual(data["target_plan"]["desired_product"], "C12-C20")
            self.assertTrue(data["target_plan"]["recommendation_blocked"])
            self.assertFalse(data["readiness"]["valid_for_experimental_plan"])
            self.assertEqual(data["schema_version"], "2.0.0")
            self.assertEqual(data["ft_regime"], "LTFT")

    def test_htft_output_is_explicitly_blocked(self):
        with tempfile.TemporaryDirectory() as folder:
            result = execute(ROOT / "examples" / "caso_htft_v2.json", Path(folder))
            data = json.loads(result.read_text(encoding="utf-8"))
            self.assertEqual(data["ft_regime"], "HTFT")
            self.assertTrue(data["recommendation_blocked"])
            self.assertIn("preparação", data["recommendation_blocking_reason"])
