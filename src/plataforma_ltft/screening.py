"""Execução mínima auditável; não estima alpha nem conversão a partir do catalisador."""
from dataclasses import asdict

from .asf import product_bands, validate_alpha
from .domain import LTFTCase, validate_case
from .product_targets import build_target_plan, target_fraction


def run_screening(case: LTFTCase, alpha: float) -> dict:
    validation = validate_case(case)
    if not validation.valid_for_screening:
        raise ValueError({
            "missing": validation.missing_screening_fields,
            "errors": validation.errors,
        })
    alpha = validate_alpha(alpha)
    return {
        "schema_version": "1.0.0",
        "status": "distribuicao_asf_condicional",
        "case": asdict(case),
        "alpha": alpha,
        "alpha_origin": "informado_pelo_usuario",
        "product_basis": "fracao_do_carbono_nos_hidrocarbonetos",
        "product_bands": product_bands(alpha),
        "target_fraction": target_fraction(alpha, case.desired_product),
        "target_plan": build_target_plan(case),
        "readiness": {
            "valid_for_screening": validation.valid_for_screening,
            "valid_for_experimental_plan": validation.valid_for_experimental_plan,
            "valid_for_rate_calculation": validation.valid_for_rate_calculation,
            "missing_experimental_fields": validation.missing_experimental_fields,
            "missing_rate_fields": validation.missing_rate_fields,
        },
        "CO_conversion_pct": None,
        "physical_productivity": None,
        "WGS_extent": None,
        "warning": "Resultado condicional a alpha; não é cinética, DFT ou validação experimental.",
    }
