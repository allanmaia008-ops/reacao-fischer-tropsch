"""Diagnósticos dimensionais de transporte para experimentos Fischer–Tropsch."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Mapping, Sequence

TRANSPORT_DIAGNOSTICS_VERSION = "1.0.0"
CRITERION_PROFILE_VERSION = "conservative-screening-v1"
CRITERION_STATUSES = ("passed", "failed", "not_assessable_missing_inputs")


@dataclass(frozen=True)
class TransportDiagnosticsContract:
    observed_rate_mol_m3_s: float | None = None
    particle_radius_m: float | None = None
    surface_reactant_concentration_mol_m3: float | None = None
    bulk_reactant_concentration_mol_m3: float | None = None
    effective_diffusivity_m2_s: float | None = None
    reaction_order_abs: float | None = None
    external_mass_transfer_coefficient_m_s: float | None = None
    reaction_enthalpy_abs_j_mol: float | None = None
    activation_energy_j_mol: float | None = None
    temperature_k: float | None = None
    external_heat_transfer_coefficient_w_m2_k: float | None = None
    relative_uncertainty_fraction: Mapping[str, float] | None = None
    source_ids: Sequence[str] = ()
    field_sources: Mapping[str, str] | None = None
    weisz_prater_limit: float = 0.3
    mears_mass_limit: float = 0.15
    mears_heat_limit: float = 0.15
    gas_constant_j_mol_k: float = 8.314462618
    criterion_profile: str = CRITERION_PROFILE_VERSION
    recommendation_blocked: bool = True
    contract_version: str = TRANSPORT_DIAGNOSTICS_VERSION


_INPUT_FIELDS = (
    "observed_rate_mol_m3_s", "particle_radius_m",
    "surface_reactant_concentration_mol_m3", "bulk_reactant_concentration_mol_m3",
    "effective_diffusivity_m2_s", "reaction_order_abs",
    "external_mass_transfer_coefficient_m_s", "reaction_enthalpy_abs_j_mol",
    "activation_energy_j_mol", "temperature_k",
    "external_heat_transfer_coefficient_w_m2_k",
)

_REQUIRED = {
    "weisz_prater": (
        "observed_rate_mol_m3_s", "particle_radius_m",
        "surface_reactant_concentration_mol_m3", "effective_diffusivity_m2_s",
    ),
    "mears_mass": (
        "observed_rate_mol_m3_s", "particle_radius_m", "reaction_order_abs",
        "external_mass_transfer_coefficient_m_s", "bulk_reactant_concentration_mol_m3",
    ),
    "mears_heat": (
        "observed_rate_mol_m3_s", "particle_radius_m", "reaction_enthalpy_abs_j_mol",
        "activation_energy_j_mol", "temperature_k",
        "external_heat_transfer_coefficient_w_m2_k",
    ),
}


def _positive(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and isfinite(value) and value > 0


def validate_transport_diagnostics_contract(contract: TransportDiagnosticsContract) -> tuple[str, ...]:
    errors: list[str] = []
    if contract.contract_version != TRANSPORT_DIAGNOSTICS_VERSION:
        errors.append(f"contract_version deve ser {TRANSPORT_DIAGNOSTICS_VERSION}.")
    if contract.criterion_profile != CRITERION_PROFILE_VERSION:
        errors.append(f"criterion_profile deve ser {CRITERION_PROFILE_VERSION}.")
    if contract.recommendation_blocked is not True:
        errors.append("recommendation_blocked deve permanecer true.")
    if not contract.source_ids or any(not isinstance(item, str) or not item.strip() for item in contract.source_ids):
        errors.append("source_ids deve conter identificadores não vazios.")
    for name in _INPUT_FIELDS:
        value = getattr(contract, name)
        if value is not None and not _positive(value):
            errors.append(f"{name} deve ser positivo e finito quando informado.")
    for name in ("weisz_prater_limit", "mears_mass_limit", "mears_heat_limit", "gas_constant_j_mol_k"):
        if not _positive(getattr(contract, name)):
            errors.append(f"{name} deve ser positivo e finito.")

    field_sources = contract.field_sources or {}
    populated = {name for name in _INPUT_FIELDS if getattr(contract, name) is not None}
    absent_sources = sorted(name for name in populated if not field_sources.get(name))
    if absent_sources:
        errors.append("field_sources ausente para campos preenchidos: " + ", ".join(absent_sources) + ".")
    unknown_sources = sorted(set(field_sources) - populated)
    if unknown_sources:
        errors.append("field_sources referencia campo ausente ou desconhecido: " + ", ".join(unknown_sources) + ".")

    uncertainty = contract.relative_uncertainty_fraction or {}
    for name, value in uncertainty.items():
        if name not in populated:
            errors.append(f"relative_uncertainty_fraction referencia campo ausente ou desconhecido: {name}.")
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or not 0 <= value < 1:
            errors.append(f"Incerteza relativa de {name} deve estar no intervalo [0, 1).")
    return tuple(dict.fromkeys(errors))


def _bounds(nominal: float, numerator: Sequence[str], denominator: Mapping[str, int], uncertainty: Mapping[str, float]) -> tuple[float, float]:
    low = nominal
    high = nominal
    for name in numerator:
        u = uncertainty.get(name, 0.0)
        low *= 1 - u
        high *= 1 + u
    for name, exponent in denominator.items():
        u = uncertainty.get(name, 0.0)
        low /= (1 + u) ** exponent
        high /= (1 - u) ** exponent
    return low, high


def _criterion(value: float, limit: float, equation: str, lower: float, upper: float) -> dict[str, Any]:
    return {
        "status": "passed" if value < limit else "failed",
        "value": value,
        "limit": limit,
        "comparison": "<",
        "equation": equation,
        "sensitivity_interval": {"lower": lower, "upper": upper},
        "sensitivity_crosses_limit": lower < limit <= upper,
        "missing_inputs": [],
    }


def assess_transport_diagnostics(contract: TransportDiagnosticsContract) -> dict[str, Any]:
    """Calcula testes de triagem; não certifica ausência de limitações."""
    errors = validate_transport_diagnostics_contract(contract)
    if errors:
        raise ValueError(errors)
    uncertainty = contract.relative_uncertainty_fraction or {}
    results: dict[str, dict[str, Any]] = {}
    for criterion, required in _REQUIRED.items():
        missing = [name for name in required if getattr(contract, name) is None]
        if missing:
            results[criterion] = {
                "status": "not_assessable_missing_inputs", "value": None, "limit": None,
                "comparison": None, "equation": None, "sensitivity_interval": None,
                "sensitivity_crosses_limit": None, "missing_inputs": missing,
            }

    r = contract.observed_rate_mol_m3_s
    radius = contract.particle_radius_m
    if "weisz_prater" not in results:
        value = r * radius**2 / (contract.surface_reactant_concentration_mol_m3 * contract.effective_diffusivity_m2_s)
        low, high = _bounds(value, ("observed_rate_mol_m3_s", "particle_radius_m", "particle_radius_m"), {"surface_reactant_concentration_mol_m3": 1, "effective_diffusivity_m2_s": 1}, uncertainty)
        results["weisz_prater"] = _criterion(value, contract.weisz_prater_limit, "r_obs*R_p^2/(C_As*D_eff)", low, high)
    if "mears_mass" not in results:
        value = contract.reaction_order_abs * r * radius / (contract.external_mass_transfer_coefficient_m_s * contract.bulk_reactant_concentration_mol_m3)
        low, high = _bounds(value, ("reaction_order_abs", "observed_rate_mol_m3_s", "particle_radius_m"), {"external_mass_transfer_coefficient_m_s": 1, "bulk_reactant_concentration_mol_m3": 1}, uncertainty)
        results["mears_mass"] = _criterion(value, contract.mears_mass_limit, "n*r_obs*R_p/(k_c*C_Ab)", low, high)
    if "mears_heat" not in results:
        value = (contract.reaction_enthalpy_abs_j_mol * r * radius * contract.activation_energy_j_mol) / (contract.external_heat_transfer_coefficient_w_m2_k * contract.gas_constant_j_mol_k * contract.temperature_k**2)
        low, high = _bounds(value, ("reaction_enthalpy_abs_j_mol", "observed_rate_mol_m3_s", "particle_radius_m", "activation_energy_j_mol"), {"external_heat_transfer_coefficient_w_m2_k": 1, "temperature_k": 2}, uncertainty)
        results["mears_heat"] = _criterion(value, contract.mears_heat_limit, "|deltaH|*r_obs*R_p*E_a/(h*T^2*R)", low, high)

    statuses = [item["status"] for item in results.values()]
    overall = "failed" if "failed" in statuses else "passed_all_assessed" if all(status == "passed" for status in statuses) else "incomplete"
    return {
        "contract_version": contract.contract_version,
        "criterion_profile": contract.criterion_profile,
        "overall_status": overall,
        "all_transport_criteria_passed": overall == "passed_all_assessed",
        "kinetic_interpretation_approved": False,
        "recommendation_blocked": True,
        "criteria": results,
        "source_ids": list(contract.source_ids),
        "warning": "Testes de triagem dependentes das entradas e hipóteses; exigem revisão humana e não provam, isoladamente, cinética intrínseca.",
    }
