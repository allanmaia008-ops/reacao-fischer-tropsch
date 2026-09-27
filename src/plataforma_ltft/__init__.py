"""Núcleo independente de domínio para a futura plataforma LTFT."""

from .domain import LTFTCase, ValidationResult, validate_case
from .screening import run_screening
from .product_targets import STANDARD_TARGETS, build_target_plan, plan_product_target
from .evidence_validation import audit_evidence_directory

__all__ = ["LTFTCase", "ValidationResult", "validate_case", "run_screening", "STANDARD_TARGETS", "build_target_plan", "plan_product_target", "audit_evidence_directory"]
