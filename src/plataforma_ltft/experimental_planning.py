"""Plano experimental e registro de piloto, sempre sujeitos a revisão humana."""

from dataclasses import asdict
from datetime import date
from .domain import LTFTCase

PLAN_VERSION = "1.0.0"

def generate_experimental_plan(case: LTFTCase) -> dict:
    return {"schema_version": PLAN_VERSION, "plan_status": "draft", "review_required": True, "recommendation_blocked": True, "case": asdict(case), "checklist": ["confirmar contrato experimental", "confirmar transporte e segurança", "definir ativação e analytics", "aprovação humana antes da execução"]}

def validate_pilot_record(record: dict) -> dict:
    required = ("pilot_id", "protocol_id", "execution_date", "raw_data_uri", "analytical_method")
    missing = [field for field in required if not record.get(field)]
    reasons = list(missing)
    if record.get("execution_confirmed") is not True:
        reasons.append("execution_not_confirmed")
    if record.get("evidence_type") != "project_experiment":
        reasons.append("project_experiment_required")
    try:
        execution = date.fromisoformat(record.get("execution_date", ""))
        if execution > date.today():
            reasons.append("execution_date_in_future")
    except (ValueError, TypeError):
        reasons.append("invalid_execution_date")
    for field in ("raw_data_sha256", "reviewer", "comparison_report_uri"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            reasons.append(field)
    digest = record.get("raw_data_sha256", "")
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
        reasons.append("invalid_raw_data_sha256")
    if record.get("raw_data_verified") is not True:
        reasons.append("raw_data_not_verified")
    status = "measured_record" if not reasons else "blocked"
    return {"schema_version": PLAN_VERSION, "status": status, "missing_fields": missing,
            "blocking_reasons": reasons, "recommendation_blocked": True,
            "record_is_evidence": status == "measured_record",
            "verification_scope": "metadata_and_reviewer_attestation_only"}
