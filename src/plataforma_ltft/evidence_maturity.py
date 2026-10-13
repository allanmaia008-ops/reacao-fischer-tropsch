"""Estados rastreáveis de maturidade científica apresentados pela interface."""

MATURITY_DEFINITIONS = {
    "matemático": "Resultado derivado de equações declaradas, sem calibração experimental.",
    "heurístico": "Orientação qualitativa que ainda exige teste e calibração.",
    "literatura": "Afirmação sustentada por fonte bibliográfica identificada.",
    "experimental": "Resultado medido com método, condições e proveniência registrados.",
    "calibrado": "Modelo ajustado e validado dentro de um domínio declarado.",
    "bloqueado": "Uso indisponível porque faltam dados, validação ou autorização científica.",
}


def maturity_catalog() -> list[dict[str, str]]:
    """Catálogo completo; cor nunca é o único portador do significado."""
    return [
        {"category": category, "definition": definition}
        for category, definition in MATURITY_DEFINITIONS.items()
    ]


def result_maturity_rows(result: dict) -> list[dict[str, str]]:
    """Classifica somente artefatos cujo estado está explícito no resultado."""
    rows = [
        {
            "artifact": "Distribuição ASF",
            "category": "matemático",
            "provenance": f"equação ASF; α {result['alpha_origin']}",
            "limitation": "Não calcula conversão, produtividade nem cinética.",
        },
        {
            "artifact": "Orientação de produto e condições",
            "category": "heurístico",
            "provenance": "target_plan; direções qualitativas",
            "limitation": "Não constitui recomendação experimental.",
        },
    ]
    if result.get("recommendation_blocked", True):
        rows.append({
            "artifact": "Recomendação final",
            "category": "bloqueado",
            "provenance": "recommendation_blocked=true",
            "limitation": result["recommendation_blocking_reason"],
        })
    return rows
