"""Contrato do reator LTFT e diagnóstico estrutural sem prever conversão."""

from dataclasses import dataclass
from math import isfinite
from typing import Mapping

from .kinetics import KineticContract, kinetic_readiness

REACTOR_CONTRACT_VERSION = "1.0.0"
SUPPORTED_REACTOR_TYPES = ("fixed_bed_pfr", "slurry_cstr")


def _positive_finite(value: object) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and isfinite(value) and value > 0


@dataclass(frozen=True)
class ReactorContract:
    reactor_id: str
    reactor_type: str
    feed_molar_flow_mol_s: Mapping[str, float]
    temperature_c: float
    pressure_bar: float
    catalyst_mass_g: float | None = None
    bed_volume_ml: float | None = None
    ghsv_h_1: float | None = None
    whsv_h_1: float | None = None
    geometry: Mapping[str, float] | None = None
    energy_model: str = "not_selected"
    pressure_drop_model: str = "not_selected"
    mass_transfer_model: str = "not_selected"
    wgs_model: str = "not_selected"
    deactivation_model: str = "not_selected"
    contract_version: str = REACTOR_CONTRACT_VERSION


def validate_reactor_contract(contract: ReactorContract) -> tuple[str, ...]:
    errors: list[str] = []
    if contract.contract_version != REACTOR_CONTRACT_VERSION:
        errors.append(f"contract_version deve ser {REACTOR_CONTRACT_VERSION}.")
    if not isinstance(contract.reactor_id, str) or not contract.reactor_id.strip():
        errors.append("reactor_id é obrigatório.")
    if contract.reactor_type not in SUPPORTED_REACTOR_TYPES:
        errors.append("reactor_type deve ser fixed_bed_pfr ou slurry_cstr.")
    if not contract.feed_molar_flow_mol_s:
        errors.append("A alimentação molar é obrigatória.")
    else:
        for species, flow in contract.feed_molar_flow_mol_s.items():
            if not isinstance(species, str) or not species.strip() or isinstance(flow, bool) or not isinstance(flow, (int, float)) or not isfinite(flow) or flow < 0:
                errors.append("A alimentação contém espécie ou vazão inválida.")
                break
        if contract.feed_molar_flow_mol_s.get("CO", 0) <= 0 or contract.feed_molar_flow_mol_s.get("H2", 0) <= 0:
            errors.append("A alimentação deve conter vazões positivas de CO e H2.")
    for name in ("temperature_c", "pressure_bar"):
        value = getattr(contract, name)
        if not _positive_finite(value):
            errors.append(f"{name} deve ser positivo e finito.")
    for name in ("catalyst_mass_g", "bed_volume_ml", "ghsv_h_1", "whsv_h_1"):
        value = getattr(contract, name)
        if value is not None and not _positive_finite(value):
            errors.append(f"{name} deve ser positivo e finito quando informado.")
    ghsv_basis = contract.ghsv_h_1 is not None and contract.bed_volume_ml is not None
    whsv_basis = contract.whsv_h_1 is not None and contract.catalyst_mass_g is not None
    if not (ghsv_basis or whsv_basis):
        errors.append("Informe GHSV+volume do leito ou WHSV+massa de catalisador.")
    if not contract.geometry:
        errors.append("A geometria do reator deve ser declarada.")
    elif any(not _positive_finite(value) for value in contract.geometry.values()):
        errors.append("As dimensões declaradas na geometria devem ser positivas e finitas.")
    return tuple(errors)


def reactor_readiness(contract: ReactorContract, kinetic: KineticContract | None, thermo_ready: bool = False) -> dict[str, object]:
    """Avalia portas sem executar EDOs nem inventar modelos ausentes."""
    errors = list(validate_reactor_contract(contract))
    if kinetic is None:
        errors.append("Nenhum contrato cinético foi selecionado.")
    else:
        kinetic_state = kinetic_readiness(kinetic)
        if not kinetic_state["valid_for_rate_calculation"]:
            errors.extend(kinetic_state["blocking_reasons"])
    if not thermo_ready:
        errors.append("As propriedades termodinâmicas ainda não foram validadas.")
    for field in ("energy_model", "pressure_drop_model", "mass_transfer_model", "wgs_model", "deactivation_model"):
        if getattr(contract, field) == "not_selected":
            errors.append(f"{field} deve ser selecionado ou justificado como não aplicável.")
    return {
        "contract_valid": not validate_reactor_contract(contract),
        "valid_for_simulation": not errors,
        "blocking_reasons": tuple(dict.fromkeys(errors)),
        "CO_conversion_pct": None,
        "physical_productivity": None,
    }


def inlet_balance(contract: ReactorContract) -> dict[str, object]:
    """Inventário de entrada; não aplica conversão, reação ou separação."""
    errors = validate_reactor_contract(contract)
    if errors:
        raise ValueError(errors)
    total = sum(contract.feed_molar_flow_mol_s.values())
    return {
        "status": "inlet_only_no_reaction",
        "species_molar_flow_mol_s": dict(contract.feed_molar_flow_mol_s),
        "total_molar_flow_mol_s": total,
        "mole_fractions": {name: flow / total for name, flow in contract.feed_molar_flow_mol_s.items()},
        "reaction_extent": None,
        "outlet_molar_flow_mol_s": None,
    }
