"""Contrato do futuro modelo cinético; não executa taxas sem calibração aprovada."""

from dataclasses import dataclass
from typing import Mapping, Sequence

KINETIC_CONTRACT_VERSION = "1.0.0"
KINETIC_REQUIRED_VARIABLES = ("temperature", "partial_pressure_H2", "partial_pressure_CO")


@dataclass(frozen=True)
class KineticContract:
    model_id: str
    model_version: str
    rate_expression: str
    variables: Mapping[str, str]
    parameters: Mapping[str, float]
    parameter_units: Mapping[str, str]
    applicability_domain: Mapping[str, object]
    source_ids: Sequence[str]
    uncertainty_method: str
    validation_dataset_ids: Sequence[str]
    calibration_status: str = "draft"
    contract_version: str = KINETIC_CONTRACT_VERSION


def validate_kinetic_contract(contract: KineticContract) -> tuple[str, ...]:
    """Retorna pendências contratuais sem avaliar mérito ou executar a equação."""
    errors: list[str] = []
    for name in ("model_id", "model_version", "rate_expression", "uncertainty_method"):
        value = getattr(contract, name)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{name} é obrigatório.")
    if contract.contract_version != KINETIC_CONTRACT_VERSION:
        errors.append(f"contract_version deve ser {KINETIC_CONTRACT_VERSION}.")
    missing_variables = [name for name in KINETIC_REQUIRED_VARIABLES if not contract.variables.get(name)]
    if missing_variables:
        errors.append("Variáveis e unidades ausentes: " + ", ".join(missing_variables) + ".")
    if not contract.parameters:
        errors.append("parameters deve conter ao menos um parâmetro identificado.")
    if set(contract.parameters) != set(contract.parameter_units):
        errors.append("Todo parâmetro deve ter exatamente uma unidade declarada.")
    required_domain = {"ft_regime", "temperature_c", "pressure_bar", "catalyst_family"}
    missing_domain = sorted(required_domain - set(contract.applicability_domain))
    if missing_domain:
        errors.append("Domínio de aplicabilidade incompleto: " + ", ".join(missing_domain) + ".")
    if not contract.source_ids:
        errors.append("Ao menos uma fonte rastreável é obrigatória.")
    if contract.calibration_status not in ("draft", "calibrated", "validated"):
        errors.append("calibration_status deve ser draft, calibrated ou validated.")
    if contract.calibration_status in ("calibrated", "validated") and not contract.validation_dataset_ids:
        errors.append("Modelos calibrados ou validados exigem validation_dataset_ids.")
    return tuple(errors)


def kinetic_readiness(contract: KineticContract) -> dict[str, object]:
    """Libera cálculo apenas para contrato validado e sem pendências."""
    errors = validate_kinetic_contract(contract)
    return {
        "contract_valid": not errors,
        "valid_for_rate_calculation": not errors and contract.calibration_status == "validated",
        "blocking_reasons": errors or (() if contract.calibration_status == "validated" else (
            "O contrato cinético ainda não possui status validated.",
        )),
    }
