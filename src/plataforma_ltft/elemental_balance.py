"""Balanços molares de C/H/O com base e tolerância explícitas."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite, sqrt
from typing import Mapping, Sequence

ELEMENTAL_BALANCE_VERSION = "1.0.0"
ELEMENTS = ("C", "H", "O")
VALID_BASES = ("wet_total", "dry_gas", "hydrocarbon_only")


@dataclass(frozen=True)
class ElementalBalanceContract:
    balance_id: str
    inlet_molar_flow_mol_s: Mapping[str, float]
    outlet_molar_flow_mol_s: Mapping[str, float]
    species_atoms: Mapping[str, Mapping[str, int]]
    inlet_basis: str
    outlet_basis: str
    tolerance_pct: float
    source_ids: Sequence[str]
    inlet_molar_flow_uncertainty_mol_s: Mapping[str, float] = field(default_factory=dict)
    outlet_molar_flow_uncertainty_mol_s: Mapping[str, float] = field(default_factory=dict)
    contract_version: str = ELEMENTAL_BALANCE_VERSION


def validate_elemental_balance_contract(contract: ElementalBalanceContract) -> tuple[str, ...]:
    errors: list[str] = []
    if contract.contract_version != ELEMENTAL_BALANCE_VERSION:
        errors.append(f"contract_version deve ser {ELEMENTAL_BALANCE_VERSION}.")
    if not isinstance(contract.balance_id, str) or not contract.balance_id.strip():
        errors.append("balance_id é obrigatório.")
    if contract.inlet_basis not in VALID_BASES or contract.outlet_basis not in VALID_BASES:
        errors.append("As bases devem ser wet_total, dry_gas ou hydrocarbon_only.")
    if contract.inlet_basis != contract.outlet_basis:
        errors.append("Entrada e saída devem usar a mesma base de medição.")
    if isinstance(contract.tolerance_pct, bool) or not isinstance(contract.tolerance_pct, (int, float)) or not isfinite(contract.tolerance_pct) or contract.tolerance_pct < 0:
        errors.append("tolerance_pct deve ser finita e não negativa.")
    if not contract.source_ids:
        errors.append("source_ids deve identificar as medições ou o conjunto de demonstração.")
    elif any(not isinstance(source_id, str) or not source_id.strip() for source_id in contract.source_ids):
        errors.append("source_ids deve conter somente identificadores textuais não vazios.")

    declared_species = set(contract.inlet_molar_flow_mol_s) | set(contract.outlet_molar_flow_mol_s)
    if not declared_species:
        errors.append("Ao menos uma espécie deve ser declarada.")
    missing = sorted(declared_species - set(contract.species_atoms))
    if missing:
        errors.append("Composição elementar ausente para: " + ", ".join(missing) + ".")
    for stream_name, stream in (("inlet", contract.inlet_molar_flow_mol_s), ("outlet", contract.outlet_molar_flow_mol_s)):
        for species, flow in stream.items():
            if not isinstance(species, str) or not species.strip() or isinstance(flow, bool) or not isinstance(flow, (int, float)) or not isfinite(flow) or flow < 0:
                errors.append(f"{stream_name} contém espécie ou vazão molar inválida.")
                break
    for stream_name, uncertainties, flows in (
        ("inlet", contract.inlet_molar_flow_uncertainty_mol_s, contract.inlet_molar_flow_mol_s),
        ("outlet", contract.outlet_molar_flow_uncertainty_mol_s, contract.outlet_molar_flow_mol_s),
    ):
        unknown = sorted(set(uncertainties) - set(flows))
        if unknown:
            errors.append(f"{stream_name}: incerteza declarada para espécie ausente: " + ", ".join(unknown) + ".")
        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not isfinite(value)
            or value < 0
            for value in uncertainties.values()
        ):
            errors.append(f"{stream_name}: incertezas devem ser finitas e não negativas.")
    for species, atoms in contract.species_atoms.items():
        if not isinstance(species, str) or not species.strip() or not isinstance(atoms, Mapping):
            errors.append("species_atoms contém registro inválido.")
            break
        if any(element not in ELEMENTS for element in atoms):
            errors.append(f"{species}: somente C, H e O são aceitos em species_atoms.")
        if any(isinstance(count, bool) or not isinstance(count, int) or count < 0 for count in atoms.values()):
            errors.append(f"{species}: contagens atômicas devem ser inteiros não negativos.")
    return tuple(dict.fromkeys(errors))


def calculate_elemental_balance(contract: ElementalBalanceContract) -> dict[str, object]:
    errors = validate_elemental_balance_contract(contract)
    if errors:
        raise ValueError(errors)

    def atomic_flow(stream: Mapping[str, float], element: str) -> float:
        return sum(flow * contract.species_atoms[species].get(element, 0) for species, flow in stream.items())

    def atomic_uncertainty(uncertainties: Mapping[str, float], element: str) -> float:
        return sqrt(sum(
            (uncertainty * contract.species_atoms[species].get(element, 0)) ** 2
            for species, uncertainty in uncertainties.items()
        ))

    balances: dict[str, dict[str, object]] = {}
    for element in ELEMENTS:
        inlet = atomic_flow(contract.inlet_molar_flow_mol_s, element)
        outlet = atomic_flow(contract.outlet_molar_flow_mol_s, element)
        inlet_uncertainty = atomic_uncertainty(contract.inlet_molar_flow_uncertainty_mol_s, element)
        outlet_uncertainty = atomic_uncertainty(contract.outlet_molar_flow_uncertainty_mol_s, element)
        residual_uncertainty = sqrt(inlet_uncertainty**2 + outlet_uncertainty**2)
        if inlet == 0:
            status = "not_applicable" if outlet == 0 else "failed_zero_inlet"
            closure_pct = None
            closure_uncertainty_pct = None
            deviation_pct = None
        else:
            closure_pct = outlet / inlet * 100
            closure_uncertainty_pct = (
                closure_pct
                * sqrt((outlet_uncertainty / outlet) ** 2 + (inlet_uncertainty / inlet) ** 2)
                if outlet > 0
                else None
            )
            deviation_pct = abs(outlet - inlet) / inlet * 100
            assessable = element == "C" or contract.inlet_basis == "wet_total"
            status = "accepted" if assessable and deviation_pct <= contract.tolerance_pct else "rejected"
            if not assessable:
                status = "not_assessable_on_dry_basis"
        balances[element] = {
            "inlet_atom_mol_s": inlet,
            "inlet_atom_uncertainty_mol_s": inlet_uncertainty,
            "outlet_atom_mol_s": outlet,
            "outlet_atom_uncertainty_mol_s": outlet_uncertainty,
            "residual_atom_mol_s": inlet - outlet,
            "residual_uncertainty_mol_s": residual_uncertainty,
            "closure_pct": closure_pct,
            "closure_uncertainty_pct": closure_uncertainty_pct,
            "absolute_deviation_pct": deviation_pct,
            "tolerance_pct": contract.tolerance_pct,
            "status": status,
        }
    return {
        "contract_version": contract.contract_version,
        "balance_id": contract.balance_id,
        "flow_unit": "mol_s",
        "measurement_basis": contract.inlet_basis,
        "source_ids": tuple(contract.source_ids),
        "balances": balances,
        "all_assessable_balances_accepted": all(
            item["status"] in ("accepted", "not_applicable") for item in balances.values()
        ),
        "warning": "Fechamento elementar avalia consistência das correntes declaradas; não valida cinética nem seletividade.",
    }
