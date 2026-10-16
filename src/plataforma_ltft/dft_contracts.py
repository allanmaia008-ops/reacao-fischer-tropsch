"""Audit gates for structures, surface models and adsorption energies."""
from __future__ import annotations

from collections.abc import Mapping, Sequence

DFT_CONTRACT_VERSION = "1.0.0"


def _sha256(value: object) -> bool:
    text = str(value or "")
    return len(text) == 64 and all(char in "0123456789abcdef" for char in text.lower())


def validate_structure_contract(contract: Mapping[str, object]) -> tuple[str, ...]:
    issues: list[str] = []
    for field in ("structure_id", "role", "chemical_formula", "structure_file", "provenance"):
        if not contract.get(field): issues.append(f"missing:{field}")
    file_record = contract.get("structure_file", {})
    if not isinstance(file_record, Mapping) or not _sha256(file_record.get("sha256")): issues.append("invalid:structure_file.sha256")
    provenance = contract.get("provenance", {})
    if not isinstance(provenance, Mapping) or not provenance.get("source_type"): issues.append("missing:provenance.source_type")
    if not isinstance(provenance, Mapping) or not provenance.get("citation_or_uri"): issues.append("missing:provenance.citation_or_uri")
    lattice = contract.get("lattice_angstrom", [])
    if not isinstance(lattice, Sequence) or len(lattice) != 3 or any(not isinstance(row, Sequence) or len(row) != 3 for row in lattice): issues.append("invalid:lattice_angstrom")
    return tuple(issues)


def validate_surface_protocol(protocol: Mapping[str, object]) -> tuple[str, ...]:
    issues: list[str] = []
    if len(protocol.get("miller_index", [])) != 3: issues.append("invalid:miller_index")
    for field in ("bulk_structure_id", "termination_id", "slab", "coverage", "convergence"):
        if not protocol.get(field): issues.append(f"missing:{field}")
    slab = protocol.get("slab", {})
    if not isinstance(slab, Mapping) or float(slab.get("vacuum_angstrom", 0) or 0) <= 0: issues.append("invalid:slab.vacuum_angstrom")
    if not isinstance(slab, Mapping) or int(slab.get("layers", 0) or 0) < 1: issues.append("invalid:slab.layers")
    return tuple(issues)


def calculate_adsorption_energy(contract: Mapping[str, object]) -> dict[str, object]:
    """Calculate E_ads only for three converged, method-comparable energies."""
    reasons: list[str] = []
    energies = contract.get("energies", [])
    if not isinstance(energies, Sequence) or isinstance(energies, (str, bytes)): energies = []
    records = {item.get("role"): item for item in energies if isinstance(item, Mapping)}
    expected = {"clean_surface", "isolated_adsorbate", "adsorbed_system"}
    if len(energies) != 3 or set(records) != expected: reasons.append("exactly_three_energy_roles_required")
    fingerprints = {str(item.get("method_fingerprint", "")) for item in records.values()}
    if len(fingerprints) != 1 or "" in fingerprints: reasons.append("incomparable_method_fingerprints")
    if any(item.get("converged") is not True for item in records.values()): reasons.append("unconverged_energy")
    if any(item.get("energy_ev") is None for item in records.values()): reasons.append("energy_missing")
    multiplicity = int(contract.get("adsorbate_count", 0) or 0)
    if multiplicity < 1: reasons.append("invalid_adsorbate_count")
    if reasons:
        return {"schema_version": DFT_CONTRACT_VERSION, "status": "blocked", "reasons": reasons,
                "adsorption_energy_ev": None, "recommendation_blocked": True}
    value = (float(records["adsorbed_system"]["energy_ev"])
             - float(records["clean_surface"]["energy_ev"])
             - multiplicity * float(records["isolated_adsorbate"]["energy_ev"]))
    return {"schema_version": DFT_CONTRACT_VERSION, "status": "calculated", "reasons": [],
            "adsorption_energy_ev": value, "sign_convention": "negative_is_exothermic",
            "recommendation_blocked": True}
