"""Núcleo independente de domínio para a futura plataforma LTFT."""

from .domain import (
    CASE_SCHEMA_VERSION, REGIME_ENVELOPE_VERSION, LTFTCase, ValidationResult,
    classify_ft_regime, migrate_case_v1_to_v2, validate_case,
)
from .screening import run_screening
from .product_targets import STANDARD_TARGETS, build_target_plan, plan_product_target
from .evidence_validation import audit_evidence_directory

__all__ = ["CASE_SCHEMA_VERSION", "REGIME_ENVELOPE_VERSION", "LTFTCase", "ValidationResult", "classify_ft_regime", "migrate_case_v1_to_v2", "validate_case", "run_screening", "STANDARD_TARGETS", "build_target_plan", "plan_product_target", "audit_evidence_directory"]
