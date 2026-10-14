"""Modelos ASF avançados normalizados em base de carbono até C infinito."""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose, isfinite

from .asf import carbon_fraction, tail_fraction, validate_alpha

ADVANCED_ASF_VERSION = "1.0.0"
MODEL_TYPES = ("single", "dual_mixture", "segmented")


@dataclass(frozen=True)
class AdvancedASFContract:
    model_type: str
    alpha: float | None = None
    alpha_1: float | None = None
    alpha_2: float | None = None
    mixture_fraction: float | None = None
    transition_carbon: int | None = None
    methane_factor: float = 1.0
    c2_factor: float = 1.0
    contract_version: str = ADVANCED_ASF_VERSION


def validate_advanced_asf_contract(contract: AdvancedASFContract) -> tuple[str, ...]:
    errors: list[str] = []
    if contract.contract_version != ADVANCED_ASF_VERSION:
        errors.append(f"contract_version deve ser {ADVANCED_ASF_VERSION}.")
    if contract.model_type not in MODEL_TYPES:
        errors.append("model_type deve ser single, dual_mixture ou segmented.")

    def check_alpha(name: str, value: float | None, required: bool) -> None:
        if value is None:
            if required:
                errors.append(f"{name} é obrigatório para {contract.model_type}.")
            return
        try:
            validate_alpha(value)
        except (TypeError, ValueError):
            errors.append(f"{name} deve estar no intervalo aberto (0, 1).")

    check_alpha("alpha", contract.alpha, contract.model_type == "single")
    check_alpha("alpha_1", contract.alpha_1, contract.model_type in ("dual_mixture", "segmented"))
    check_alpha("alpha_2", contract.alpha_2, contract.model_type in ("dual_mixture", "segmented"))
    if contract.model_type == "dual_mixture":
        if (
            isinstance(contract.mixture_fraction, bool)
            or not isinstance(contract.mixture_fraction, (int, float))
            or not isfinite(contract.mixture_fraction)
            or not 0 <= contract.mixture_fraction <= 1
        ):
            errors.append("mixture_fraction deve estar entre 0 e 1.")
    elif contract.mixture_fraction is not None:
        errors.append("mixture_fraction somente é permitido em dual_mixture.")
    if contract.model_type == "segmented":
        if (
            isinstance(contract.transition_carbon, bool)
            or not isinstance(contract.transition_carbon, int)
            or contract.transition_carbon < 2
            or contract.transition_carbon > 59
        ):
            errors.append("transition_carbon deve ser inteiro entre 2 e 59.")
    elif contract.transition_carbon is not None:
        errors.append("transition_carbon somente é permitido em segmented.")
    for name in ("methane_factor", "c2_factor"):
        value = getattr(contract, name)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value < 0:
            errors.append(f"{name} deve ser finito e não negativo.")
    return tuple(dict.fromkeys(errors))


def _segmented_raw(contract: AdvancedASFContract, carbon_number: int) -> float:
    k = contract.transition_carbon
    if carbon_number <= k:
        return carbon_fraction(contract.alpha_1, carbon_number)
    anchor = carbon_fraction(contract.alpha_1, k)
    return anchor * carbon_number / k * contract.alpha_2 ** (carbon_number - k)


def _segmented_raw_tail(contract: AdvancedASFContract, first_carbon: int) -> float:
    k = contract.transition_carbon
    if first_carbon <= k:
        low = sum(_segmented_raw(contract, n) for n in range(first_carbon, k + 1))
        return low + _segmented_raw_tail(contract, k + 1)
    j = first_carbon - k
    anchor = carbon_fraction(contract.alpha_1, k)
    alpha_2 = contract.alpha_2
    series = alpha_2**j * (
        first_carbon / (1 - alpha_2) + alpha_2 / (1 - alpha_2) ** 2
    )
    return anchor / k * series


def _uncorrected_fraction(contract: AdvancedASFContract, carbon_number: int) -> float:
    if contract.model_type == "single":
        return carbon_fraction(contract.alpha, carbon_number)
    if contract.model_type == "dual_mixture":
        fraction = contract.mixture_fraction
        return (
            fraction * carbon_fraction(contract.alpha_1, carbon_number)
            + (1 - fraction) * carbon_fraction(contract.alpha_2, carbon_number)
        )
    raw_total = _segmented_raw_tail(contract, 1)
    return _segmented_raw(contract, carbon_number) / raw_total


def _uncorrected_tail(contract: AdvancedASFContract, first_carbon: int) -> float:
    if contract.model_type == "single":
        return tail_fraction(contract.alpha, first_carbon)
    if contract.model_type == "dual_mixture":
        fraction = contract.mixture_fraction
        return fraction * tail_fraction(contract.alpha_1, first_carbon) + (1 - fraction) * tail_fraction(contract.alpha_2, first_carbon)
    return _segmented_raw_tail(contract, first_carbon) / _segmented_raw_tail(contract, 1)


def _correction_normalizer(contract: AdvancedASFContract) -> float:
    c1 = _uncorrected_fraction(contract, 1)
    c2 = _uncorrected_fraction(contract, 2)
    return 1 + (contract.methane_factor - 1) * c1 + (contract.c2_factor - 1) * c2


def advanced_carbon_fraction(contract: AdvancedASFContract, carbon_number: int) -> float:
    errors = validate_advanced_asf_contract(contract)
    if errors:
        raise ValueError(errors)
    if isinstance(carbon_number, bool) or not isinstance(carbon_number, int) or carbon_number < 1:
        raise ValueError("carbon_number deve ser inteiro positivo.")
    factor = contract.methane_factor if carbon_number == 1 else contract.c2_factor if carbon_number == 2 else 1.0
    return factor * _uncorrected_fraction(contract, carbon_number) / _correction_normalizer(contract)


def advanced_tail_fraction(contract: AdvancedASFContract, first_carbon: int) -> float:
    errors = validate_advanced_asf_contract(contract)
    if errors:
        raise ValueError(errors)
    if isinstance(first_carbon, bool) or not isinstance(first_carbon, int) or first_carbon < 1:
        raise ValueError("first_carbon deve ser inteiro positivo.")
    tail = _uncorrected_tail(contract, first_carbon)
    if first_carbon <= 1:
        tail += (contract.methane_factor - 1) * _uncorrected_fraction(contract, 1)
    if first_carbon <= 2:
        tail += (contract.c2_factor - 1) * _uncorrected_fraction(contract, 2)
    return tail / _correction_normalizer(contract)


def advanced_distribution(contract: AdvancedASFContract, max_carbon: int = 60) -> dict[str, object]:
    if isinstance(max_carbon, bool) or not isinstance(max_carbon, int) or max_carbon < 2:
        raise ValueError("max_carbon deve ser inteiro maior ou igual a 2.")
    points = [
        {"carbon_number": n, "carbon_fraction": advanced_carbon_fraction(contract, n)}
        for n in range(1, max_carbon + 1)
    ]
    tail = advanced_tail_fraction(contract, max_carbon + 1)
    total = sum(point["carbon_fraction"] for point in points) + tail
    if not isclose(total, 1.0, abs_tol=1e-10):
        raise ArithmeticError("A distribuição avançada não fechou em 1.")
    return {
        "contract_version": contract.contract_version,
        "model_type": contract.model_type,
        "points": points,
        "tail": {"first_carbon": max_carbon + 1, "carbon_fraction": tail},
        "closure": total,
        "warning": "Modelo matemático; parâmetros não constituem evidência experimental nem recomendação.",
    }
