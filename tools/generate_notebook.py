"""Gera um notebook de uso da plataforma sem incorporar código legado."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "notebooks" / "fluxo_ltft.ipynb"


def cell(kind, source):
    item = {"cell_type": kind, "metadata": {}, "source": source.splitlines(keepends=True)}
    if kind == "code":
        item.update(execution_count=None, outputs=[])
    return item


notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}},
    "cells": [
        cell("markdown", "# Plataforma LTFT\n\nExecução própria com alpha informado; não estima cinética ou conversão.\n"),
        cell("code", "from plataforma_ltft import LTFTCase, run_screening\n"),
        cell("code", "case = LTFTCase(composition='Co', active_family='Co', active_phase_hypothesis='Co0 a confirmar', support='Al2O3', active_metal_loading_wt_pct=20, temperature_c=220, pressure_bar=20, h2_co_molar_ratio=2.0, desired_product='C12-C20')\n"),
        cell("code", "result = run_screening(case, alpha=0.85)\nresult\n"),
    ],
}
for index, item in enumerate(notebook["cells"]):
    item["id"] = f"plataforma-ltft-{index}"
TARGET.parent.mkdir(parents=True, exist_ok=True)
TARGET.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(TARGET)
