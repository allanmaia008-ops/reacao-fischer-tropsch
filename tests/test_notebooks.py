import json
import subprocess
import sys
import unittest
from pathlib import Path

from tools.validate_notebooks import validate_notebook

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {"01_produto_asf.ipynb", "02_contrato_catalisador.ipynb", "03_unidades_canonicas.ipynb", "04_auditoria_evidencias.ipynb", "05_caso_experimental_ltft.ipynb", "06_preparacao_htft.ipynb"}


class NotebookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(ROOT / "tools" / "generate_notebook.py")], cwd=ROOT, check=True)

    def test_expected_modular_notebooks_exist(self):
        self.assertTrue(EXPECTED.issubset({path.name for path in (ROOT / "notebooks").glob("*.ipynb")}))

    def test_notebooks_are_valid_and_code_cells_compile(self):
        for name in EXPECTED:
            with self.subTest(name=name):
                notebook = json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))
                self.assertEqual(notebook["nbformat"], 4)
                self.assertEqual(notebook["metadata"]["plataforma_ft"]["generator"], "tools/generate_notebook.py")
                ids = [cell["id"] for cell in notebook["cells"]]
                self.assertEqual(len(ids), len(set(ids)))
                for item in notebook["cells"]:
                    if item["cell_type"] == "code":
                        compile("".join(item["source"]), f"{name}:{item['id']}", "exec")

    def test_notebooks_import_instead_of_redefining_scientific_functions(self):
        forbidden = ("def run_screening", "def validate_case", "def convert(", "def validate_catalyst")
        for name in EXPECTED:
            text = (ROOT / "notebooks" / name).read_text(encoding="utf-8")
            self.assertFalse(any(item in text for item in forbidden), name)

    def test_notebook_cells_execute_sequentially(self):
        for name in EXPECTED:
            with self.subTest(name=name):
                validate_notebook(ROOT / "notebooks" / name)


if __name__ == "__main__":
    unittest.main()
