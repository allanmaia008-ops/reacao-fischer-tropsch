"""Interface web pública do Projeto Fischer–Tropsch."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import streamlit as st

from plataforma_ltft import (
    CASE_SCHEMA_VERSION, LTFTCase, plan_product_target, run_screening, validate_case,
)
from plataforma_ltft.ui_workflow import (
    STEP_CATALYST,
    STEP_CONDITIONS,
    STEP_EVIDENCE,
    STEP_PRODUCT,
    STEP_REGIME,
    STEP_RESULTS,
    WORKFLOW_STEPS,
    invalidate_from,
    mark_step_complete,
    pending_steps,
    workflow_progress,
)


PRODUCT_OPTIONS = ["CH4", "C2-C4", "C5-C11", "C12-C20", "C21+", "C5+"]


def _initialize_state() -> None:
    defaults = {
        "workflow_step": STEP_PRODUCT,
        "completed_steps": [],
        "target_standard": "C12-C20",
        "target_exact": "",
        "selected_target": None,
        "target_plan": None,
        "ft_regime": "LTFT",
        "regime_justification": "",
        "composition": "Co",
        "active_family": "Co",
        "active_phase": "Co0 a confirmar",
        "support": "Al2O3",
        "loading": 20.0,
        "temperature": 220.0,
        "pressure": 20.0,
        "h2_co_ratio": 2.0,
        "alpha": 0.85,
        "screening_result": None,
        "case_validation": None,
        "evidence_reviewed": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _mark_complete(step: str) -> None:
    st.session_state.completed_steps = mark_step_complete(
        st.session_state.completed_steps, step
    )


def _invalidate_from(step: str) -> None:
    st.session_state.completed_steps = invalidate_from(
        st.session_state.completed_steps, step
    )
    st.session_state.screening_result = None
    st.session_state.case_validation = None
    st.session_state.evidence_reviewed = False


def _set_step(step: str) -> None:
    st.session_state.workflow_step = step


def _regime_changed() -> None:
    regime = st.session_state.ft_regime
    st.session_state.composition = "Fe" if regime == "HTFT" else "Co"
    st.session_state.active_family = "Fe" if regime == "HTFT" else "Co"
    st.session_state.active_phase = "Fase de Fe a confirmar" if regime == "HTFT" else "Co0 a confirmar"
    st.session_state.temperature = {
        "LTFT": 220.0, "transicao": 270.0, "HTFT": 320.0,
    }[regime]
    _invalidate_from(STEP_REGIME)


def _evidence_changed() -> None:
    if st.session_state.evidence_reviewed:
        _mark_complete(STEP_EVIDENCE)
    else:
        st.session_state.completed_steps = invalidate_from(
            st.session_state.completed_steps, STEP_EVIDENCE
        )


def _navigation() -> None:
    completed = st.session_state.completed_steps
    st.sidebar.header("Fluxo de planejamento")
    st.sidebar.radio("Etapa atual", WORKFLOW_STEPS, key="workflow_step")
    progress = workflow_progress(completed)
    st.sidebar.progress(progress, text=f"{len(completed)} de {len(WORKFLOW_STEPS)} etapas confirmadas")
    remaining = pending_steps(completed)
    if remaining:
        st.sidebar.caption("Pendências do fluxo")
        for step in remaining:
            st.sidebar.write(f"○ {step}")
    else:
        st.sidebar.success("Fluxo de interface revisado. Os bloqueios científicos continuam válidos.")
    st.sidebar.divider()
    st.sidebar.caption("O progresso indica preenchimento do fluxo, não validação científica.")


def _step_buttons(previous: str | None, following: str | None) -> None:
    left, right = st.columns(2)
    if previous:
        left.button("← Etapa anterior", on_click=_set_step, args=(previous,), use_container_width=True)
    if following:
        right.button("Próxima etapa →", on_click=_set_step, args=(following,), use_container_width=True)


def _render_product() -> None:
    st.subheader("Produto desejado")
    st.write("Comece pelo hidrocarboneto ou corte que deseja priorizar.")
    with st.form("product_form"):
        st.selectbox("Produto ou faixa-alvo", PRODUCT_OPTIONS, key="target_standard")
        st.text_input("Ou informe um hidrocarboneto individual entre C1 e C60", key="target_exact")
        submitted = st.form_submit_button("Confirmar produto", type="primary")
    if submitted:
        selected = st.session_state.target_exact.strip() or st.session_state.target_standard
        try:
            st.session_state.target_plan = plan_product_target(selected)
        except ValueError as exc:
            st.error(str(exc))
        else:
            st.session_state.selected_target = selected
            _invalidate_from(STEP_PRODUCT)
            _mark_complete(STEP_PRODUCT)
    plan = st.session_state.target_plan
    if plan:
        alpha = plan["asf_orientation"]
        st.info(plan["interpretation"])
        col1, col2 = st.columns(2)
        col1.metric("Alvo normalizado", plan["desired_product"])
        col2.metric("Orientação ASF", alpha["direction"].replace("_", " "))
        if alpha["finite_optimum"] is not None:
            st.write(f"**α do máximo matemático ASF:** {alpha['finite_optimum']:.4f}")
        st.caption(alpha["note"])
        st.warning(plan["blocking_reason"])
    _step_buttons(None, STEP_REGIME)


def _render_regime() -> None:
    st.subheader("Regime Fischer–Tropsch")
    st.selectbox(
        "Regime", ["LTFT", "HTFT", "transicao"], key="ft_regime",
        on_change=_regime_changed,
    )
    if st.session_state.ft_regime == "HTFT":
        st.warning("HTFT está em preparação: a saída será descritiva e a recomendação permanecerá bloqueada.")
    elif st.session_state.ft_regime == "transicao":
        st.warning("A faixa de transição exige justificativa científica explícita.")
    st.text_input(
        "Justificativa do regime (obrigatória para transição)",
        key="regime_justification",
    )
    if st.button("Confirmar regime", type="primary"):
        if st.session_state.ft_regime == "transicao" and not st.session_state.regime_justification.strip():
            st.error("Informe a justificativa científica para o regime de transição.")
        else:
            _mark_complete(STEP_REGIME)
            st.success("Regime confirmado para este fluxo.")
    _step_buttons(STEP_PRODUCT, STEP_CATALYST)


def _render_catalyst() -> None:
    st.subheader("Catalisador")
    regime = st.session_state.ft_regime
    family_options = ["Fe"] if regime == "HTFT" else ["Co", "Fe", "Co-Fe"]
    if st.session_state.active_family not in family_options:
        st.session_state.active_family = family_options[0]
    with st.form("catalyst_form"):
        c1, c2 = st.columns(2)
        c1.text_input("Composição", key="composition")
        c2.selectbox("Família ativa", family_options, key="active_family")
        c1.text_input("Hipótese de fase ativa", key="active_phase")
        c2.text_input("Suporte", key="support")
        st.number_input("Carga de metal ativo (% massa)", 0.01, 100.0, key="loading")
        submitted = st.form_submit_button("Confirmar catalisador", type="primary")
    if submitted:
        required = [st.session_state.composition, st.session_state.active_phase, st.session_state.support]
        if not all(value.strip() for value in required):
            st.error("Preencha composição, hipótese de fase ativa e suporte.")
        else:
            _invalidate_from(STEP_CATALYST)
            _mark_complete(STEP_CATALYST)
            st.success("Dados mínimos do catalisador confirmados.")
    _step_buttons(STEP_REGIME, STEP_CONDITIONS)


def _render_conditions() -> None:
    st.subheader("Condições e execução")
    prerequisites = (STEP_PRODUCT, STEP_REGIME, STEP_CATALYST)
    missing = [step for step in prerequisites if step not in st.session_state.completed_steps]
    if missing:
        st.warning("Confirme antes: " + ", ".join(missing) + ".")
    c1, c2, c3 = st.columns(3)
    c1.number_input(
        "Temperatura (°C)", 180.0, 350.0, key="temperature",
        on_change=_invalidate_from, args=(STEP_CONDITIONS,),
    )
    c2.number_input(
        "Pressão (bar absoluto)", 0.01, 500.0, key="pressure",
        on_change=_invalidate_from, args=(STEP_CONDITIONS,),
    )
    c3.number_input(
        "Razão molar H₂/CO", 0.01, 10.0, key="h2_co_ratio",
        on_change=_invalidate_from, args=(STEP_CONDITIONS,),
    )
    st.number_input(
        "α informado pelo usuário", 0.001, 0.999, key="alpha", step=0.01,
        on_change=_invalidate_from, args=(STEP_CONDITIONS,),
    )
    if st.button("Validar e calcular distribuição ASF", type="primary", disabled=bool(missing)):
        desired_product = st.session_state.selected_target or st.session_state.target_standard
        case = LTFTCase(
            schema_version=CASE_SCHEMA_VERSION,
            composition=st.session_state.composition,
            active_family=st.session_state.active_family,
            active_phase_hypothesis=st.session_state.active_phase,
            support=st.session_state.support,
            active_metal_loading_wt_pct=st.session_state.loading,
            temperature_c=st.session_state.temperature,
            pressure_bar=st.session_state.pressure,
            h2_co_molar_ratio=st.session_state.h2_co_ratio,
            desired_product=desired_product,
            ft_regime=st.session_state.ft_regime,
            regime_justification=st.session_state.regime_justification or None,
        )
        validation = validate_case(case)
        st.session_state.case_validation = validation
        if not validation.valid_for_screening:
            st.session_state.screening_result = None
            st.error("Caso inválido: " + "; ".join(validation.errors or validation.missing_screening_fields))
        else:
            st.session_state.screening_result = run_screening(case, st.session_state.alpha)
            _mark_complete(STEP_CONDITIONS)
            _mark_complete(STEP_RESULTS)
            st.success("Caso válido e distribuição ASF condicional calculada.")
    _step_buttons(STEP_CATALYST, STEP_RESULTS)


def _render_results() -> None:
    st.subheader("Resultados")
    result = st.session_state.screening_result
    if not result:
        st.info("Nenhum resultado disponível. Confirme as etapas anteriores e execute o caso em Condições.")
    else:
        st.success("Distribuição ASF condicional calculada.")
        st.bar_chart(result["product_bands"])
        st.metric("Fração de carbono na faixa-alvo", f"{100 * result['target_fraction']:.2f}%")
        st.json(result["readiness"])
        st.warning(result["warning"])
    _step_buttons(STEP_CONDITIONS, STEP_EVIDENCE)


def _render_evidence() -> None:
    st.subheader("Evidências e limites")
    st.markdown(
        "**Esta versão faz:** seleção de alvo, cálculo ASF condicionado ao α, "
        "validação de entradas e manutenção dos bloqueios científicos."
    )
    st.markdown(
        "**Esta versão não afirma:** conversão, produtividade, cinética calibrada, "
        "fase ativa confirmada, resultado DFT/experimental ou condição ótima."
    )
    reviewed = st.checkbox(
        "Revisei os limites desta execução (isso não aprova evidências nem libera recomendação).",
        key="evidence_reviewed",
        on_change=_evidence_changed,
    )
    if reviewed:
        st.success("Limites revisados para fins de navegação. Bloqueios científicos preservados.")
    _step_buttons(STEP_RESULTS, None)


st.set_page_config(page_title="Projeto Fischer–Tropsch", page_icon="⚗️", layout="wide")
_initialize_state()
_navigation()
st.title("Projeto Fischer–Tropsch")
st.caption("Orientação científica para Fischer–Tropsch em baixa e alta temperatura")
st.warning(
    "A plataforma diferencia orientação ASF, evidência, cálculo e experimento. "
    "Não apresenta heurísticas como cinética calibrada ou recomendação final."
)

renderers = {
    STEP_PRODUCT: _render_product,
    STEP_REGIME: _render_regime,
    STEP_CATALYST: _render_catalyst,
    STEP_CONDITIONS: _render_conditions,
    STEP_RESULTS: _render_results,
    STEP_EVIDENCE: _render_evidence,
}
renderers[st.session_state.workflow_step]()
