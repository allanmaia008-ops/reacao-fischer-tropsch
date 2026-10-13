"""Estado de navegação da interface, sem regras científicas duplicadas."""

from collections.abc import Iterable


STEP_PRODUCT = "1. Produto desejado"
STEP_REGIME = "2. Regime"
STEP_CATALYST = "3. Catalisador"
STEP_CONDITIONS = "4. Condições"
STEP_RESULTS = "5. Resultados"
STEP_EVIDENCE = "6. Evidências e limites"

WORKFLOW_STEPS = (
    STEP_PRODUCT,
    STEP_REGIME,
    STEP_CATALYST,
    STEP_CONDITIONS,
    STEP_RESULTS,
    STEP_EVIDENCE,
)


def product_input_error(exact_target: str) -> str | None:
    """Valida somente a sintaxe do alvo individual digitado."""
    value = exact_target.strip().upper()
    if not value:
        return None
    if not value.startswith("C") or not value[1:].isdigit():
        return "Use C seguido de um número inteiro, por exemplo C8 ou C16."
    carbon_number = int(value[1:])
    if not 1 <= carbon_number <= 60:
        return "O hidrocarboneto individual deve estar entre C1 e C60."
    return None


def regime_input_errors(regime: str, justification: str) -> tuple[str, ...]:
    """Retorna pendências visíveis antes da confirmação do regime."""
    if regime == "transicao" and not justification.strip():
        return ("Informe a justificativa científica para o regime de transição.",)
    return ()


def catalyst_input_errors(composition: str, phase: str, support: str) -> tuple[str, ...]:
    """Valida os campos textuais mínimos do catalisador."""
    labels = (
        ("composição", composition),
        ("hipótese de fase ativa", phase),
        ("suporte", support),
    )
    return tuple(f"Preencha {label}." for label, value in labels if not value.strip())


def normalize_completed_steps(completed: Iterable[str] | None) -> tuple[str, ...]:
    """Mantém somente etapas conhecidas, sempre na ordem oficial."""
    selected = set(completed or ())
    return tuple(step for step in WORKFLOW_STEPS if step in selected)


def workflow_progress(completed: Iterable[str] | None) -> float:
    """Retorna progresso do fluxo de interface entre zero e um."""
    return len(normalize_completed_steps(completed)) / len(WORKFLOW_STEPS)


def pending_steps(completed: Iterable[str] | None) -> tuple[str, ...]:
    """Lista etapas de navegação ainda não confirmadas pelo usuário."""
    done = set(normalize_completed_steps(completed))
    return tuple(step for step in WORKFLOW_STEPS if step not in done)


def mark_step_complete(completed: Iterable[str] | None, step: str) -> list[str]:
    """Marca uma etapa conhecida e devolve lista serializável para a sessão."""
    if step not in WORKFLOW_STEPS:
        raise ValueError(f"Etapa desconhecida: {step}")
    return list(normalize_completed_steps([*(completed or ()), step]))


def invalidate_from(completed: Iterable[str] | None, step: str) -> list[str]:
    """Invalida a etapa alterada e todas as etapas dependentes seguintes."""
    if step not in WORKFLOW_STEPS:
        raise ValueError(f"Etapa desconhecida: {step}")
    cutoff = WORKFLOW_STEPS.index(step)
    valid = set(normalize_completed_steps(completed))
    return [item for item in WORKFLOW_STEPS[:cutoff] if item in valid]
