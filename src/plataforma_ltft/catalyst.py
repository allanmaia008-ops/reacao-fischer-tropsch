"""Contrato versionado de lotes de catalisador Fischer–Tropsch."""

from dataclasses import dataclass
from datetime import date
from math import isfinite
from typing import Any, Mapping, Sequence

CATALYST_SCHEMA_VERSION = "1.0.0"
VALID_ACTIVE_FAMILIES = ("Co", "Fe", "Co-Fe")
VALID_PHASE_STATUSES = ("medida", "inferida", "hipotetica")
VALID_SOURCE_TYPES = ("experimento_interno", "literatura", "fornecedor", "legado")


@dataclass(frozen=True)
class CatalystValidationResult:
    valid: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _finite_positive(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and isfinite(value) and value > 0


def validate_catalyst(data: Mapping[str, Any]) -> CatalystValidationResult:
    """Aplica regras científicas cruzadas além da forma validada pelo JSON Schema."""
    errors: list[str] = []
    warnings: list[str] = []

    required_text = (
        "catalyst_id", "batch_id", "display_name", "nominal_composition",
        "precursor", "support", "preparation_method",
    )
    if data.get("schema_version") != CATALYST_SCHEMA_VERSION:
        errors.append(f"schema_version deve ser {CATALYST_SCHEMA_VERSION}.")
    for field in required_text:
        if not _text(data.get(field)):
            errors.append(f"{field} deve ser uma string não vazia.")

    family = data.get("active_family")
    if family not in VALID_ACTIVE_FAMILIES:
        errors.append("active_family deve ser Co, Fe ou Co-Fe.")
    hypothesis = data.get("scientific_hypothesis")
    if family == "Co-Fe" and not _text(hypothesis):
        errors.append("Catalisador Co-Fe exige scientific_hypothesis explícita.")

    loading = data.get("active_metal_loading_wt_pct")
    if not _finite_positive(loading) or loading > 100:
        errors.append("active_metal_loading_wt_pct deve estar em (0, 100].")

    promoters = data.get("promoters")
    if not isinstance(promoters, Sequence) or isinstance(promoters, (str, bytes)):
        errors.append("promoters deve ser uma lista.")
        promoters = ()
    promoter_names: list[str] = []
    promoter_total = 0.0
    for index, promoter in enumerate(promoters):
        if not isinstance(promoter, Mapping):
            errors.append(f"promoters[{index}] deve ser um objeto.")
            continue
        name = promoter.get("name")
        promoter_loading = promoter.get("loading_wt_pct")
        if not _text(name):
            errors.append(f"promoters[{index}].name deve ser não vazio.")
        else:
            promoter_names.append(name.strip().casefold())
        if not _finite_positive(promoter_loading) or promoter_loading > 100:
            errors.append(f"promoters[{index}].loading_wt_pct deve estar em (0, 100].")
        else:
            promoter_total += float(promoter_loading)
    if len(promoter_names) != len(set(promoter_names)):
        errors.append("Promotores não podem ser duplicados no mesmo lote.")
    if _finite_positive(loading) and loading + promoter_total > 100:
        errors.append("A soma de metal ativo e promotores não pode exceder 100 % em massa.")

    preparation_steps = data.get("preparation_steps")
    if not isinstance(preparation_steps, Sequence) or isinstance(preparation_steps, (str, bytes)) or not preparation_steps:
        errors.append("preparation_steps deve conter ao menos uma etapa.")
    else:
        for index, step in enumerate(preparation_steps):
            if not isinstance(step, Mapping) or not _text(step.get("name")) or not _text(step.get("description")):
                errors.append(f"preparation_steps[{index}] exige name e description.")

    activation = data.get("activation")
    if not isinstance(activation, Mapping):
        errors.append("activation deve ser um objeto.")
    else:
        for field in ("gas", "temperature_c", "duration_h"):
            if field == "gas" and not _text(activation.get(field)):
                errors.append("activation.gas deve ser não vazio.")
            elif field != "gas" and not _finite_positive(activation.get(field)):
                errors.append(f"activation.{field} deve ser positivo e finito.")

    phase = data.get("active_phase")
    if not isinstance(phase, Mapping):
        errors.append("active_phase deve ser um objeto.")
    else:
        status = phase.get("status")
        evidence_ids = phase.get("evidence_ids")
        if not _text(phase.get("label")):
            errors.append("active_phase.label deve ser não vazio.")
        if status not in VALID_PHASE_STATUSES:
            errors.append("active_phase.status deve ser medida, inferida ou hipotetica.")
        if not isinstance(evidence_ids, Sequence) or isinstance(evidence_ids, (str, bytes)):
            errors.append("active_phase.evidence_ids deve ser uma lista.")
        elif status == "medida" and not evidence_ids:
            errors.append("Fase medida exige ao menos um evidence_id.")
        elif status != "medida" and not evidence_ids:
            warnings.append("Fase não medida sem evidência associada; permanece hipótese não verificada.")

    provenance = data.get("provenance")
    if not isinstance(provenance, Mapping):
        errors.append("provenance deve ser um objeto.")
    else:
        if provenance.get("source_type") not in VALID_SOURCE_TYPES:
            errors.append("provenance.source_type é inválido.")
        for field in ("source_reference", "license", "curator", "recorded_at"):
            if not _text(provenance.get(field)):
                errors.append(f"provenance.{field} deve ser não vazio.")
        if _text(provenance.get("recorded_at")):
            try:
                date.fromisoformat(provenance["recorded_at"])
            except ValueError:
                errors.append("provenance.recorded_at deve usar YYYY-MM-DD.")

    characterization_ids = data.get("characterization_evidence_ids")
    if not isinstance(characterization_ids, Sequence) or isinstance(characterization_ids, (str, bytes)):
        errors.append("characterization_evidence_ids deve ser uma lista.")
    if not _text(data.get("storage_conditions")):
        warnings.append("Condições de armazenamento não registradas.")

    return CatalystValidationResult(not errors, tuple(errors), tuple(warnings))

