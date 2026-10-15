"""Gate de aprovação do corpus LTFT, sem inventar metadados ausentes."""

import json
from pathlib import Path

CORPUS_APPROVAL_SCHEMA_VERSION = "1.0.0"

def assess_corpus_approval(manifest_path: Path) -> dict:
    payload = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    rows = []
    for filename, metadata in payload.get("datasets", {}).items():
        missing = [field for field in ("source_url_or_doi", "license") if not metadata.get(field)]
        if metadata.get("license_verified") is not True:
            missing.append("license_verified")
        if not metadata.get("full_text_verified", False):
            missing.append("full_text_verified")
        status = "approved" if not missing and metadata.get("evidence_status") == "approved" and metadata.get("review_status") == "approved" else "blocked"
        rows.append({"filename": filename, "status": status, "missing_requirements": missing})
    approved = sum(row["status"] == "approved" for row in rows)
    return {"schema_version": CORPUS_APPROVAL_SCHEMA_VERSION, "manifest": str(Path(manifest_path).resolve()), "dataset_count": len(rows), "approved_count": approved, "corpus_status": "approved" if rows and approved == len(rows) else "blocked", "datasets": rows, "prohibited_until_approval": ["calibracao_automatica", "ranking", "recomendacao_de_condicoes"]}

def write_corpus_approval_report(manifest_path: Path, output_path: Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(assess_corpus_approval(manifest_path), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output_path
