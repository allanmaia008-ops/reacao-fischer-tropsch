"""Planejamento orientado ao produto sem promover heurística a cinética."""
import re

from .asf import carbon_fraction, product_bands
from .domain import LTFTCase

STANDARD_TARGETS = ("CH4", "C2-C4", "C5-C11", "C12-C20", "C21+", "C5+")


def normalize_target(target: str) -> str:
    if not isinstance(target, str) or not target.strip():
        raise ValueError("O produto-alvo deve ser informado.")
    compact = target.strip().upper().replace("–", "-").replace(" ", "")
    aliases = {"METANO": "CH4", "C1": "CH4", "GASOLINA": "C5-C11", "DIESEL": "C12-C20", "CERAS": "C21+"}
    compact = aliases.get(compact, compact)
    if compact in STANDARD_TARGETS:
        return compact
    match = re.fullmatch(r"C([1-9]|[1-5][0-9]|60)", compact)
    if match:
        return compact
    raise ValueError("Produto-alvo inválido. Use CH4, C2-C4, C5-C11, C12-C20, C21+, C5+ ou C1-C60.")


def target_fraction(alpha: float, target: str) -> float:
    target = normalize_target(target)
    if target in STANDARD_TARGETS:
        return product_bands(alpha)[target]
    return carbon_fraction(alpha, int(target[1:]))


def mathematical_alpha_orientation(target: str) -> dict:
    """Orienta alpha apenas pela matemática ASF, sem associá-lo a um catalisador."""
    target = normalize_target(target)
    if target in ("C5+", "C21+"):
        return {
            "direction": "aumentar_alpha",
            "finite_optimum": None,
            "note": "Na ASF ideal, a fração da cauda cresce com alpha; não há ótimo interno.",
        }
    if target == "CH4":
        return {
            "direction": "reduzir_alpha",
            "finite_optimum": None,
            "note": "Na ASF ideal, CH4 cresce quando alpha se aproxima de zero; isso não define conversão.",
        }
    if re.fullmatch(r"C\d+", target):
        carbon_number = int(target[1:])
        optimum = (carbon_number - 1) / (carbon_number + 1)
    else:
        # Busca determinística do máximo da faixa em uma malha fina. É um resultado
        # matemático ASF, não ajuste experimental.
        grid = (index / 10000 for index in range(1, 10000))
        optimum = max(grid, key=lambda alpha: target_fraction(alpha, target))
    return {
        "direction": "alpha_intermediario",
        "finite_optimum": round(optimum, 4),
        "note": "Máximo matemático da fração-alvo na ASF ideal; requer validação experimental.",
    }


def plan_product_target(target: str, selected_family: str | None = None) -> dict:
    """Planeja a partir do produto antes da escolha do catalisador."""
    target = normalize_target(target)
    alpha = mathematical_alpha_orientation(target)
    long_chain = target in ("C12-C20", "C21+", "C5+") or (
        target.startswith("C") and target[1:].isdigit() and int(target[1:]) >= 12
    )
    return {
        "desired_product": target,
        "interpretation": "faixa de hidrocarbonetos, não produto puro",
        "asf_orientation": alpha,
        "catalyst_orientation": {
            "candidate_families": ["Co", "Fe"],
            "priority_question": (
                "Avaliar Co para parafinas de cadeia longa e Fe quando atividade WGS/ajuste de gás de síntese for necessária."
                if long_chain else
                "Comparar Co e Fe; seletividade leve não pode ser escolhida apenas pela identidade do metal."
            ),
            "selected_family": selected_family,
            "status": "orientacao_qualitativa_nao_validada_para_o_caso",
        },
        "condition_orientation": {
            "temperature": "avaliar redução de temperatura para favorecer maior crescimento de cadeia" if long_chain else "avaliar temperatura sem inferir seletividade isoladamente",
            "pressure": "avaliar aumento de pressão para favorecer maior crescimento de cadeia" if long_chain else "avaliar pressão em conjunto com conversão e transferência de massa",
            "h2_co": "definir pela família catalítica, atividade WGS e composição real da alimentação",
            "status": "direções qualitativas; nenhuma condição exata foi recomendada",
        },
        "required_experimental_checks": [
            "conversão de CO e balanço de carbono",
            "seletividade por número de carbono e base declarada",
            "vazão, massa de catalisador e GHSV/WHSV com unidades",
            "temperatura real do leito, pressão e tempo em operação",
            "fase ativa, dispersão, desativação e incertezas",
        ],
        "recommendation_blocked": True,
        "blocking_reason": "Faltam dados calibrados específicos do catalisador e das condições para recomendar uma formulação/condição final.",
    }


def build_target_plan(case: LTFTCase) -> dict:
    return plan_product_target(case.desired_product, case.active_family)
