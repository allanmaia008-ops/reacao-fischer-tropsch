"""Audit the dedicated HTFT corpus without mixing it with LTFT evidence."""
import csv
import hashlib
import json
from pathlib import Path

REQUIRED_COLUMNS = ("dataset_id", "row_id", "catalyst", "temperature_c", "pressure_bar",
                    "co_conversion_pct", "co2_selectivity_pct", "ch4_carbon_pct",
                    "c2_c4_olefins_carbon_pct", "c2_c4_paraffins_carbon_pct",
                    "c5plus_carbon_pct", "olefin_paraffin_ratio_c2_c4", "selectivity_basis",
                    "source_doi", "source_table", "evidence_status")


def audit_htft_corpus(directory: Path) -> dict:
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    reports = []
    for filename, metadata in manifest.get("datasets", {}).items():
        path = directory / filename
        issues = []
        if not path.exists():
            reports.append({"filename": filename, "valid": False, "issues": ["missing_file"]}); continue
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream); headers = tuple(reader.fieldnames or ()); rows = list(reader)
        missing = [name for name in REQUIRED_COLUMNS if name not in headers]
        issues.extend(f"missing_column:{name}" for name in missing)
        for index, row in enumerate(rows, start=2):
            try:
                temperature = float(row["temperature_c"])
                fractions = [float(row[name]) for name in ("ch4_carbon_pct", "c2_c4_olefins_carbon_pct", "c2_c4_paraffins_carbon_pct", "c5plus_carbon_pct")]
                if not 280 <= temperature <= 350: issues.append(f"row_{index}:outside_htft_envelope")
                if abs(sum(fractions) - 100) > .11: issues.append(f"row_{index}:hydrocarbon_closure")
            except (KeyError, TypeError, ValueError): issues.append(f"row_{index}:invalid_numeric")
        approved = metadata.get("review_status") == metadata.get("evidence_status") == "approved"
        reports.append({"filename": filename, "row_count": len(rows), "valid": not issues,
                        "approved_internal_contextual": approved, "issues": issues,
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "allowed_for_automatic_calibration": False})
    return {"schema_version": "1.0.0", "dataset_count": len(reports),
            "row_count": sum(item.get("row_count", 0) for item in reports),
            "valid": bool(reports) and all(item["valid"] for item in reports),
            "approved_internal_contextual": bool(reports) and all(item.get("approved_internal_contextual") for item in reports),
            "recommendation_blocked": True, "datasets": reports}


def htft_dataset_route(case: dict, metadata: dict) -> dict:
    reasons = []
    if metadata.get("regime") != "HTFT": reasons.append("dataset_regime_mismatch")
    if not str((case.get("catalyst") or {}).get("family", "")).startswith(str(metadata.get("catalyst_family", "missing"))): reasons.append("catalyst_family_mismatch")
    return {"compatible_for_context": not reasons, "reasons": reasons,
            "ltft_model_allowed": False, "automatic_calibration_allowed": False,
            "recommendation_blocked": True}
