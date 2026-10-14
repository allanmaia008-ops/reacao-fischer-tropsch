"""Plano experimental e registro de piloto, sempre sujeitos a revisão humana."""

from dataclasses import asdict
from .domain import LTFTCase

PLAN_VERSION = "1.0.0"

def generate_experimental_plan(case: LTFTCase) -> dict:
    return {"schema_version": PLAN_VERSION, "plan_status": "draft", "review_required": True, "recommendation_blocked": True, "case": asdict(case), "checklist": ["confirmar contrato experimental", "confirmar transporte e segurança", "definir ativação e analytics", "aprovação humana antes da execução"]}

def validate_pilot_record(record: dict) -> dict:
    required = ("pilot_id", "protocol_id", "execution_date", "raw_data_uri", "analytical_method")
    missing = [field for field in required if not record.get(field)]
    status = "measured_record" if not missing and record.get("execution_confirmed") is True else "blocked"
    return {"schema_version": PLAN_VERSION, "status": status, "missing_fields": missing, "recommendation_blocked": True, "record_is_evidence": status == "measured_record"}
