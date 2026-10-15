"""Preparação HTFT isolada dos modelos LTFT."""

HTFT_SCHEMA_VERSION = "1.0.0"

def validate_htft_case(case: dict) -> tuple[str, ...]:
    required = ("case_id", "desired_product", "temperature_c", "catalyst_family", "oxygenate_policy", "coke_tracking", "secondary_reactions")
    errors = [f"campo ausente: {name}" for name in required if case.get(name) is None]
    if case.get("catalyst_family") not in (None, "Fe", "Fe-K", "Fe-Co"):
        errors.append("catalyst_family HTFT deve ser Fe, Fe-K ou Fe-Co")
    if case.get("temperature_c") is not None and not 280 <= case["temperature_c"] <= 350:
        errors.append("temperature_c deve estar no envelope HTFT versionado (280–350 °C)")
    return tuple(errors)

def route_model(case: dict) -> dict:
    errors = validate_htft_case(case)
    return {"schema_version": HTFT_SCHEMA_VERSION, "valid": not errors, "errors": errors, "model_family": "HTFT_diagnostic" if not errors else None, "recommendation_blocked": True, "ltft_execution_allowed": False}
