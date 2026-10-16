"""Elemental and analytical closure for measured HTFT streams."""
from collections.abc import Mapping

ELEMENTS = ("C", "H", "O")
SPECIES = {
    "CO": {"C": 1, "O": 1}, "H2": {"H": 2}, "CO2": {"C": 1, "O": 2},
    "H2O": {"H": 2, "O": 1}, "CH4": {"C": 1, "H": 4},
}


def _atoms(stream: Mapping[str, object]) -> dict[str, float]:
    totals = {element: 0.0 for element in ELEMENTS}
    for name, amount in stream.get("species_mol_h", {}).items():
        if name not in SPECIES: raise ValueError(f"unsupported_species:{name}")
        if float(amount) < 0: raise ValueError(f"negative_flow:{name}")
        for element, count in SPECIES[name].items(): totals[element] += count * float(amount)
    for pool in ("hydrocarbon_atoms_mol_h", "oxygenate_atoms_mol_h", "unidentified_atoms_mol_h"):
        for element, amount in stream.get(pool, {}).items():
            if element not in ELEMENTS or float(amount) < 0: raise ValueError(f"invalid_{pool}:{element}")
            totals[element] += float(amount)
    coke = float(stream.get("coke_carbon_mol_h", 0))
    if coke < 0: raise ValueError("negative_coke")
    totals["C"] += coke
    return totals


def calculate_htft_balance(contract: Mapping[str, object]) -> dict:
    if contract.get("regime") != "HTFT": raise ValueError("regime_must_be_HTFT")
    incoming, outgoing = _atoms(contract["inlet"]), _atoms(contract["outlet"])
    tolerance = float(contract["closure_tolerance_pct"])
    balances = {}
    for element in ELEMENTS:
        entered = incoming[element]; left = outgoing[element]
        residual = entered - left
        error = abs(residual) / entered * 100 if entered else (0.0 if left == 0 else None)
        balances[element] = {"in_mol_atoms_h": entered, "out_mol_atoms_h": left,
                             "residual_mol_atoms_h": residual, "closure_error_pct": error,
                             "within_tolerance": error is not None and error <= tolerance}
    unidentified = sum(float(v) for v in contract["outlet"].get("unidentified_atoms_mol_h", {}).values())
    required_measured = ("CO2" in contract["outlet"].get("species_mol_h", {}) and
                         "H2O" in contract["outlet"].get("species_mol_h", {}) and
                         "coke_carbon_mol_h" in contract["outlet"])
    complete = required_measured and unidentified == 0 and all(row["within_tolerance"] for row in balances.values())
    return {"schema_version": "1.0.0", "regime": "HTFT", "balances": balances,
            "co2_water_coke_measured": required_measured, "unidentified_atoms_mol_h": unidentified,
            "status": "closed" if complete else "review_required",
            "recommendation_blocked": True}
