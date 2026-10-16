"""Scientific gate for quantitative HTFT validation."""
from __future__ import annotations

from collections.abc import Mapping

HTFT_VALIDATION_VERSION = "1.0.0"


def assess_htft_validation(contract: Mapping[str, object]) -> dict[str, object]:
    """Evaluate external-data and independent-review prerequisites."""
    reasons: list[str] = []
    if contract.get("regime") != "HTFT": reasons.append("regime_must_be_HTFT")
    model = contract.get("model", {})
    if not isinstance(model, Mapping) or not model.get("model_id"): reasons.append("model_identifier_missing")
    if not isinstance(model, Mapping) or not model.get("version"): reasons.append("model_version_missing")
    if not isinstance(model, Mapping) or model.get("frozen") is not True: reasons.append("model_not_frozen")
    dataset = contract.get("external_dataset", {})
    if not isinstance(dataset, Mapping) or not dataset.get("dataset_id"): reasons.append("external_dataset_missing")
    if not isinstance(dataset, Mapping) or dataset.get("independent_from_calibration") is not True: reasons.append("dataset_not_independent_from_calibration")
    if not isinstance(dataset, Mapping) or dataset.get("compatibility_review") != "accepted": reasons.append("dataset_compatibility_not_accepted")
    if not isinstance(dataset, Mapping) or int(dataset.get("row_count", 0) or 0) < 1: reasons.append("external_dataset_empty")
    evaluation = contract.get("evaluation", {})
    if not isinstance(evaluation, Mapping) or not evaluation.get("metrics"): reasons.append("validation_metrics_missing")
    if not isinstance(evaluation, Mapping) or not evaluation.get("uncertainty_method"): reasons.append("uncertainty_method_missing")
    if not isinstance(evaluation, Mapping) or evaluation.get("residual_analysis") is not True: reasons.append("residual_analysis_missing")
    review = contract.get("independent_review", {})
    if not isinstance(review, Mapping) or review.get("independent") is not True: reasons.append("reviewer_not_independent")
    if not isinstance(review, Mapping) or review.get("status") != "approved": reasons.append("independent_review_not_approved")
    if not isinstance(review, Mapping) or not review.get("reviewer_id"): reasons.append("reviewer_identity_missing")
    return {"schema_version": HTFT_VALIDATION_VERSION,
            "validation_gate_passed": not reasons,
            "status": "validated_for_declared_domain" if not reasons else "blocked",
            "reasons": reasons, "automatic_recommendation_allowed": False,
            "recommendation_blocked": True}
