"""Distribuição Anderson-Schulz-Flory em base de carbono nos hidrocarbonetos."""
from math import isfinite


def validate_alpha(alpha: float) -> float:
    if isinstance(alpha, bool) or not isinstance(alpha, (int, float)):
        raise TypeError("alpha deve ser numérico")
    alpha = float(alpha)
    if not isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("alpha deve estar no intervalo aberto (0, 1)")
    return alpha


def carbon_fraction(alpha: float, carbon_number: int) -> float:
    """Fração de carbono ASF para uma cadeia Cn."""
    alpha = validate_alpha(alpha)
    if isinstance(carbon_number, bool) or not isinstance(carbon_number, int) or carbon_number < 1:
        raise ValueError("carbon_number deve ser inteiro positivo")
    return carbon_number * (1 - alpha) ** 2 * alpha ** (carbon_number - 1)


def tail_fraction(alpha: float, first_carbon: int) -> float:
    """Fração de carbono para Cn+, incluindo a cauda infinita."""
    alpha = validate_alpha(alpha)
    if isinstance(first_carbon, bool) or not isinstance(first_carbon, int) or first_carbon < 1:
        raise ValueError("first_carbon deve ser inteiro positivo")
    n = first_carbon
    return alpha ** (n - 1) * (n - (n - 1) * alpha)


def product_bands(alpha: float) -> dict[str, float]:
    bands = {
        "CH4": carbon_fraction(alpha, 1),
        "C2-C4": sum(carbon_fraction(alpha, n) for n in range(2, 5)),
        "C5-C11": sum(carbon_fraction(alpha, n) for n in range(5, 12)),
        "C12-C20": sum(carbon_fraction(alpha, n) for n in range(12, 21)),
        "C21+": tail_fraction(alpha, 21),
    }
    return {**bands, "C5+": tail_fraction(alpha, 5)}

