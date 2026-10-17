"""Versioned DFT-engine input adapters (FT-038).

The adapter only prepares auditable input files.  It does not execute VASP and
does not turn a planned or synthetic structure into scientific evidence.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha256
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from .dft_contracts import validate_structure_contract, validate_surface_protocol

ENGINE_INPUT_SCHEMA_VERSION = "1.0.0"
ADAPTER_VERSION = "1.0.0"


class EngineInputError(ValueError):
    """Raised when an engine input cannot be generated safely."""


def _digest(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def _canonical_fingerprint(values: Mapping[str, object]) -> str:
    import json

    payload = json.dumps(values, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return _digest(payload)


def _pymatgen_version() -> str:
    try:
        return version("pymatgen")
    except PackageNotFoundError as exc:  # pragma: no cover - depends on deployment
        raise EngineInputError(
            "pymatgen is required for the VASP adapter; install the 'dft' extra"
        ) from exc


@dataclass(frozen=True)
class EngineInputBundle:
    """In-memory files and audit manifest produced by an engine adapter."""

    files: Mapping[str, str]
    manifest: Mapping[str, object]

    def write(self, destination: Path) -> tuple[Path, ...]:
        """Write a new bundle without overwriting pre-existing files."""
        destination = Path(destination)
        destination.mkdir(parents=True, exist_ok=True)
        targets = [destination / name for name in (*self.files.keys(), "manifest.json")]
        existing = [path.name for path in targets if path.exists()]
        if existing:
            raise FileExistsError(f"refusing to overwrite engine inputs: {', '.join(existing)}")

        import json

        written: list[Path] = []
        for name, content in self.files.items():
            path = destination / name
            path.write_text(content, encoding="utf-8", newline="\n")
            written.append(path)
        manifest_path = destination / "manifest.json"
        manifest_path.write_text(
            json.dumps(self.manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        written.append(manifest_path)
        return tuple(written)


def build_vasp_input(
    structure_contract: Mapping[str, object],
    surface_protocol: Mapping[str, object],
    *,
    input_set_id: str,
) -> EngineInputBundle:
    """Create a deterministic VASP input bundle through pymatgen.

    POTCAR is deliberately not generated: its licensed content and the exact
    potential files must be supplied and checked by the executing institution.
    """
    structure_issues = validate_structure_contract(structure_contract)
    surface_issues = validate_surface_protocol(surface_protocol)
    if structure_issues or surface_issues:
        issues = (*structure_issues, *surface_issues)
        raise EngineInputError("invalid DFT contract: " + ", ".join(issues))
    if not input_set_id.strip():
        raise EngineInputError("input_set_id must not be empty")

    method = surface_protocol.get("electronic_method")
    if not isinstance(method, Mapping):
        raise EngineInputError("missing electronic_method")
    engine = str(method.get("engine", "")).strip().lower()
    if engine != "vasp":
        raise EngineInputError(f"unsupported engine for this adapter: {engine or 'missing'}")
    for key in ("functional", "pseudopotential_family"):
        if str(method.get(key, "")).strip().lower() in {"", "unassigned"}:
            raise EngineInputError(f"electronic_method.{key} must be assigned")

    try:
        from pymatgen.core import Lattice, Structure
        from pymatgen.io.vasp.inputs import Incar, Kpoints, Poscar
    except ImportError as exc:  # pragma: no cover - depends on deployment
        raise EngineInputError(
            "pymatgen is required for the VASP adapter; install the 'dft' extra"
        ) from exc

    lattice = Lattice(structure_contract["lattice_angstrom"])
    sites = structure_contract["sites"]
    species = [site["element"] for site in sites]
    coordinates = [site["fractional_coordinates"] for site in sites]
    structure = Structure(lattice, species, coordinates, coords_are_cartesian=False)

    convergence = surface_protocol["convergence"]
    incar_values: dict[str, Any] = {
        "SYSTEM": input_set_id,
        "ENCUT": float(method["cutoff_ev"]),
        "EDIFF": float(convergence["energy_ev"]),
        "EDIFFG": -float(convergence["force_ev_angstrom"]),
        "IBRION": 2,
        "ISIF": 2,
        "ISPIN": 2 if method["spin_polarized"] else 1,
        "LCHARG": False,
        "LWAVE": False,
        "NSW": 200,
        "PREC": "Accurate",
    }
    functional = str(method["functional"]).strip().upper()
    if functional == "PBE":
        incar_values["GGA"] = "PE"
    else:
        raise EngineInputError(f"unsupported VASP functional mapping: {functional}")
    dispersion = str(method.get("dispersion") or "").strip().upper()
    if dispersion:
        ivdw = {"D3": 11, "D3(BJ)": 12, "D3BJ": 12}.get(dispersion)
        if ivdw is None:
            raise EngineInputError(f"unsupported VASP dispersion mapping: {dispersion}")
        incar_values["IVDW"] = ivdw

    files = {
        "INCAR": str(Incar(incar_values)),
        "KPOINTS": str(Kpoints.gamma_automatic(tuple(method["k_mesh"]))),
        "POSCAR": Poscar(structure, comment=input_set_id).get_str(),
    }
    files = {name: content if content.endswith("\n") else content + "\n" for name, content in files.items()}
    source_fingerprint = _canonical_fingerprint(
        {"structure": structure_contract, "surface_protocol": surface_protocol}
    )
    method_fingerprint = _canonical_fingerprint(dict(method))
    manifest: dict[str, object] = {
        "schema_version": ENGINE_INPUT_SCHEMA_VERSION,
        "adapter_version": ADAPTER_VERSION,
        "input_set_id": input_set_id,
        "engine": "vasp",
        "generator": {"name": "pymatgen", "version": _pymatgen_version()},
        "source": {
            "structure_id": structure_contract["structure_id"],
            "surface_protocol_id": surface_protocol["protocol_id"],
            "contract_fingerprint_sha256": source_fingerprint,
        },
        "method_fingerprint_sha256": method_fingerprint,
        "files": [
            {"path": name, "sha256": _digest(content), "role": name.lower()}
            for name, content in sorted(files.items())
        ],
        "required_external_files": [
            {
                "path": "POTCAR",
                "reason": "licensed pseudopotential file; verify family and hashes at execution",
                "status": "missing",
            }
        ],
        "execution_status": "synthetic_test"
        if structure_contract.get("scientific_status") == "synthetic_test"
        else "planned",
        "recommendation_blocked": True,
    }
    return EngineInputBundle(files=files, manifest=manifest)


def validate_engine_input_manifest(manifest: Mapping[str, object]) -> tuple[str, ...]:
    """Perform cross-field checks beyond the JSON Schema."""
    issues: list[str] = []
    if manifest.get("schema_version") != ENGINE_INPUT_SCHEMA_VERSION:
        issues.append("invalid:schema_version")
    if manifest.get("adapter_version") != ADAPTER_VERSION:
        issues.append("invalid:adapter_version")
    if manifest.get("engine") != "vasp":
        issues.append("invalid:engine")
    files = manifest.get("files")
    if not isinstance(files, list) or {item.get("path") for item in files if isinstance(item, Mapping)} != {"INCAR", "KPOINTS", "POSCAR"}:
        issues.append("invalid:files")
    if manifest.get("recommendation_blocked") is not True:
        issues.append("invalid:recommendation_blocked")
    external = manifest.get("required_external_files")
    if not isinstance(external, list) or not any(
        isinstance(item, Mapping) and item.get("path") == "POTCAR" and item.get("status") == "missing"
        for item in external
    ):
        issues.append("missing:required_external_files.POTCAR")
    return tuple(issues)
