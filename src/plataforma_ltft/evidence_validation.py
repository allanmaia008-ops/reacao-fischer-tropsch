"""Auditoria não destrutiva dos CSVs de evidência LTFT."""

import csv
import hashlib
import json
from dataclasses import asdict
from datetime import date
from pathlib import Path

from .domain import LTFTCase

AUDIT_SCHEMA_VERSION = "1.0.0"

DATASET_SPECS = {
    "ltft_kinetic_equations_provenance.csv": {
        "headers": ["system", "equation", "parameters", "source", "status", "limitation"],
        "required": ["system", "equation", "parameters", "source", "status", "limitation"],
        "numeric": [],
    },
    "ltft_mello_2017_selectivity.csv": {
        "headers": ["Catalisador", "CO2_pct", "C1_pct", "C2_C4_pct", "C5_C12_pct", "C13plus_pct", "CTY_mol_CO_gCo_h", "basis", "source_table"],
        "required": ["Catalisador", "CO2_pct", "C1_pct", "C2_C4_pct", "C5_C12_pct", "C13plus_pct", "basis", "source_table"],
        "numeric": ["CO2_pct", "C1_pct", "C2_C4_pct", "C5_C12_pct", "C13plus_pct", "CTY_mol_CO_gCo_h"],
    },
    "ltft_mello_2017_supports.csv": {
        "headers": ["Suporte", "M_wt_pct", "delta_atoms_nm2", "BET_m2_g", "Vp_cm3_g", "Vp_normalized_cm3_gAl2O3", "pore_nm", "eta_eV"],
        "required": ["Suporte", "BET_m2_g", "Vp_cm3_g", "Vp_normalized_cm3_gAl2O3", "pore_nm", "eta_eV"],
        "numeric": ["M_wt_pct", "delta_atoms_nm2", "BET_m2_g", "Vp_cm3_g", "Vp_normalized_cm3_gAl2O3", "pore_nm", "eta_eV"],
    },
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def _number(value: str, field: str, row_number: int, issues: list[dict]) -> float | None:
    if value == "":
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        issues.append({"severity": "error", "row": row_number, "field": field, "code": "invalid_numeric", "message": f"{field} não é numérico."})
        return None
    if result < 0:
        issues.append({"severity": "error", "row": row_number, "field": field, "code": "negative_value", "message": f"{field} não pode ser negativo."})
    return result


def _audit_rows(filename: str, rows: list[dict[str, str]], issues: list[dict]) -> dict:
    spec = DATASET_SPECS[filename]
    missing_counts = {header: 0 for header in spec["headers"]}
    closures: list[float] = []
    duplicate_keys: list[str] = []
    key_field = {"ltft_kinetic_equations_provenance.csv": "system", "ltft_mello_2017_selectivity.csv": "Catalisador", "ltft_mello_2017_supports.csv": "Suporte"}[filename]
    seen = set()
    for row_number, row in enumerate(rows, start=2):
        key = row.get(key_field, "")
        if key in seen:
            duplicate_keys.append(key)
            issues.append({"severity": "error", "row": row_number, "field": key_field, "code": "duplicate_key", "message": f"Chave duplicada: {key}."})
        seen.add(key)
        for field in spec["headers"]:
            value = (row.get(field) or "").strip()
            if not value:
                missing_counts[field] += 1
                if field in spec["required"]:
                    issues.append({"severity": "error", "row": row_number, "field": field, "code": "missing_required", "message": f"Campo obrigatório ausente: {field}."})
        values = {field: _number((row.get(field) or "").strip(), field, row_number, issues) for field in spec["numeric"]}
        for field, value in values.items():
            if value is not None and field.endswith("_pct") and value > 100:
                issues.append({"severity": "error", "row": row_number, "field": field, "code": "percent_above_100", "message": f"{field} excede 100%."})
        if filename == "ltft_mello_2017_selectivity.csv" and all(values.get(field) is not None for field in ("C1_pct", "C2_C4_pct", "C5_C12_pct", "C13plus_pct")):
            closure = sum(values[field] for field in ("C1_pct", "C2_C4_pct", "C5_C12_pct", "C13plus_pct"))
            closures.append(closure)
            if abs(closure - 100.0) > 0.11:
                issues.append({"severity": "error", "row": row_number, "field": "HC_closure_pct", "code": "selectivity_closure", "message": f"Seletividades de hidrocarbonetos fecham em {closure:.3f}%, não 100%."})
        if filename == "ltft_kinetic_equations_provenance.csv":
            status = (row.get("status") or "").lower()
            if status not in ("not calibrated", "assumption only", "literature equation"):
                issues.append({"severity": "warning", "row": row_number, "field": "status", "code": "unknown_kinetic_status", "message": "Status cinético não reconhecido."})
    return {
        "row_count": len(rows),
        "missing_counts": missing_counts,
        "duplicate_keys": duplicate_keys,
        "selectivity_closure_pct": closures,
    }


def _compatibility(filename: str, case: LTFTCase | None) -> dict:
    if case is None:
        return {"status": "not_evaluated", "reasons": ["Nenhum caso LTFT foi fornecido."]}
    reasons = []
    if filename.startswith("ltft_mello"):
        if case.active_family != "Co":
            reasons.append("A série Mello é Co-Ru; a família ativa do caso não é Co.")
        if case.promoter != "Ru":
            reasons.append("A série Mello usa Ru; o caso não declara Ru como promotor.")
        reasons.append("Composição de recobrimento, preparação e condições completas não estão codificadas nestes CSVs.")
        return {"status": "context_only", "reasons": reasons}
    reasons.append("Equações incluem hipóteses não calibradas ou sistemas não transferíveis ao caso.")
    return {"status": "provenance_only", "reasons": reasons}


def audit_evidence_directory(evidence_dir: Path, case: LTFTCase | None = None) -> dict:
    evidence_dir = Path(evidence_dir)
    manifest_path = evidence_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = []
    global_issues = []
    for filename, spec in DATASET_SPECS.items():
        path = evidence_dir / filename
        issues: list[dict] = []
        if not path.exists():
            files.append({"filename": filename, "status": "invalid", "issues": [{"severity": "error", "code": "missing_file", "message": "Arquivo ausente."}]})
            continue
        headers, rows = _read_csv(path)
        if headers != spec["headers"]:
            issues.append({"severity": "error", "code": "header_mismatch", "message": "Cabeçalho ou ordem de colunas diferente do esquema.", "expected": spec["headers"], "actual": headers})
        metrics = _audit_rows(filename, rows, issues)
        metadata = manifest.get("datasets", {}).get(filename)
        if metadata is None:
            issues.append({"severity": "error", "code": "missing_manifest_entry", "message": "Arquivo não possui entrada no manifesto."})
            metadata = {}
        for field in ("source_url_or_doi", "license"):
            if not metadata.get(field):
                issues.append({"severity": "warning", "code": f"missing_{field}", "message": f"Manifesto não informa {field}."})
        if not metadata.get("full_text_verified"):
            issues.append({"severity": "warning", "code": "full_text_unverified", "message": "Leitura integral não está registrada como verificada."})
        errors = sum(issue["severity"] == "error" for issue in issues)
        file_report = {
            "filename": filename,
            "sha256": _sha256(path),
            "status": "invalid" if errors else "structurally_valid_not_approved",
            "metadata": metadata,
            "metrics": metrics,
            "compatibility": _compatibility(filename, case),
            "issues": issues,
            "allowed_for_automatic_calibration": False,
            "allowed_to_change_ranking": False,
        }
        files.append(file_report)
        global_issues.extend({"filename": filename, **issue} for issue in issues)
    error_count = sum(issue["severity"] == "error" for issue in global_issues)
    warning_count = sum(issue["severity"] == "warning" for issue in global_issues)
    return {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "audit_date": date.today().isoformat(),
        "evidence_directory": str(evidence_dir.resolve()),
        "case": asdict(case) if case else None,
        "summary": {
            "dataset_count": len(files),
            "structurally_valid_count": sum(item["status"] == "structurally_valid_not_approved" for item in files),
            "approved_for_model_use_count": 0,
            "error_count": error_count,
            "warning_count": warning_count,
            "g2_ready": False,
        },
        "datasets": files,
        "global_limits": [
            "Nenhum CSV pode calibrar modelos, alterar ranking ou recomendar condições automaticamente.",
            "Licença, localização da fonte e leitura integral ainda não estão verificadas no manifesto.",
            "Compatibilidade contextual não equivale a transferibilidade quantitativa.",
        ],
    }


def write_audit_report(evidence_dir: Path, output_path: Path, case: LTFTCase | None = None) -> Path:
    report = audit_evidence_directory(evidence_dir, case)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output_path
