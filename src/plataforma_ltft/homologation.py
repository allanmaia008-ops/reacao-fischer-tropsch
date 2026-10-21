"""Technical preflight report with explicit separation from actual acceptance."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

REQUIRED_GATES = ("scientific_data_approved", "isolated_environment", "security_review", "recovery_drill", "owner_signoff")


def build_preflight_report(checks: list[Mapping[str, Any]], *, gates: Mapping[str, bool] | None = None) -> dict[str, Any]:
    gates = dict(gates or {})
    gate_results = {name: bool(gates.get(name, False)) for name in REQUIRED_GATES}
    checks_passed = bool(checks) and all(check.get("passed") is True for check in checks)
    all_gates = all(gate_results.values())
    return {
        "schema_version":"1.0.0",
        "generated_at":datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "technical_preflight":"passed" if checks_passed else "failed",
        "homologation":"accepted" if checks_passed and all_gates else "pending_gates",
        "checks":[dict(check) for check in checks],
        "required_gates":gate_results,
        "scientific_acceptance":"separate_human_gate",
        "production_ready":False,
        "limitations":["Automated tests do not establish scientific validity.","Security review, isolated deployment, recovery drill and owner sign-off require real evidence."],
    }
