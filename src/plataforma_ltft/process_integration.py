"""Integração de balanços e avaliação técnico-econômica com portas explícitas."""

def integrated_balance_gate(*, syngas_closed: bool, ft_closed: bool, upgrading_closed: bool, oxygen_accounted: bool) -> dict:
    checks = {"syngas": syngas_closed, "ft": ft_closed, "upgrading": upgrading_closed, "oxygen": oxygen_accounted}
    return {"checks": checks, "status": "ready" if all(checks.values()) else "blocked", "recommendation_blocked": True, "missing": [name for name, ok in checks.items() if not ok]}

def economic_scenario(*, capacity_kg_h: float, h2_cost_per_kg: float, electricity_cost_per_mwh: float, carbon_cost_per_t: float, capex: float, opex_per_kg: float, product_price_per_kg: float) -> dict:
    revenue = capacity_kg_h * product_price_per_kg
    variable = capacity_kg_h * opex_per_kg + h2_cost_per_kg * capacity_kg_h
    return {"capacity_kg_h": capacity_kg_h, "revenue_per_h": revenue, "variable_cost_per_h": variable, "carbon_cost_per_t": carbon_cost_per_t, "capex": capex, "margin_per_h": revenue - variable, "recommendation_blocked": True}

def integrated_validation_gate(*, external_dataset: bool, residuals_checked: bool, uncertainty_checked: bool, independent_review: bool) -> dict:
    checks = {"external_dataset": external_dataset, "residuals": residuals_checked, "uncertainty": uncertainty_checked, "independent_review": independent_review}
    return {"status": "validated" if all(checks.values()) else "blocked", "checks": checks, "recommendation_blocked": not all(checks.values()), "missing": [name for name, ok in checks.items() if not ok]}
