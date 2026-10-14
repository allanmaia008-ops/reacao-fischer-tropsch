"""Portas do modelo quantitativo e sensibilidade sem inventar cinética."""

from collections.abc import Callable, Mapping

QUANTITATIVE_MODEL_VERSION = "1.0.0"

def quantitative_readiness(kinetic_readiness: Mapping[str, object], *, external_validation: bool, uncertainty_defined: bool) -> dict:
    reasons = list(kinetic_readiness.get("blocking_reasons", ()))
    if not kinetic_readiness.get("valid_for_rate_calculation", False):
        reasons.append("contrato cinético não está validado para cálculo de taxa")
    if not external_validation:
        reasons.append("validação externa ausente")
    if not uncertainty_defined:
        reasons.append("método de incerteza não definido")
    return {"schema_version": QUANTITATIVE_MODEL_VERSION, "status": "ready" if not reasons else "blocked", "reasons": list(dict.fromkeys(reasons)), "recommendation_blocked": bool(reasons)}

def one_at_a_time_sensitivity(baseline: Mapping[str, float], perturbations: Mapping[str, float], evaluator: Callable[[Mapping[str, float]], float], *, valid_ranges: Mapping[str, tuple[float, float]] | None = None) -> dict:
    """Calcula sensibilidades locais; marca pontos fora da faixa declarada."""
    base = float(evaluator(dict(baseline)))
    rows = []
    for variable, delta in perturbations.items():
        value = float(baseline[variable])
        trial = dict(baseline); trial[variable] = value + delta
        out = valid_ranges and not (valid_ranges[variable][0] <= trial[variable] <= valid_ranges[variable][1])
        trial_value = float(evaluator(trial))
        rows.append({"variable": variable, "baseline": value, "perturbed": trial[variable], "output_baseline": base, "output_perturbed": trial_value, "local_sensitivity": (trial_value - base) / delta if delta else None, "within_declared_range": not out})
    return {"schema_version": QUANTITATIVE_MODEL_VERSION, "method": "one_at_a_time", "rows": rows, "recommendation_blocked": True}
