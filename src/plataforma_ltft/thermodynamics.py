"""Contrato termodinâmico e porta de validação para misturas Fischer–Tropsch."""

from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Sequence

THERMO_CONTRACT_VERSION = "1.0.0"
REQUIRED_PHASE_COVERAGE = ("syngas", "water", "light_hydrocarbons", "liquid_hydrocarbons", "waxes")


@dataclass(frozen=True)
class ThermodynamicContract:
    package_id: str
    package_version: str
    provider: str
    equation_of_state: str
    mixing_rule: str
    component_mapping: Mapping[str, str]
    pseudocomponent_method: str
    vle_method: str
    phase_coverage: Sequence[str]
    temperature_c: tuple[float, float]
    pressure_bar: tuple[float, float]
    source_ids: Sequence[str]
    validation_dataset_ids: Sequence[str]
    validation_metrics: Mapping[str, float]
    validation_status: str = "draft"
    contract_version: str = THERMO_CONTRACT_VERSION


def validate_thermodynamic_contract(contract: ThermodynamicContract) -> tuple[str, ...]:
    errors: list[str] = []
    if contract.contract_version != THERMO_CONTRACT_VERSION:
        errors.append(f"contract_version deve ser {THERMO_CONTRACT_VERSION}.")
    for name in ("package_id", "package_version", "provider", "equation_of_state", "mixing_rule", "pseudocomponent_method", "vle_method"):
        value = getattr(contract, name)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{name} é obrigatório.")
    if not contract.component_mapping:
        errors.append("component_mapping é obrigatório.")
    missing_phases = sorted(set(REQUIRED_PHASE_COVERAGE) - set(contract.phase_coverage))
    if missing_phases:
        errors.append("Cobertura de fases incompleta: " + ", ".join(missing_phases) + ".")
    for name in ("temperature_c", "pressure_bar"):
        bounds = getattr(contract, name)
        valid_bounds = (
            len(bounds) == 2
            and all(not isinstance(value, bool) and isinstance(value, (int, float)) and isfinite(value) for value in bounds)
            and bounds[0] < bounds[1]
        )
        if not valid_bounds:
            errors.append(f"{name} deve conter limites mínimo e máximo crescentes.")
    if not contract.source_ids:
        errors.append("Ao menos uma fonte rastreável é obrigatória.")
    if contract.validation_status not in ("draft", "compared", "validated"):
        errors.append("validation_status deve ser draft, compared ou validated.")
    if contract.validation_status in ("compared", "validated") and not contract.validation_dataset_ids:
        errors.append("Comparação ou validação exige validation_dataset_ids.")
    if contract.validation_status == "validated" and not contract.validation_metrics:
        errors.append("Pacote validado exige métricas quantitativas de erro.")
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value < 0 for value in contract.validation_metrics.values()):
        errors.append("As métricas de validação devem ser numéricas, finitas e não negativas.")
    return tuple(errors)


def thermodynamic_readiness(contract: ThermodynamicContract) -> dict[str, object]:
    errors = validate_thermodynamic_contract(contract)
    validated = not errors and contract.validation_status == "validated"
    reasons = errors or (() if validated else ("O pacote termodinâmico ainda não possui status validated.",))
    return {"contract_valid": not errors, "valid_for_process_model": validated, "blocking_reasons": reasons}
