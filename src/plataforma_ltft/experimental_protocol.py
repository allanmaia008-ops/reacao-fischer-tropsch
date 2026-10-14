"""Contrato experimental v2 com migração sem preenchimento de dados ausentes."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Any, Mapping, Sequence

from .domain import LTFTCase, validate_case

EXPERIMENTAL_PROTOCOL_VERSION = "2.0.0"
PROTOCOL_STATUSES = ("planned", "executed")

REACTOR_FIELDS = (
    "internal_diameter_mm", "heated_length_mm", "bed_porosity_fraction",
    "catalyst_particle_diameter_um", "catalyst_mass_g", "inert_diluent",
    "dilution_ratio_mass", "diluent_particle_diameter_um",
)
ACTIVATION_FIELDS = (
    "gas_composition_mol_fraction", "total_flow_mol_s", "temperature_c",
    "heating_rate_c_min", "hold_time_h", "pressure_bar",
)
ANALYTICS_FIELDS = (
    "online_detectors", "species_ranges", "calibration_protocol",
    "detection_limits", "quantification_limits", "heavy_fraction_method",
    "heavy_fraction_recovery_pct",
)


@dataclass(frozen=True)
class ExperimentalProtocolV2:
    protocol_id: str
    base_case: Mapping[str, Any]
    reactor_configuration: Mapping[str, Any]
    activation_protocol: Mapping[str, Any]
    analytics: Mapping[str, Any]
    source_ids: Sequence[str]
    field_sources: Mapping[str, str]
    status: str = "planned"
    execution_confirmed: bool = False
    recommendation_blocked: bool = True
    contract_version: str = EXPERIMENTAL_PROTOCOL_VERSION


@dataclass(frozen=True)
class ExperimentalProtocolValidation:
    structurally_valid: bool
    ready_for_transport_assessment: bool
    ready_for_experimental_execution_review: bool
    missing_fields: tuple[str, ...]
    errors: tuple[str, ...]


def _finite_positive(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and isfinite(value) and value > 0


def _missing(section: str, data: Mapping[str, Any], fields: Sequence[str]) -> list[str]:
    return [f"{section}.{field}" for field in fields if data.get(field) is None]


def migrate_case_to_experimental_protocol_v2(
    case: LTFTCase | Mapping[str, Any], protocol_id: str, source_ids: Sequence[str]
) -> ExperimentalProtocolV2:
    """Preserva o caso e deixa campos novos nulos para revisão humana."""
    payload = asdict(case) if isinstance(case, LTFTCase) else dict(case)
    normalized_case = LTFTCase(**payload)
    case_validation = validate_case(normalized_case)
    if case_validation.errors:
        raise ValueError(case_validation.errors)
    return ExperimentalProtocolV2(
        protocol_id=protocol_id,
        base_case=payload,
        reactor_configuration={field: None for field in REACTOR_FIELDS},
        activation_protocol={field: None for field in ACTIVATION_FIELDS},
        analytics={field: None for field in ANALYTICS_FIELDS},
        source_ids=tuple(source_ids),
        field_sources={},
    )


def validate_experimental_protocol_v2(contract: ExperimentalProtocolV2) -> ExperimentalProtocolValidation:
    errors: list[str] = []
    if contract.contract_version != EXPERIMENTAL_PROTOCOL_VERSION:
        errors.append(f"contract_version deve ser {EXPERIMENTAL_PROTOCOL_VERSION}.")
    if not isinstance(contract.protocol_id, str) or not contract.protocol_id.strip():
        errors.append("protocol_id é obrigatório.")
    if contract.status not in PROTOCOL_STATUSES:
        errors.append("status deve ser planned ou executed.")
    if not isinstance(contract.execution_confirmed, bool):
        errors.append("execution_confirmed deve ser booleano.")
    if contract.recommendation_blocked is not True:
        errors.append("recommendation_blocked deve permanecer true.")
    if contract.status == "executed" and not contract.execution_confirmed:
        errors.append("status executed exige execution_confirmed=true.")
    if not contract.source_ids or any(not isinstance(item, str) or not item.strip() for item in contract.source_ids):
        errors.append("source_ids deve conter identificadores não vazios.")

    try:
        case = LTFTCase(**dict(contract.base_case))
    except (TypeError, ValueError) as exc:
        errors.append(f"base_case incompatível: {exc}")
    else:
        case_result = validate_case(case)
        errors.extend(f"base_case: {error}" for error in case_result.errors)

    sections = (
        ("reactor_configuration", contract.reactor_configuration, REACTOR_FIELDS),
        ("activation_protocol", contract.activation_protocol, ACTIVATION_FIELDS),
        ("analytics", contract.analytics, ANALYTICS_FIELDS),
    )
    for section_name, section, allowed_fields in sections:
        if not isinstance(section, Mapping):
            errors.append(f"{section_name} deve ser objeto.")
            continue
        unknown = sorted(set(section) - set(allowed_fields))
        if unknown:
            errors.append(f"{section_name} contém campos desconhecidos: " + ", ".join(unknown) + ".")

    reactor = contract.reactor_configuration
    for field in (
        "internal_diameter_mm", "heated_length_mm", "catalyst_particle_diameter_um",
        "catalyst_mass_g", "dilution_ratio_mass", "diluent_particle_diameter_um",
    ):
        if reactor.get(field) is not None and not _finite_positive(reactor.get(field)):
            errors.append(f"reactor_configuration.{field} deve ser positivo e finito.")
    porosity = reactor.get("bed_porosity_fraction")
    if porosity is not None and (
        isinstance(porosity, bool) or not isinstance(porosity, (int, float)) or not isfinite(porosity) or not 0 < porosity < 1
    ):
        errors.append("reactor_configuration.bed_porosity_fraction deve estar entre 0 e 1.")
    diluent = reactor.get("inert_diluent")
    if diluent is not None and (not isinstance(diluent, str) or not diluent.strip()):
        errors.append("reactor_configuration.inert_diluent não pode ser vazio.")

    activation = contract.activation_protocol
    for field in ("total_flow_mol_s", "heating_rate_c_min", "hold_time_h", "pressure_bar"):
        if activation.get(field) is not None and not _finite_positive(activation.get(field)):
            errors.append(f"activation_protocol.{field} deve ser positivo e finito.")
    temperature = activation.get("temperature_c")
    if temperature is not None and (
        isinstance(temperature, bool) or not isinstance(temperature, (int, float)) or not isfinite(temperature) or temperature <= -273.15
    ):
        errors.append("activation_protocol.temperature_c deve ser maior que zero absoluto.")
    gas = activation.get("gas_composition_mol_fraction")
    if gas is not None:
        if not isinstance(gas, Mapping) or not gas:
            errors.append("activation_protocol.gas_composition_mol_fraction deve ser mapa não vazio.")
        elif any(not isinstance(key, str) or not key.strip() or not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value) or value < 0 for key, value in gas.items()):
            errors.append("Composição do gás de ativação contém valor inválido.")
        elif abs(sum(gas.values()) - 1.0) > 1e-6:
            errors.append("Frações molares do gás de ativação devem somar 1,0.")

    analytics = contract.analytics
    detectors = analytics.get("online_detectors")
    if detectors is not None and (
        not isinstance(detectors, Sequence) or isinstance(detectors, (str, bytes))
        or not detectors or any(not isinstance(item, str) or not item.strip() for item in detectors)
    ):
        errors.append("analytics.online_detectors deve ser lista não vazia de textos.")
    recovery = analytics.get("heavy_fraction_recovery_pct")
    if recovery is not None and (
        isinstance(recovery, bool) or not isinstance(recovery, (int, float)) or not isfinite(recovery) or not 0 <= recovery <= 100
    ):
        errors.append("analytics.heavy_fraction_recovery_pct deve estar entre 0 e 100.")
    for field in ("calibration_protocol", "heavy_fraction_method"):
        value = analytics.get(field)
        if value is not None and (not isinstance(value, str) or not value.strip()):
            errors.append(f"analytics.{field} não pode ser vazio.")
    for field in ("species_ranges", "detection_limits", "quantification_limits"):
        value = analytics.get(field)
        if value is not None and (not isinstance(value, Mapping) or not value):
            errors.append(f"analytics.{field} deve ser mapa não vazio.")

    missing = []
    for section_name, section, fields in sections:
        if isinstance(section, Mapping):
            missing.extend(_missing(section_name, section, fields))
    populated_paths = {
        f"{section_name}.{field}"
        for section_name, section, fields in sections
        if isinstance(section, Mapping)
        for field in fields
        if section.get(field) is not None
    }
    absent_sources = sorted(path for path in populated_paths if not contract.field_sources.get(path))
    if absent_sources:
        errors.append("field_sources ausente para campos preenchidos: " + ", ".join(absent_sources) + ".")
    unknown_sources = sorted(set(contract.field_sources) - populated_paths)
    if unknown_sources:
        errors.append("field_sources referencia campo ausente ou desconhecido: " + ", ".join(unknown_sources) + ".")

    structurally_valid = not errors
    ready = structurally_valid and not missing
    return ExperimentalProtocolValidation(
        structurally_valid=structurally_valid,
        ready_for_transport_assessment=ready,
        ready_for_experimental_execution_review=ready and contract.status == "planned" and not contract.execution_confirmed,
        missing_fields=tuple(missing),
        errors=tuple(errors),
    )
