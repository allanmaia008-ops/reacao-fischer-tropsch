"""Núcleo independente de domínio para a futura plataforma LTFT."""

from .domain import (
    CASE_SCHEMA_VERSION, REGIME_ENVELOPE_VERSION, LTFTCase, ValidationResult,
    classify_ft_regime, migrate_case_v1_to_v2, validate_case,
)
from .screening import run_screening
from .product_targets import STANDARD_TARGETS, build_target_plan, plan_product_target
from .evidence_validation import audit_evidence_directory
from .units import (
    CANONICAL_UNITS, FIELD_QUANTITIES, UNIT_CATALOG_VERSION,
    CanonicalMeasurement, UnitDefinition, UnitError,
    canonicalize, canonicalize_field, convert, normalize_unit, unit_catalog,
)
from .catalyst import CATALYST_SCHEMA_VERSION, CatalystValidationResult, validate_catalyst
from .kinetics import KINETIC_CONTRACT_VERSION, KineticContract, kinetic_readiness, validate_kinetic_contract

__all__ = ["CASE_SCHEMA_VERSION", "REGIME_ENVELOPE_VERSION", "LTFTCase", "ValidationResult", "classify_ft_regime", "migrate_case_v1_to_v2", "validate_case", "run_screening", "STANDARD_TARGETS", "build_target_plan", "plan_product_target", "audit_evidence_directory", "CANONICAL_UNITS", "FIELD_QUANTITIES", "UNIT_CATALOG_VERSION", "CanonicalMeasurement", "UnitDefinition", "UnitError", "canonicalize", "canonicalize_field", "convert", "normalize_unit", "unit_catalog", "CATALYST_SCHEMA_VERSION", "CatalystValidationResult", "validate_catalyst", "KINETIC_CONTRACT_VERSION", "KineticContract", "kinetic_readiness", "validate_kinetic_contract"]
