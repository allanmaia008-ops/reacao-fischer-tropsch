"""Preparação HTFT isolada dos modelos LTFT."""

HTFT_SCHEMA_VERSION = "1.0.0"
HTFT_TARGET = "light_olefins_C2_C4"
HTFT_REQUIRED_ANALYTICS = ("co_conversion", "carbon_balance", "oxygenates", "co2", "water", "coke", "unidentified_fraction", "thermal_gradient")
HTFT_REQUIRED_REACTIONS = ("wgs", "methanation", "boudouard")

def validate_htft_case(case: dict) -> tuple[str, ...]:
    required = ("schema_version", "case_id", "case_status", "desired_product", "product_carbon_range", "selectivity_basis", "temperature_c", "pressure_bar", "h2_co_molar_ratio", "reactor_type", "catalyst", "analytics", "acceptance_criteria", "oxygenate_policy", "coke_tracking", "secondary_reactions", "recommendation_blocked")
    errors = [f"campo ausente: {name}" for name in required if case.get(name) is None]
    catalyst = case.get("catalyst") or {}
    if catalyst.get("family") not in (None, "Fe", "Fe-K", "Fe-Co"):
        errors.append("catalyst.family HTFT deve ser Fe, Fe-K ou Fe-Co")
    if case.get("temperature_c") is not None and not 280 <= case["temperature_c"] <= 350:
        errors.append("temperature_c deve estar no envelope HTFT versionado (280–350 °C)")
    if case.get("desired_product") not in (None, HTFT_TARGET):
        errors.append("desired_product inicial HTFT deve ser light_olefins_C2_C4")
    if case.get("product_carbon_range") not in (None, {"min": 2, "max": 4}):
        errors.append("product_carbon_range deve ser C2-C4")
    analytics = case.get("analytics") or {}
    for name in HTFT_REQUIRED_ANALYTICS:
        if analytics.get(name) is not True:
            errors.append(f"analytics.{name} deve ser true")
    if analytics.get("olefin_paraffin_by_carbon") != [2, 3, 4]:
        errors.append("analytics.olefin_paraffin_by_carbon deve cobrir C2, C3 e C4")
    reactions = case.get("secondary_reactions") or []
    for name in HTFT_REQUIRED_REACTIONS:
        if name not in reactions:
            errors.append(f"secondary_reactions deve incluir {name}")
    criteria = case.get("acceptance_criteria") or {}
    for name in ("carbon_balance_error_max_pct", "steady_state_conversion_variation_max_pct", "steady_state_window_h", "replicates_min"):
        if criteria.get(name) is None:
            errors.append(f"acceptance_criteria.{name} é obrigatório")
    if case.get("recommendation_blocked") is not True:
        errors.append("recommendation_blocked deve permanecer true")
    return tuple(errors)

def route_model(case: dict) -> dict:
    errors = validate_htft_case(case)
    return {"schema_version": HTFT_SCHEMA_VERSION, "valid": not errors, "errors": errors,
            "model_family": "HTFT_diagnostic" if not errors else None,
            "target": HTFT_TARGET, "tracked_carbon_numbers": [2, 3, 4],
            "recommendation_blocked": True, "ltft_execution_allowed": False}
