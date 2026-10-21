"""Conservative VASP OUTCAR parser (FT-039).

Parsing an output file is not a scientific validation or a new DFT run. The
parser reports only signals explicitly present in the file and keeps
scientific recommendations blocked.
"""
from __future__ import annotations

from hashlib import sha256
from math import sqrt
from pathlib import Path
import re
from typing import Any

PARSER_VERSION = "1.0.0"
_FLOAT = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][-+]?\d+)?"
_TOTEN = re.compile(rf"free\s+energy\s+TOTEN\s*=\s*({_FLOAT})", re.IGNORECASE)
_NIONS = re.compile(r"\bNIONS\s*=\s*(\d+)", re.IGNORECASE)
_ERROR_PATTERNS = (
    re.compile(r"\bVERY BAD NEWS\b", re.IGNORECASE),
    re.compile(r"\bBRMIX:\s*very serious problems\b", re.IGNORECASE),
    re.compile(r"\bZBRENT:\s*fatal error\b", re.IGNORECASE),
    re.compile(r"\bEDDDAV:.*(?:error|not converg)", re.IGNORECASE),
    re.compile(r"\bsegmentation fault\b", re.IGNORECASE),
    re.compile(r"\bERROR\s*[:!]", re.IGNORECASE),
)


def _number(value: str) -> float:
    return float(value.replace("D", "E").replace("d", "e"))


def _force_block_metrics(lines: list[str]) -> list[tuple[float, int]]:
    metrics: list[tuple[float, int]] = []
    i = 0
    while i < len(lines):
        if "TOTAL-FORCE" not in lines[i] or "POSITION" not in lines[i]:
            i += 1
            continue
        i += 1
        numeric_rows: list[list[float]] = []
        while i < len(lines):
            try:
                numbers = [_number(token) for token in lines[i].split()]
            except ValueError:
                numbers = []
            if len(numbers) >= 6:
                numeric_rows.append(numbers[-6:])
            elif numeric_rows:
                break
            i += 1
        if numeric_rows:
            maximum = max(sqrt(row[3] ** 2 + row[4] ** 2 + row[5] ** 2) for row in numeric_rows)
            metrics.append((maximum, len(numeric_rows)))
        i += 1
    return metrics


def parse_vasp_outcar(
    text: str,
    *,
    source_name: str = "OUTCAR",
    force_threshold_ev_angstrom: float | None = None,
    expected_atom_count: int | None = None,
    synthetic: bool = False,
) -> dict[str, Any]:
    """Parse explicit convergence and energy signals; do not infer success from file presence."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("OUTCAR text must be a non-empty string")
    if force_threshold_ev_angstrom is not None and force_threshold_ev_angstrom <= 0:
        raise ValueError("force threshold must be positive")
    if expected_atom_count is not None and expected_atom_count <= 0:
        raise ValueError("expected atom count must be positive")

    lines = text.splitlines()
    energies = [_number(match.group(1)) for line in lines if (match := _TOTEN.search(line))]
    nions_match = next((match for line in lines if (match := _NIONS.search(line))), None)
    reported_nions = int(nions_match.group(1)) if nions_match else None
    count_to_check = expected_atom_count if expected_atom_count is not None else reported_nions
    force_blocks = _force_block_metrics(lines)
    force_maxima = [metric[0] for metric in force_blocks]
    final_force_count = force_blocks[-1][1] if force_blocks else None
    atom_count_matches = (
        final_force_count == count_to_check
        and (expected_atom_count is None or reported_nions is None or expected_atom_count == reported_nions)
        if count_to_check is not None and final_force_count is not None
        else None
    )
    normal_termination = any(
        "General timing and accounting informations for this job" in line for line in lines
    )
    electronic_markers = sum(
        "aborting loop because EDIFF is reached" in line for line in lines
    )
    explicit_unconverged = any(
        "EDIFF was not reached" in line or "electronic self-consistency was not achieved" in line.lower()
        for line in lines
    )
    if explicit_unconverged:
        scf_converged: bool | None = False
    elif force_maxima and electronic_markers >= len(force_maxima):
        scf_converged = True
    elif electronic_markers:
        scf_converged = False
    else:
        scf_converged = None

    ionic_marker = any(
        "reached required accuracy - stopping structural energy minimisation" in line.lower()
        for line in lines
    )
    final_force = force_maxima[-1] if force_maxima else None
    # VASP's ionic stopping message reports the optimizer's termination
    # condition; it is not itself proof that the final force meets our
    # independently declared acceptance threshold.
    if final_force is not None and force_threshold_ev_angstrom is not None:
        ionic_converged = final_force <= force_threshold_ev_angstrom
    else:
        ionic_converged = None

    errors = [line.strip() for line in lines if any(pattern.search(line) for pattern in _ERROR_PATTERNS)]
    if errors:
        status = "failed"
    elif synthetic:
        status = "synthetic_test"
    elif atom_count_matches is not True:
        status = "incomplete"
    elif not normal_termination:
        status = "incomplete"
    elif scf_converged is False or ionic_converged is False:
        status = "unconverged"
    elif scf_converged is True and ionic_converged is True and energies:
        status = "succeeded"
    else:
        status = "incomplete"

    return {
        "schema_version": "1.0.0",
        "parser_version": PARSER_VERSION,
        "engine": "vasp",
        "source": {
            "name": Path(source_name).name,
            "sha256": sha256(text.encode("utf-8")).hexdigest(),
        },
        "status": status,
        "normal_termination": normal_termination,
        "error_messages": errors,
        "total_energy_ev": energies[-1] if energies else None,
        "ionic_steps_with_forces": len(force_maxima),
        "final_force_count": final_force_count,
        "reported_nions": reported_nions,
        "expected_atom_count": count_to_check,
        "force_count_matches_expected": atom_count_matches,
        "final_max_force_ev_angstrom": final_force,
        "force_threshold_ev_angstrom": force_threshold_ev_angstrom,
        "ionic_stop_marker_present": ionic_marker,
        "electronic_converged": scf_converged,
        "ionic_converged": ionic_converged,
        "recommendation_blocked": True,
        "interpretation": "parsed_output_only_not_independent_scientific_validation",
    }


def parse_vasp_outcar_file(
    path: str | Path,
    *,
    force_threshold_ev_angstrom: float | None = None,
    expected_atom_count: int | None = None,
    synthetic: bool = False,
) -> dict[str, Any]:
    source = Path(path)
    return parse_vasp_outcar(
        source.read_text(encoding="utf-8", errors="replace"),
        source_name=source.name,
        force_threshold_ev_angstrom=force_threshold_ev_angstrom,
        expected_atom_count=expected_atom_count,
        synthetic=synthetic,
    )
