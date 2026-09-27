"""Contrato científico v1; valida entradas sem inferir desempenho catalítico."""

from dataclasses import dataclass
from math import isclose, isfinite
from typing import Mapping

CASE_SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True)
class LTFTCase:
    schema_version: str = CASE_SCHEMA_VERSION
    composition: str | None = None
    active_family: str | None = None
    active_phase_hypothesis: str | None = None
    support: str | None = None
    active_metal_loading_wt_pct: float | None = None
    promoter: str | None = None
    promoter_loading_wt_pct: float | None = None
    precursor: str | None = None
    activation_gas: str | None = None
    activation_temperature_c: float | None = None
    activation_duration_h: float | None = None
    reactor_type: str | None = None
    temperature_c: float | None = None
    pressure_bar: float | None = None
    h2_co_molar_ratio: float | None = None
    feed_composition_mol_fraction: Mapping[str, float] | None = None
    feed_flow_mol_s: float | None = None
    ghsv_h_1: float | None = None
    whsv_h_1: float | None = None
    catalyst_mass_g: float | None = None
    bed_volume_ml: float | None = None
    time_on_stream_h: float | None = None
    desired_product: str | None = None


@dataclass(frozen=True)
class ValidationResult:
    valid_for_screening: bool
    valid_for_experimental_plan: bool
    valid_for_rate_calculation: bool
    missing_screening_fields: tuple[str, ...]
    missing_experimental_fields: tuple[str, ...]
    missing_rate_fields: tuple[str, ...]
    errors: tuple[str, ...]


def _is_finite_number(value) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and isfinite(value)


def validate_case(case: LTFTCase) -> ValidationResult:
    """Valida completude, unidades fixas e dependências condicionais do contrato v1."""
    screening_fields = (
        "composition", "active_family", "active_phase_hypothesis", "support",
        "active_metal_loading_wt_pct", "temperature_c", "pressure_bar",
        "h2_co_molar_ratio", "desired_product",
    )
    experimental_fields = (
        "precursor", "activation_gas", "activation_temperature_c",
        "activation_duration_h", "reactor_type", "feed_composition_mol_fraction",
        "feed_flow_mol_s", "time_on_stream_h",
    )
    missing_screening = tuple(name for name in screening_fields if getattr(case, name) is None)
    missing_experimental = [name for name in experimental_fields if getattr(case, name) is None]
    errors: list[str] = []

    if case.schema_version != CASE_SCHEMA_VERSION:
        errors.append(f"schema_version deve ser {CASE_SCHEMA_VERSION}.")
    if case.active_family is not None and case.active_family not in ("Co", "Fe", "Co-Fe"):
        errors.append("Família ativa deve ser Co, Fe ou Co-Fe exploratória.")
    if case.desired_product is not None:
        try:
            from .product_targets import normalize_target
            normalize_target(case.desired_product)
        except ValueError as exc:
            errors.append(str(exc))

    for name in (
        "composition", "active_phase_hypothesis", "support", "promoter", "precursor",
        "activation_gas", "reactor_type",
    ):
        value = getattr(case, name)
        if value is not None and (not isinstance(value, str) or not value.strip()):
            errors.append(f"{name} não pode ser vazio.")

    numeric_fields = (
        "active_metal_loading_wt_pct", "promoter_loading_wt_pct",
        "activation_temperature_c", "activation_duration_h", "temperature_c",
        "pressure_bar", "h2_co_molar_ratio", "feed_flow_mol_s", "ghsv_h_1",
        "whsv_h_1", "catalyst_mass_g", "bed_volume_ml", "time_on_stream_h",
    )
    for name in numeric_fields:
        value = getattr(case, name)
        if value is None:
            continue
        if not _is_finite_number(value):
            errors.append(f"{name} deve ser um número finito.")
        elif name in ("temperature_c", "activation_temperature_c"):
            if value <= -273.15:
                errors.append(f"{name} deve ser maior que zero absoluto.")
        elif value <= 0:
            errors.append(f"{name} deve ser positivo.")

    for name in ("active_metal_loading_wt_pct", "promoter_loading_wt_pct"):
        value = getattr(case, name)
        if _is_finite_number(value) and value > 100:
            errors.append(f"{name} não pode exceder 100 % em massa.")
    if _is_finite_number(case.active_metal_loading_wt_pct) and _is_finite_number(case.promoter_loading_wt_pct):
        if case.active_metal_loading_wt_pct + case.promoter_loading_wt_pct > 100:
            errors.append("A soma das cargas de metal ativo e promotor não pode exceder 100 % em massa.")

    if bool(case.promoter) != (case.promoter_loading_wt_pct is not None):
        errors.append("Promotor e promoter_loading_wt_pct devem ser informados juntos.")

    feed = case.feed_composition_mol_fraction
    if feed is not None:
        if not isinstance(feed, Mapping) or not feed:
            errors.append("feed_composition_mol_fraction deve ser um mapa não vazio.")
        else:
            bad = [key for key, value in feed.items() if not isinstance(key, str) or not key.strip() or not _is_finite_number(value) or value < 0]
            if bad:
                errors.append("A composição da alimentação contém componente ou fração inválida.")
            else:
                total = sum(feed.values())
                if not isclose(total, 1.0, abs_tol=1e-6):
                    errors.append("As frações molares da alimentação devem somar 1,0.")
                if "H2" not in feed or "CO" not in feed or feed.get("CO", 0) <= 0:
                    errors.append("A alimentação deve conter H2 e CO, com fração de CO positiva.")
                elif case.h2_co_molar_ratio is not None:
                    calculated = feed["H2"] / feed["CO"]
                    if not isclose(calculated, case.h2_co_molar_ratio, rel_tol=0.02, abs_tol=1e-6):
                        errors.append("h2_co_molar_ratio diverge da composição molar da alimentação em mais de 2 %.")

    has_ghsv_basis = case.ghsv_h_1 is not None and case.bed_volume_ml is not None
    has_whsv_basis = case.whsv_h_1 is not None and case.catalyst_mass_g is not None
    if case.ghsv_h_1 is not None and case.bed_volume_ml is None:
        errors.append("bed_volume_ml é obrigatório quando GHSV é informado.")
    if case.bed_volume_ml is not None and case.ghsv_h_1 is None:
        errors.append("ghsv_h_1 é obrigatório quando o volume do leito é informado.")
    if case.whsv_h_1 is not None and case.catalyst_mass_g is None:
        errors.append("catalyst_mass_g é obrigatório quando WHSV é informado.")
    if case.catalyst_mass_g is not None and case.whsv_h_1 is None:
        errors.append("whsv_h_1 é obrigatório quando a massa de catalisador é informada.")
    if not (has_ghsv_basis or has_whsv_basis):
        missing_experimental.append("ghsv_h_1+bed_volume_ml ou whsv_h_1+catalyst_mass_g")

    valid_for_screening = not missing_screening and not errors
    valid_for_experimental_plan = valid_for_screening and not missing_experimental
    rate_fields = (
        "rate_equation", "rate_parameters", "parameter_units", "uncertainties",
        "measured_conversion", "carbon_balance",
    )
    return ValidationResult(
        valid_for_screening=valid_for_screening,
        valid_for_experimental_plan=valid_for_experimental_plan,
        valid_for_rate_calculation=False,
        missing_screening_fields=missing_screening,
        missing_experimental_fields=tuple(missing_experimental),
        missing_rate_fields=rate_fields,
        errors=tuple(errors),
    )
