"""Dados de apresentação do painel científico, sem alterar o cálculo ASF."""

from .asf import carbon_fraction, tail_fraction
from .product_targets import normalize_target


DISPLAY_MAX_CARBON = 60


def target_bounds(target: str) -> tuple[int, int]:
    """Limites visíveis do alvo na curva C1–C60."""
    target = normalize_target(target)
    ranges = {
        "CH4": (1, 1),
        "C2-C4": (2, 4),
        "C5-C11": (5, 11),
        "C12-C20": (12, 20),
        "C21+": (21, DISPLAY_MAX_CARBON),
        "C5+": (5, DISPLAY_MAX_CARBON),
    }
    if target in ranges:
        return ranges[target]
    carbon_number = int(target[1:])
    return carbon_number, carbon_number


def carbon_curve(alpha: float, target: str) -> list[dict[str, object]]:
    """Série C1–C60 para visualização, mantendo a cauda fora do gráfico explícita."""
    first, last = target_bounds(target)
    return [
        {
            "carbon_number": carbon_number,
            "carbon_fraction": carbon_fraction(alpha, carbon_number),
            "target_group": "Faixa-alvo" if first <= carbon_number <= last else "Demais Cn",
        }
        for carbon_number in range(1, DISPLAY_MAX_CARBON + 1)
    ]


def curve_closure(alpha: float) -> dict[str, float]:
    """Fecha a curva exibida com a cauda analítica C61+."""
    shown = sum(carbon_fraction(alpha, n) for n in range(1, DISPLAY_MAX_CARBON + 1))
    tail = tail_fraction(alpha, DISPLAY_MAX_CARBON + 1)
    return {"C1-C60": shown, "C61+": tail, "total": shown + tail}


def readiness_rows(readiness: dict) -> list[dict[str, str]]:
    """Transforma o JSON de prontidão em linhas legíveis."""
    labels = (
        ("Triagem ASF", "valid_for_screening"),
        ("Plano experimental", "valid_for_experimental_plan"),
        ("Cálculo de taxa", "valid_for_rate_calculation"),
    )
    return [
        {"Uso": label, "Estado": "Disponível" if readiness.get(key) else "Bloqueado"}
        for label, key in labels
    ]
