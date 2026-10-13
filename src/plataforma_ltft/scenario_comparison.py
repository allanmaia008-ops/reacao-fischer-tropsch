"""Comparação matemática de cenários ASF sem otimização experimental."""

from .asf import product_bands, validate_alpha
from .product_targets import normalize_target, target_fraction
from .result_panel import carbon_curve


def compare_asf_scenarios(alphas: list[float] | tuple[float, ...], target: str) -> dict:
    """Compara dois ou três valores únicos de alpha para o mesmo alvo e base."""
    if not isinstance(alphas, (list, tuple)) or not 2 <= len(alphas) <= 3:
        raise ValueError("A comparação exige dois ou três cenários.")
    normalized = [validate_alpha(alpha) for alpha in alphas]
    if len(set(normalized)) != len(normalized):
        raise ValueError("Os valores de alpha dos cenários devem ser distintos.")
    target = normalize_target(target)
    summaries = []
    curve = []
    for index, alpha in enumerate(normalized, start=1):
        scenario = f"Cenário {index}"
        summaries.append({
            "scenario": scenario,
            "alpha": alpha,
            "target_fraction": target_fraction(alpha, target),
            **product_bands(alpha),
        })
        curve.extend({**row, "scenario": scenario, "alpha": alpha} for row in carbon_curve(alpha, target))
    return {
        "target": target,
        "basis": "fracao_do_carbono_nos_hidrocarbonetos",
        "status": "sensibilidade_matematica_nao_otimizacao",
        "recommendation_blocked": True,
        "summaries": summaries,
        "curve": curve,
    }
