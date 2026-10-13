"""Valida e executa sequencialmente as células dos notebooks, sem kernel Jupyter."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate_notebook(path: Path) -> None:
    content = json.loads(path.read_text(encoding="utf-8"))
    namespace = {"__name__": "__notebook__"}
    for item in content["cells"]:
        if item["cell_type"] == "code":
            exec(compile("".join(item["source"]), f"{path.name}:{item['id']}", "exec"), namespace)


if __name__ == "__main__":
    for notebook_path in sorted((ROOT / "notebooks").glob("0*.ipynb")):
        validate_notebook(notebook_path)
        print(f"OK {notebook_path.name}")
