"""Gera notebooks modulares que reutilizam o núcleo oficial da plataforma."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"


def cell(kind, source):
    item = {"cell_type": kind, "metadata": {}, "source": source.splitlines(keepends=True)}
    if kind == "code":
        item.update(execution_count=None, outputs=[])
    return item


def notebook(slug, title, purpose, cells):
    all_cells = [
        cell("markdown", f"# {title}\n\n{purpose}\n\n> Este notebook importa os módulos oficiais. Não copie regras científicas para as células.\n"),
        cell("code", "from pathlib import Path\nimport json\nimport sys\n\nROOT = Path.cwd()\nif not (ROOT / 'src').exists():\n    ROOT = ROOT.parent\nif not (ROOT / 'src' / 'plataforma_ltft').exists():\n    raise RuntimeError('Execute o notebook na raiz do projeto ou em notebooks/.')\nsys.path.insert(0, str(ROOT / 'src'))\n"),
        *cells,
    ]
    for index, item in enumerate(all_cells):
        item["id"] = f"{slug}-{index:02d}"
    return {
        "nbformat": 4, "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
            "language_info": {"name": "python", "version": "3.11"},
            "plataforma_ft": {"generator": "tools/generate_notebook.py", "module": slug},
        },
        "cells": all_cells,
    }


SPECS = {
    "01_produto_asf.ipynb": notebook("produto-asf", "01 — Produto-alvo e orientação ASF", "Explora o produto desejado antes da escolha do catalisador. ASF é referência matemática, não previsão de conversão.", [
        cell("code", "from plataforma_ltft import plan_product_target\n"),
        cell("code", "target = 'C12-C20'\nplan = plan_product_target(target)\nplan\n"),
        cell("markdown", "## Verificação\n\nA recomendação final deve permanecer bloqueada sem dados calibrados específicos.\n"),
        cell("code", "assert plan['recommendation_blocked'] is True\nplan['asf_orientation']\n"),
    ]),
    "02_contrato_catalisador.ipynb": notebook("contrato-catalisador", "02 — Cadastro e validação de catalisador", "Valida os exemplos Co, Fe e Co–Fe exploratório sem tratar hipótese de fase como medição.", [
        cell("code", "from plataforma_ltft import validate_catalyst\n"),
        cell("code", "names = ['catalisador_co_v1.json', 'catalisador_fe_v1.json', 'catalisador_co_fe_exploratorio_v1.json']\nreports = {}\nfor name in names:\n    data = json.loads((ROOT / 'examples' / name).read_text(encoding='utf-8'))\n    reports[name] = validate_catalyst(data)\nreports\n"),
        cell("code", "assert all(report.valid for report in reports.values())\n"),
    ]),
    "03_unidades_canonicas.ipynb": notebook("unidades-canonicas", "03 — Unidades canônicas", "Demonstra conversões dimensionais e preservação do valor e da unidade originais.", [
        cell("code", "from plataforma_ltft import canonicalize_field, convert\n"),
        cell("code", "pressure = canonicalize_field('pressure_bar', 2.0, 'MPa')\ntemperature_c = convert(298.15, 'K', 'degC')\npressure, temperature_c\n"),
        cell("code", "assert pressure.canonical_value == 20.0\nassert pressure.original_unit == 'MPa'\n"),
    ]),
    "04_auditoria_evidencias.ipynb": notebook("auditoria-evidencias", "04 — Auditoria de evidências", "Audita as evidências sem modificar as fontes nem liberar dados automaticamente para calibração.", [
        cell("code", "from plataforma_ltft import audit_evidence_directory\n"),
        cell("code", "report = audit_evidence_directory(ROOT / 'data' / 'evidence')\nreport['summary']\n"),
        cell("code", "assert report['summary']['approved_for_model_use_count'] == 0\nassert report['summary']['g2_ready'] is False\n"),
    ]),
    "05_caso_experimental_ltft.ipynb": notebook("caso-experimental-ltft", "05 — Caso experimental LTFT", "Carrega um caso, migra explicitamente v1→v2, valida a completude e calcula ASF condicional.", [
        cell("code", "from plataforma_ltft import LTFTCase, migrate_case_v1_to_v2, run_screening, validate_case\n"),
        cell("code", "payload = json.loads((ROOT / 'examples' / 'caso_experimental_completo.json').read_text(encoding='utf-8'))\nmigrated = migrate_case_v1_to_v2(payload['case'])\ncase = LTFTCase(**migrated)\nvalidation = validate_case(case)\nvalidation\n"),
        cell("code", "result = run_screening(case, alpha=payload['alpha'])\nresult\n"),
        cell("code", "assert validation.valid_for_experimental_plan is True\nassert validation.valid_for_rate_calculation is False\n"),
    ]),
    "06_preparacao_htft.ipynb": notebook("preparacao-htft", "06 — Preparação HTFT", "Exercita o contrato HTFT separado e confirma que a saída permanece descritiva e bloqueada.", [
        cell("code", "from plataforma_ltft import LTFTCase, run_screening, validate_case\n"),
        cell("code", "payload = json.loads((ROOT / 'examples' / 'caso_htft_v2.json').read_text(encoding='utf-8'))\ncase = LTFTCase(**payload['case'])\nvalidation = validate_case(case)\nvalidation\n"),
        cell("code", "result = run_screening(case, alpha=payload['alpha'])\nresult['readiness'], result['warning']\n"),
        cell("code", "assert result['ft_regime'] == 'HTFT'\nassert result['recommendation_blocked'] is True\n"),
    ]),
}


def generate_all():
    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    paths = []
    for filename, content in SPECS.items():
        target = NOTEBOOK_DIR / filename
        target.write_text(json.dumps(content, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        paths.append(target)
    return tuple(paths)


if __name__ == "__main__":
    for generated in generate_all():
        print(generated)
