"""Resumo auditável de um caso experimental, sem tratá-lo como evidência."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict

from .domain import LTFTCase, validate_case

EXPERIMENTAL_CASE_SUMMARY_VERSION = "1.0.0"

FIELD_GROUPS = {
    "catalyst_and_activation": (
        "composition", "active_family", "active_phase_hypothesis", "support",
        "active_metal_loading_wt_pct", "promoter", "promoter_loading_wt_pct",
        "precursor", "activation_gas", "activation_temperature_c",
        "activation_duration_h",
    ),
    "reactor": (
        "reactor_type", "bed_inlet_temperature_c", "bed_outlet_temperature_c",
        "ghsv_h_1", "whsv_h_1", "catalyst_mass_g", "bed_volume_ml",
    ),
    "feed": ("feed_composition_mol_fraction", "feed_flow_mol_s", "h2_co_molar_ratio"),
    "operating_conditions": (
        "temperature_c", "pressure_bar", "time_on_stream_h", "analytical_method",
        "replicate_count", "steady_state_criterion",
    ),
    "scientific_scope": ("desired_product", "ft_regime", "regime_envelope_version", "regime_justification"),
}


def experimental_case_summary(case: LTFTCase) -> dict[str, object]:
    """Organiza entradas declaradas e prontidão; não calcula desempenho."""
    validation = validate_case(case)
    payload = asdict(case)
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {
        "summary_version": EXPERIMENTAL_CASE_SUMMARY_VERSION,
        "case_fingerprint_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "record_status": "planned_case_not_experimental_evidence",
        "groups": {
            group: {field: payload[field] for field in fields}
            for group, fields in FIELD_GROUPS.items()
        },
        "readiness": {
            "valid_for_screening": validation.valid_for_screening,
            "valid_for_experimental_plan": validation.valid_for_experimental_plan,
            "valid_for_rate_calculation": validation.valid_for_rate_calculation,
            "missing_experimental_fields": validation.missing_experimental_fields,
            "errors": validation.errors,
        },
        "outputs": {
            "CO_conversion_pct": None,
            "physical_productivity": None,
            "measured_selectivity": None,
        },
        "warning": (
            "Caso planejado e reprodutível; não constitui dado medido, condição ótima "
            "ou liberação para execução sem revisão humana e de segurança."
        ),
    }
