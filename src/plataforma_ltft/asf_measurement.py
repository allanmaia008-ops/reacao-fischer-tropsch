"""Comparação rastreável entre ASF e distribuições medidas de hidrocarbonetos."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite, sqrt
from typing import Mapping, Sequence

from .asf import carbon_fraction, product_bands, validate_alpha

ASF_MEASUREMENT_VERSION = "1.0.0"
MEASUREMENT_BASIS = "carbon_fraction_hydrocarbons"
EVIDENCE_STATUSES = ("synthetic", "extracted", "verified", "approved")
BAND_LABELS = ("CH4", "C2-C4", "C5-C11", "C12-C20", "C21+")


@dataclass(frozen=True)
class ASFMeasurementContract:
    comparison_id: str
    alpha: float
    representation: str
    measured_fractions: Mapping[str, float]
    measurement_basis: str
    evidence_status: str
    source_ids: Sequence[str]
    measured_uncertainty: Mapping[str, float] = field(default_factory=dict)
    closure_tolerance_pct: float = 2.0
    contract_version: str = ASF_MEASUREMENT_VERSION


def _carbon_number(label: str) -> int | None:
    if not isinstance(label, str) or not label.startswith("C") or not label[1:].isdigit():
        return None
    value = int(label[1:])
    return value if 1 <= value <= 60 else None


def validate_asf_measurement_contract(contract: ASFMeasurementContract) -> tuple[str, ...]:
    errors: list[str] = []
    if contract.contract_version != ASF_MEASUREMENT_VERSION:
        errors.append(f"contract_version deve ser {ASF_MEASUREMENT_VERSION}.")
    if not isinstance(contract.comparison_id, str) or not contract.comparison_id.strip():
        errors.append("comparison_id é obrigatório.")
    try:
        validate_alpha(contract.alpha)
    except (TypeError, ValueError) as exc:
        errors.append(str(exc) + ".")
    if contract.representation not in ("carbon_number", "product_bands"):
        errors.append("representation deve ser carbon_number ou product_bands.")
    if contract.measurement_basis != MEASUREMENT_BASIS:
        errors.append(f"measurement_basis deve ser {MEASUREMENT_BASIS}.")
    if contract.evidence_status not in EVIDENCE_STATUSES:
        errors.append("evidence_status inválido.")
    if not contract.source_ids or any(not isinstance(item, str) or not item.strip() for item in contract.source_ids):
        errors.append("source_ids deve conter identificadores textuais não vazios.")
    if not contract.measured_fractions:
        errors.append("measured_fractions deve conter ao menos uma medição.")

    labels = set(contract.measured_fractions)
    if contract.representation == "carbon_number":
        invalid_labels = sorted(label for label in labels if _carbon_number(label) is None)
    else:
        invalid_labels = sorted(labels - set(BAND_LABELS))
    if invalid_labels:
        errors.append("Rótulos incompatíveis com representation: " + ", ".join(invalid_labels) + ".")

    for label, value in contract.measured_fractions.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value < 0 or value > 1:
            errors.append(f"{label}: fração medida deve ser finita entre 0 e 1.")
    unknown_uncertainty = sorted(set(contract.measured_uncertainty) - labels)
    if unknown_uncertainty:
        errors.append("Incerteza sem medição correspondente: " + ", ".join(unknown_uncertainty) + ".")
    for label, value in contract.measured_uncertainty.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value < 0:
            errors.append(f"{label}: incerteza deve ser finita e não negativa.")
    if (
        isinstance(contract.closure_tolerance_pct, bool)
        or not isinstance(contract.closure_tolerance_pct, (int, float))
        or not isfinite(contract.closure_tolerance_pct)
        or contract.closure_tolerance_pct < 0
    ):
        errors.append("closure_tolerance_pct deve ser finita e não negativa.")
    return tuple(dict.fromkeys(errors))


def compare_asf_to_measurement(contract: ASFMeasurementContract) -> dict[str, object]:
    errors = validate_asf_measurement_contract(contract)
    if errors:
        raise ValueError(errors)

    predictions = product_bands(contract.alpha) if contract.representation == "product_bands" else {
        label: carbon_fraction(contract.alpha, _carbon_number(label))
        for label in contract.measured_fractions
    }
    rows = []
    squared = []
    absolute = []
    chi_square_terms = []
    for label in sorted(contract.measured_fractions, key=lambda item: (_carbon_number(item) or 999, item)):
        measured = contract.measured_fractions[label]
        predicted = predictions[label]
        residual = measured - predicted
        uncertainty = contract.measured_uncertainty.get(label)
        standardized = residual / uncertainty if uncertainty and uncertainty > 0 else None
        rows.append({
            "label": label,
            "measured_fraction": measured,
            "asf_fraction": predicted,
            "residual_measured_minus_asf": residual,
            "absolute_residual": abs(residual),
            "measured_uncertainty": uncertainty,
            "standardized_residual": standardized,
        })
        squared.append(residual**2)
        absolute.append(abs(residual))
        if standardized is not None:
            chi_square_terms.append(standardized**2)

    measured_total = sum(contract.measured_fractions.values())
    closure_deviation_pct = abs(measured_total - 1.0) * 100
    complete_distribution = (
        contract.representation == "product_bands" and set(contract.measured_fractions) == set(BAND_LABELS)
    )
    closure_status = (
        "accepted" if complete_distribution and closure_deviation_pct <= contract.closure_tolerance_pct
        else "rejected" if complete_distribution
        else "not_assessable_partial_distribution"
    )
    approved = contract.evidence_status == "approved"
    return {
        "contract_version": contract.contract_version,
        "comparison_id": contract.comparison_id,
        "alpha": float(contract.alpha),
        "measurement_basis": contract.measurement_basis,
        "representation": contract.representation,
        "evidence_status": contract.evidence_status,
        "source_ids": tuple(contract.source_ids),
        "comparison": rows,
        "metrics": {
            "point_count": len(rows),
            "mae": sum(absolute) / len(absolute),
            "rmse": sqrt(sum(squared) / len(squared)),
            "chi_square": sum(chi_square_terms) if chi_square_terms else None,
            "chi_square_point_count": len(chi_square_terms),
            "measured_fraction_sum": measured_total,
            "closure_deviation_pct": closure_deviation_pct,
            "closure_status": closure_status,
        },
        "diagnostics": {
            "C1_residual": next((row["residual_measured_minus_asf"] for row in rows if row["label"] == "CH4" or row["label"] == "C1"), None),
            "C2_residual": next((row["residual_measured_minus_asf"] for row in rows if row["label"] == "C2"), None),
            "tail_residual": next((row["residual_measured_minus_asf"] for row in rows if row["label"] == "C21+"), None),
        },
        "allowed_for_model_validation": approved and closure_status != "rejected",
        "recommendation_blocked": True,
        "warnings": [
            "Resíduos quantificam aderência à ASF; não demonstram causalidade, cinética ou transferibilidade.",
            *([] if approved else ["A evidência não está aprovada; o resultado é apenas diagnóstico."]),
        ],
    }
