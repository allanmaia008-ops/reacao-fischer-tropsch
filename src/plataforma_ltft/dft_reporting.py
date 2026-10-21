"""Reproducible, explicitly non-prescriptive DFT report assembly (FT-040)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

REPORT_VERSION = "1.0.0"
DEFAULT_LIMITATIONS = [
    "A parsed DFT output is not experimental evidence or an experimental recommendation.",
    "A successful parser state does not replace independent scientific review.",
    "No uncertainty is inferred when the calculation protocol does not provide one.",
    "Synthetic inputs or outputs must remain labelled synthetic and cannot support scientific claims.",
]


def build_dft_report(
    parsed_result: Mapping[str, Any],
    *,
    report_id: str,
    structure_contract: Mapping[str, Any],
    surface_protocol: Mapping[str, Any],
    input_manifest: Mapping[str, Any],
    source_citation: str,
) -> dict[str, Any]:
    """Assemble an auditable report from contracts and parser output only."""
    if not report_id.strip():
        raise ValueError("report_id must not be empty")
    if not source_citation.strip():
        raise ValueError("source_citation must not be empty")
    if parsed_result.get("recommendation_blocked") is not True:
        raise ValueError("parsed result must retain recommendation_blocked=true")
    if input_manifest.get("recommendation_blocked") is not True:
        raise ValueError("input manifest must retain recommendation_blocked=true")

    method = surface_protocol.get("electronic_method")
    if not isinstance(method, Mapping):
        raise ValueError("surface protocol has no electronic_method object")
    provenance = structure_contract.get("provenance")
    if not isinstance(provenance, Mapping):
        provenance = {}
    synthetic = (
        parsed_result.get("status") == "synthetic_test"
        or input_manifest.get("execution_status") == "synthetic_test"
        or structure_contract.get("scientific_status") == "synthetic_test"
    )

    return {
        "schema_version": REPORT_VERSION,
        "report_id": report_id,
        "report_type": "dft_run_audit",
        "execution_status": parsed_result.get("status"),
        "synthetic": synthetic,
        "source_citation": source_citation.strip(),
        "structure": {
            "structure_id": structure_contract.get("structure_id"),
            "scientific_status": structure_contract.get("scientific_status"),
            "provenance": dict(provenance),
        },
        "protocol": {
            "protocol_id": surface_protocol.get("protocol_id"),
            "protocol_version": surface_protocol.get("schema_version"),
            "method": dict(method),
            "convergence": surface_protocol.get("convergence"),
            "surface": {
                "miller_index": surface_protocol.get("miller_index"),
                "termination_id": surface_protocol.get("termination_id"),
                "slab": surface_protocol.get("slab"),
                "coverage": surface_protocol.get("coverage"),
            },
        },
        "input_manifest": {
            "input_set_id": input_manifest.get("input_set_id"),
            "adapter_version": input_manifest.get("adapter_version"),
            "method_fingerprint_sha256": input_manifest.get("method_fingerprint_sha256"),
            "source_fingerprint_sha256": (
                input_manifest.get("source") or {}
            ).get("contract_fingerprint_sha256")
            if isinstance(input_manifest.get("source"), Mapping)
            else None,
            "files": input_manifest.get("files"),
            "required_external_files": input_manifest.get("required_external_files"),
        },
        "parsed_result": {
            "parser_version": parsed_result.get("parser_version"),
            "source": parsed_result.get("source"),
            "normal_termination": parsed_result.get("normal_termination"),
            "error_messages": parsed_result.get("error_messages"),
            "total_energy_ev": parsed_result.get("total_energy_ev"),
            "ionic_steps_with_forces": parsed_result.get("ionic_steps_with_forces"),
            "final_force_count": parsed_result.get("final_force_count"),
            "reported_nions": parsed_result.get("reported_nions"),
            "expected_atom_count": parsed_result.get("expected_atom_count"),
            "force_count_matches_expected": parsed_result.get("force_count_matches_expected"),
            "final_max_force_ev_angstrom": parsed_result.get("final_max_force_ev_angstrom"),
            "electronic_converged": parsed_result.get("electronic_converged"),
            "ionic_converged": parsed_result.get("ionic_converged"),
        },
        "limitations": list(DEFAULT_LIMITATIONS),
        "independent_review_required": True,
        "recommendation_blocked": True,
    }


def render_dft_report_markdown(report: Mapping[str, Any]) -> str:
    """Render a concise Markdown audit, retaining explicit provenance and limits."""
    parsed = report.get("parsed_result")
    protocol = report.get("protocol")
    structure = report.get("structure")
    if not all(isinstance(x, Mapping) for x in (parsed, protocol, structure)):
        raise ValueError("report is missing structured sections")
    source = parsed.get("source") or {}
    method = protocol.get("method") or {}
    convergence = protocol.get("convergence") or {}
    limitations = report.get("limitations") or []
    rows = [
        f"# DFT run audit: {report.get('report_id', 'unassigned')}",
        "",
        f"- Execution/parser status: **{report.get('execution_status', 'unknown')}**",
        f"- Synthetic record: **{'yes' if report.get('synthetic') else 'no'}**",
        f"- Structure: {structure.get('structure_id', 'unknown')}",
        f"- Source citation: {report.get('source_citation', 'not supplied')}",
        f"- Parsed output: {source.get('name', 'unknown')}; SHA-256 {source.get('sha256', 'unknown')}",
        f"- Energy: {parsed.get('total_energy_ev') if parsed.get('total_energy_ev') is not None else 'not reported'} eV",
        f"- Electronic convergence: {parsed.get('electronic_converged')}",
        f"- Ionic convergence: {parsed.get('ionic_converged')}",
        f"- Force rows / expected atoms: {parsed.get('final_force_count')} / {parsed.get('expected_atom_count')}",
        f"- Final maximum force: {parsed.get('final_max_force_ev_angstrom')} eV/Å",
        "",
        "## Method",
        "",
        f"Engine: {method.get('engine', 'not assigned')}; functional: {method.get('functional', 'not assigned')}; "
        f"pseudopotential family: {method.get('pseudopotential_family', 'not assigned')}; "
        f"cutoff: {method.get('cutoff_ev', 'not assigned')} eV.",
        f"Protocol: {protocol.get('protocol_id', 'unassigned')}; convergence criteria: "
        f"{json.dumps(convergence, ensure_ascii=False, sort_keys=True)}.",
        "",
        "## Interpretation and limits",
        "",
        "This document audits parser output and declared inputs. It does not establish experimental performance, "
        "intrinsic kinetics, catalyst suitability, or a recommended operating condition.",
        "Recommendation status: **BLOCKED**. Independent scientific review is required.",
        "",
    ]
    rows.extend(f"- {item}" for item in limitations)
    return "\n".join(rows) + "\n"


def write_dft_report(report: Mapping[str, Any], destination_prefix: str | Path) -> tuple[Path, Path]:
    """Write JSON and Markdown report files without overwriting existing files."""
    prefix = Path(destination_prefix)
    targets = (prefix.with_suffix(".json"), prefix.with_suffix(".md"))
    existing = [str(path) for path in targets if path.exists()]
    if existing:
        raise FileExistsError("refusing to overwrite DFT report: " + ", ".join(existing))
    prefix.parent.mkdir(parents=True, exist_ok=True)
    targets[0].write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    targets[1].write_text(render_dft_report_markdown(report), encoding="utf-8", newline="\n")
    return targets
