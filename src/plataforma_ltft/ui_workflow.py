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
