"""Compatibilidade e domínio de aplicabilidade, sem extrapolação silenciosa."""

from dataclasses import asdict
from .domain import LTFTCase, classify_ft_regime

APPLICABILITY_SCHEMA_VERSION = "1.0.0"

def assess_case_applicability(case: LTFTCase, *, evidence_approved: bool = False) -> dict:
    reasons = []
    alerts = []
    if case.temperature_c is None:
        alerts.append("temperature_c ausente; envelope térmico não avaliado")
    else:
        try:
            regime = classify_ft_regime(case.temperature_c)
            if regime != "LTFT":
                alerts.append(f"caso classificado como {regime}; domínio LTFT não se aplica")
        except ValueError as exc:
            alerts.append(str(exc))
    if case.active_family not in ("Co", "Co-Fe"):
        alerts.append("família ativa fora do domínio contextual Co/Co-Fe do corpus LTFT atual")
    if case.pressure_bar is not None and not 1.0 <= case.pressure_bar <= 40.0:
        alerts.append("pressão fora da faixa contextual 1–40 bar; requer evidência específica")
    if case.h2_co_molar_ratio is not None and not 0.5 <= case.h2_co_molar_ratio <= 3.0:
        alerts.append("razão H2/CO fora da faixa contextual 0,5–3,0")
    if not evidence_approved:
        reasons.append("corpus LTFT ainda não aprovado pela FT-021")
    if alerts:
        reasons.extend(alerts)
    return {"schema_version": APPLICABILITY_SCHEMA_VERSION, "status": "blocked" if reasons else "contextual_only", "case": asdict(case), "alerts": alerts, "reasons": reasons, "recommendation_blocked": True}

def assess_case_compatibility(case: LTFTCase, *, evidence_approved: bool = False) -> dict:
    result = assess_case_applicability(case, evidence_approved=evidence_approved)
    result["compatibility"] = "compatible_contextually" if result["status"] == "contextual_only" else "not_demonstrated"
    result["justification"] = "Compatibilidade contextual não equivale a transferência quantitativa."
    return result
