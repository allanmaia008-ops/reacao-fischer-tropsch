"""Núcleo independente de domínio para a futura plataforma LTFT."""

from .domain import (
    CASE_SCHEMA_VERSION, REGIME_ENVELOPE_VERSION, LTFTCase, ValidationResult,
    classify_ft_regime, migrate_case_v1_to_v2, validate_case,
)
from .screening import run_screening
from .product_targets import STANDARD_TARGETS, build_target_plan, plan_product_target
from .evidence_validation import audit_evidence_directory
from .corpus_approval import assess_corpus_approval, write_corpus_approval_report
from .applicability import assess_case_applicability, assess_case_compatibility
from .units import (
    CANONICAL_UNITS, FIELD_QUANTITIES, UNIT_CATALOG_VERSION,
    CanonicalMeasurement, UnitDefinition, UnitError,
    canonicalize, canonicalize_field, convert, normalize_unit, unit_catalog,
)
from .catalyst import CATALYST_SCHEMA_VERSION, CatalystValidationResult, validate_catalyst
from .kinetics import KINETIC_CONTRACT_VERSION, KineticContract, kinetic_readiness, validate_kinetic_contract
from .reactor import REACTOR_CONTRACT_VERSION, ReactorContract, inlet_balance, reactor_readiness, validate_reactor_contract
from .thermodynamics import THERMO_CONTRACT_VERSION, ThermodynamicContract, thermodynamic_readiness, validate_thermodynamic_contract
from .experimental_case import EXPERIMENTAL_CASE_SUMMARY_VERSION, experimental_case_summary
from .elemental_balance import ELEMENTAL_BALANCE_VERSION, ElementalBalanceContract, calculate_elemental_balance, validate_elemental_balance_contract
from .asf_measurement import ASF_MEASUREMENT_VERSION, ASFMeasurementContract, compare_asf_to_measurement, validate_asf_measurement_contract
from .advanced_asf import ADVANCED_ASF_VERSION, AdvancedASFContract, advanced_carbon_fraction, advanced_distribution, advanced_tail_fraction, validate_advanced_asf_contract
from .experimental_protocol import EXPERIMENTAL_PROTOCOL_VERSION, ExperimentalProtocolV2, ExperimentalProtocolValidation, migrate_case_to_experimental_protocol_v2, validate_experimental_protocol_v2
from .transport_diagnostics import TRANSPORT_DIAGNOSTICS_VERSION, CRITERION_PROFILE_VERSION, TransportDiagnosticsContract, assess_transport_diagnostics, validate_transport_diagnostics_contract
from .reporting import EXPORT_CONTRACT_VERSION, SCIENTIFIC_REPORT_VERSION, build_export_artifacts, generate_scientific_report

__all__ = ["CASE_SCHEMA_VERSION", "REGIME_ENVELOPE_VERSION", "LTFTCase", "ValidationResult", "classify_ft_regime", "migrate_case_v1_to_v2", "validate_case", "run_screening", "STANDARD_TARGETS", "build_target_plan", "plan_product_target", "audit_evidence_directory", "CANONICAL_UNITS", "FIELD_QUANTITIES", "UNIT_CATALOG_VERSION", "CanonicalMeasurement", "UnitDefinition", "UnitError", "canonicalize", "canonicalize_field", "convert", "normalize_unit", "unit_catalog", "CATALYST_SCHEMA_VERSION", "CatalystValidationResult", "validate_catalyst", "KINETIC_CONTRACT_VERSION", "KineticContract", "kinetic_readiness", "validate_kinetic_contract", "REACTOR_CONTRACT_VERSION", "ReactorContract", "inlet_balance", "reactor_readiness", "validate_reactor_contract", "THERMO_CONTRACT_VERSION", "ThermodynamicContract", "thermodynamic_readiness", "validate_thermodynamic_contract", "EXPERIMENTAL_CASE_SUMMARY_VERSION", "experimental_case_summary", "ELEMENTAL_BALANCE_VERSION", "ElementalBalanceContract", "calculate_elemental_balance", "validate_elemental_balance_contract", "ASF_MEASUREMENT_VERSION", "ASFMeasurementContract", "compare_asf_to_measurement", "validate_asf_measurement_contract", "ADVANCED_ASF_VERSION", "AdvancedASFContract", "advanced_carbon_fraction", "advanced_distribution", "advanced_tail_fraction", "validate_advanced_asf_contract", "EXPERIMENTAL_PROTOCOL_VERSION", "ExperimentalProtocolV2", "ExperimentalProtocolValidation", "migrate_case_to_experimental_protocol_v2", "validate_experimental_protocol_v2", "TRANSPORT_DIAGNOSTICS_VERSION", "CRITERION_PROFILE_VERSION", "TransportDiagnosticsContract", "assess_transport_diagnostics", "validate_transport_diagnostics_contract", "EXPORT_CONTRACT_VERSION", "SCIENTIFIC_REPORT_VERSION", "build_export_artifacts", "generate_scientific_report"]
