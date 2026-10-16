"""Interface web pública do Projeto Fischer–Tropsch."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import altair as alt
import streamlit as st

from plataforma_ltft.domain import CASE_SCHEMA_VERSION, LTFTCase, validate_case
from plataforma_ltft.product_targets import plan_product_target
from plataforma_ltft.reporting import build_export_artifacts, generate_scientific_report
from plataforma_ltft.screening import run_screening
from plataforma_ltft.ui_workflow import (
    STEP_CATALYST,
    STEP_CONDITIONS,
    STEP_EVIDENCE,
    STEP_PRODUCT,
    STEP_REGIME,
    STEP_RESULTS,
    WORKFLOW_STEPS,
    catalyst_input_errors,
    invalidate_from,
    mark_step_complete,
    pending_steps,
    product_input_error,
    regime_input_errors,
    workflow_progress,
)
from plataforma_ltft.ui_design import apply_global_design, maturity_badge, maturity_card, section_intro
from plataforma_ltft.result_panel import carbon_curve, curve_closure, readiness_rows
from plataforma_ltft.evidence_maturity import maturity_catalog, result_maturity_rows
from plataforma_ltft.scenario_comparison import compare_asf_scenarios
from plataforma_ltft.htft_evidence import audit_htft_corpus


PRODUCT_OPTIONS = ["CH4", "C2-C4", "C5-C11", "C12-C20", "C21+", "C5+"]


def _initialize_state() -> None:
    defaults = {
        "workflow_step": STEP_PRODUCT,
        "show_home": True,
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
        "comparison_enabled": False,
        "comparison_count": 2,
        "comparison_alpha_1": 0.80,
        "comparison_alpha_2": 0.85,
        "comparison_alpha_3": 0.90,
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
    st.session_state.show_home = False


def _open_home() -> None:
    st.session_state.show_home = True


def _show_workflow() -> None:
    st.session_state.show_home = False


def _open_step(step: str) -> None:
    st.session_state.workflow_step = step
    st.session_state.show_home = False


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
    st.sidebar.button("⌂ Visão geral", on_click=_open_home, use_container_width=True)
    st.sidebar.header("Fluxo de planejamento")
    st.sidebar.radio(
        "Etapa atual", WORKFLOW_STEPS, key="workflow_step",
        on_change=_show_workflow,
    )
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


def _render_home() -> None:
    section_intro(
        "Planejamento científico orientado pelo produto",
        "Escolha o hidrocarboneto ou corte desejado, descreva o regime, o "
        "catalisador e as condições e obtenha uma análise rastreável dos limites "
        "do caso Fischer–Tropsch.",
    )
    primary, secondary = st.columns(2)
    primary.button(
        "Começar planejamento", type="primary", on_click=_open_step,
        args=(STEP_PRODUCT,), use_container_width=True,
    )
    secondary.button(
        "Revisar escopo e limites", on_click=_open_step,
        args=(STEP_EVIDENCE,), use_container_width=True,
    )

    st.markdown("### Estado científico da plataforma")
    ltft, htft, recommendation = st.columns(3)
    with ltft:
        maturity_card("LTFT", "Protótipo funcional", "Seleção de produto, validação do caso e distribuição ASF condicionada ao α informado.", "success")
    with htft:
        maturity_card("HTFT", "Em preparação", "Cadastro e diagnóstico descritivo, sem reutilizar automaticamente modelos LTFT.", "warning")
    with recommendation:
        maturity_card("Recomendações", "Bloqueadas", "Exigem evidência aprovada, calibração, domínio de aplicabilidade e validação externa.", "blocked")

    st.markdown("### O que você pode fazer agora")
    st.markdown(
        "- definir um produto individual entre C1 e C60 ou uma faixa de carbono;\n"
        "- organizar regime, catalisador e condições do caso;\n"
        "- calcular e visualizar a distribuição ASF para um α fornecido;\n"
        "- verificar pendências, limitações e bloqueios científicos."
    )
    st.info(
        "A plataforma é uma ferramenta de apoio ao planejamento. Ela ainda não "
        "prevê conversão, produtividade ou condição experimental ótima."
    )


def _step_buttons(previous: str | None, following: str | None) -> None:
    left, right = st.columns(2)
    if previous:
        left.button("← Etapa anterior", on_click=_set_step, args=(previous,), use_container_width=True)
    if following:
        right.button("Próxima etapa →", on_click=_set_step, args=(following,), use_container_width=True)


def _render_product() -> None:
    section_intro("Produto desejado", "Comece pelo hidrocarboneto ou corte que deseja priorizar.")
    with st.container(border=True):
        st.markdown("#### Definição do alvo")
        st.selectbox("Produto ou faixa-alvo", PRODUCT_OPTIONS, key="target_standard", help="Faixas de número de carbono usadas para triagem. Elas não garantem um produto comercial puro.")
        st.text_input("Hidrocarboneto individual, opcional", key="target_exact", placeholder="Exemplo: C16", help="Se preenchido, substitui a faixa selecionada. Aceita C1 a C60.")
        product_error = product_input_error(st.session_state.target_exact)
        if product_error:
            st.error(product_error)
        submitted = st.button("Confirmar produto", type="primary", disabled=bool(product_error))
    if submitted and not product_error:
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
    section_intro("Regime Fischer–Tropsch", "Classifique o caso antes de aplicar regras ou evidências específicas.")
    with st.container(border=True):
        st.markdown("#### Classificação térmica")
        st.selectbox("Regime", ["LTFT", "HTFT", "transicao"], key="ft_regime", on_change=_regime_changed, help="LTFT: 180–260 °C. Transição: acima de 260 e abaixo de 280 °C. HTFT: 280–350 °C.")
        st.text_input("Justificativa do regime", key="regime_justification", placeholder="Obrigatória somente para a faixa de transição", help="Registre a base científica usada para classificar um caso na faixa de transição.")
        regime_errors = regime_input_errors(st.session_state.ft_regime, st.session_state.regime_justification)
        for message in regime_errors:
            st.error(message)
        confirm_regime = st.button("Confirmar regime", type="primary", disabled=bool(regime_errors))
    if st.session_state.ft_regime == "HTFT":
        st.warning("HTFT está em preparação: a saída será descritiva e a recomendação permanecerá bloqueada.")
        corpus = audit_htft_corpus(ROOT / "data" / "htft")
        with st.container(border=True):
            st.markdown("#### Diagnóstico HTFT controlado")
            c1, c2, c3 = st.columns(3)
            c1.metric("Alvo inicial", "Olefinas C2–C4")
            c2.metric("Corpus interno", f"{corpus['row_count']} registros")
            c3.metric("Recomendação", "Bloqueada")
            st.caption("Contrato HTFT v1: Fe, O/P por C2–C4, CO₂, água, oxigenados, coque, gradiente térmico e reações secundárias. O corpus serve apenas para comparação contextual.")
    elif st.session_state.ft_regime == "transicao":
        st.warning("A faixa de transição exige justificativa científica explícita.")
    if confirm_regime:
        _mark_complete(STEP_REGIME)
        st.success("Regime confirmado para este fluxo.")
    _step_buttons(STEP_PRODUCT, STEP_CATALYST)


def _render_catalyst() -> None:
    section_intro("Catalisador", "Registre a formulação declarada e diferencie dados medidos de hipóteses.")
    regime = st.session_state.ft_regime
    family_options = ["Fe"] if regime == "HTFT" else ["Co", "Fe", "Co-Fe"]
    if st.session_state.active_family not in family_options:
        st.session_state.active_family = family_options[0]
    with st.container(border=True):
        st.markdown("#### Composição e fase")
        c1, c2 = st.columns(2)
        c1.text_input("Composição", key="composition", help="Composição declarada; não confirma a fase ativa.")
        c2.selectbox("Família ativa", family_options, key="active_family", help="Família usada para aplicar regras específicas do regime.")
        c1.text_input("Hipótese de fase ativa", key="active_phase", help="Hipótese científica que exige confirmação experimental.")
        c2.text_input("Suporte", key="support", help="Material de suporte declarado, por exemplo Al2O3, SiO2 ou TiO2.")
        st.number_input("Carga de metal ativo", 0.01, 100.0, key="loading", format="%.2f", help="Porcentagem em massa (% m/m) do metal ativo.")
        catalyst_errors = catalyst_input_errors(st.session_state.composition, st.session_state.active_phase, st.session_state.support)
        for message in catalyst_errors:
            st.error(message)
        submitted = st.button("Confirmar catalisador", type="primary", disabled=bool(catalyst_errors))
    if submitted:
        _invalidate_from(STEP_CATALYST)
        _mark_complete(STEP_CATALYST)
        st.success("Dados mínimos do catalisador confirmados.")
    _step_buttons(STEP_REGIME, STEP_CONDITIONS)


def _render_conditions() -> None:
    section_intro("Condições e execução", "Informe as condições com unidades explícitas e revise a validação antes do cálculo.")
    prerequisites = (STEP_PRODUCT, STEP_REGIME, STEP_CATALYST)
    missing = [step for step in prerequisites if step not in st.session_state.completed_steps]
    if missing:
        st.warning("Confirme antes: " + ", ".join(missing) + ".")
    with st.container(border=True):
        st.markdown("#### Condições do reator")
        c1, c2, c3 = st.columns(3)
        c1.number_input("Temperatura", 180.0, 350.0, key="temperature", format="%.1f", on_change=_invalidate_from, args=(STEP_CONDITIONS,), help="Unidade: °C. A compatibilidade é verificada contra o regime selecionado.")
        c2.number_input("Pressão absoluta", 0.01, 500.0, key="pressure", format="%.2f", on_change=_invalidate_from, args=(STEP_CONDITIONS,), help="Unidade: bar absoluto.")
        c3.number_input("Razão molar H₂/CO", 0.01, 10.0, key="h2_co_ratio", format="%.2f", on_change=_invalidate_from, args=(STEP_CONDITIONS,), help="Razão molar adimensional na alimentação.")
    with st.container(border=True):
        st.markdown("#### Parâmetro do modelo ASF")
        st.number_input("Probabilidade de crescimento da cadeia (α)", 0.001, 0.999, key="alpha", step=0.01, format="%.3f", on_change=_invalidate_from, args=(STEP_CONDITIONS,), help="Entrada do usuário entre 0 e 1. Não é prevista a partir de temperatura e pressão nesta versão.")
        st.caption("α é uma entrada matemática do cálculo ASF, não uma medição nem uma cinética calibrada.")
    if st.session_state.ft_regime == "HTFT":
        st.info("No modo HTFT, a ASF é apenas uma referência matemática. Conversão, O/P, WGS, coque e balanços dependem de medições e permanecem indisponíveis sem um registro experimental completo.")
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
    section_intro(
        "Resultados",
        "Leia a distribuição matemática junto das entradas, da prontidão e das limitações do caso.",
    )
    result = st.session_state.screening_result
    if not result:
        st.info("Nenhum resultado disponível. Confirme as etapas anteriores e execute o caso em Condições.")
    else:
        case = result["case"]
        target = case["desired_product"]
        st.success("Diagnóstico HTFT condicional calculado." if result["ft_regime"] == "HTFT" else "Distribuição ASF condicional calculada.")
        if result["ft_regime"] == "HTFT":
            st.warning("A curva ASF não representa seletividade HTFT validada. Relações olefina/parafina, CO₂, água, coque e reações secundárias exigem dados medidos.")

        metric_target, metric_alpha, metric_regime = st.columns(3)
        metric_target.metric("Fração de carbono no alvo", f"{100 * result['target_fraction']:.2f}%", help="Fração calculada na base de carbono dos hidrocarbonetos.")
        metric_alpha.metric("α informado", f"{result['alpha']:.3f}", help="Entrada do usuário; não foi estimada por cinética.")
        metric_regime.metric("Regime declarado", result["ft_regime"])

        with st.container(border=True):
            st.markdown("#### Curva ASF por número de carbono")
            curve = carbon_curve(result["alpha"], target)
            chart = (
                alt.Chart(alt.Data(values=curve))
                .mark_bar()
                .encode(
                    x=alt.X("carbon_number:O", title="Número de carbono (Cn)", axis=alt.Axis(labelAngle=0, labelOverlap=True)),
                    y=alt.Y("carbon_fraction:Q", title="Fração de carbono ASF", axis=alt.Axis(format=".1%")),
                    color=alt.Color(
                        "target_group:N", title=None,
                        scale=alt.Scale(domain=["Faixa-alvo", "Demais Cn"], range=["#B45309", "#5B8F82"]),
                    ),
                    tooltip=[
                        alt.Tooltip("carbon_number:O", title="Cn"),
                        alt.Tooltip("carbon_fraction:Q", title="Fração de carbono", format=".4%"),
                        alt.Tooltip("target_group:N", title="Classificação"),
                    ],
                )
                .properties(height=360)
            )
            st.altair_chart(chart, use_container_width=True)
            closure = curve_closure(result["alpha"])
            st.caption(
                f"A curva exibe C1–C60 ({closure['C1-C60']:.4%}). A cauda analítica C61+ "
                f"é {closure['C61+']:.4%}; fechamento total = {closure['total']:.6f}."
            )

        with st.container(border=True):
            st.markdown("#### Faixas de número de carbono")
            bands = result["product_bands"]
            band_columns = st.columns(5)
            for column, label in zip(band_columns, ("CH4", "C2-C4", "C5-C11", "C12-C20", "C21+")):
                column.metric(label, f"{100 * bands[label]:.2f}%")
            st.caption("As faixas são agrupamentos por Cn; não representam automaticamente produtos comerciais após separação ou upgrading.")

        left, right = st.columns(2)
        with left:
            with st.container(border=True):
                st.markdown("#### Condições utilizadas")
                st.table([
                    {"Entrada": "Produto-alvo", "Valor": target},
                    {"Entrada": "Temperatura", "Valor": f"{case['temperature_c']:.1f} °C"},
                    {"Entrada": "Pressão absoluta", "Valor": f"{case['pressure_bar']:.2f} bar"},
                    {"Entrada": "Razão molar H₂/CO", "Valor": f"{case['h2_co_molar_ratio']:.2f}"},
                    {"Entrada": "Catalisador", "Valor": f"{case['active_family']} / {case['support']}"},
                ])
        with right:
            with st.container(border=True):
                st.markdown("#### Prontidão científica")
                st.table(readiness_rows(result["readiness"]))
                missing = result["readiness"]["missing_experimental_fields"]
                if missing:
                    st.caption("Campos ainda necessários para plano experimental: " + ", ".join(missing) + ".")

        st.warning(result["warning"])
        st.error("Recomendação bloqueada: " + result["recommendation_blocking_reason"])

        with st.container(border=True):
            st.markdown("#### Maturidade dos resultados")
            for item in result_maturity_rows(result):
                maturity_badge(item["category"])
                st.markdown(f"**{item['artifact']}** — {item['provenance']}")
                st.caption(item["limitation"])

        with st.container(border=True):
            st.markdown("#### Exportação e relatório científico")
            st.caption("Arquivos versionados e reproduzíveis. A exportação preserva campos nulos, proveniência disponível e bloqueios científicos.")
            artifacts = build_export_artifacts(result)
            report = generate_scientific_report(result)
            export_columns = st.columns(4)
            export_columns[0].download_button(
                "Baixar resultado JSON", artifacts["resultado_ft_v1.json"],
                file_name="resultado_ft_v1.json", mime="application/json",
            )
            export_columns[1].download_button(
                "Baixar resumo CSV", artifacts["resumo_ft_v1.csv"],
                file_name="resumo_ft_v1.csv", mime="text/csv",
            )
            export_columns[2].download_button(
                "Baixar faixas ASF CSV", artifacts["faixas_asf_v1.csv"],
                file_name="faixas_asf_v1.csv", mime="text/csv",
            )
            export_columns[3].download_button(
                "Baixar relatório científico", report.encode("utf-8"),
                file_name="relatorio_cientifico_ft_v1.md", mime="text/markdown",
            )
            with st.expander("Manifesto de integridade"):
                st.download_button(
                    "Baixar manifesto JSON", artifacts["manifesto_exportacao_v1.json"],
                    file_name="manifesto_exportacao_v1.json", mime="application/json",
                )

        with st.container(border=True):
            st.markdown("#### Comparação de cenários ASF")
            st.checkbox(
                "Ativar comparação matemática", key="comparison_enabled",
                help="Compara somente a sensibilidade ao α. Não otimiza condições experimentais.",
            )
            if st.session_state.comparison_enabled:
                st.selectbox("Número de cenários", [2, 3], key="comparison_count")
                comparison_columns = st.columns(st.session_state.comparison_count)
                alphas = []
                for index, column in enumerate(comparison_columns, start=1):
                    key = f"comparison_alpha_{index}"
                    alphas.append(column.number_input(
                        f"α do cenário {index}", 0.001, 0.999, key=key,
                        step=0.01, format="%.3f",
                    ))
                try:
                    comparison = compare_asf_scenarios(alphas, target)
                except ValueError as exc:
                    st.error(str(exc))
                else:
                    comparison_rows = [
                        {
                            "Cenário": row["scenario"], "α": row["alpha"],
                            "Fração no alvo (%)": 100 * row["target_fraction"],
                            "CH4 (%)": 100 * row["CH4"], "C2-C4 (%)": 100 * row["C2-C4"],
                            "C5-C11 (%)": 100 * row["C5-C11"], "C12-C20 (%)": 100 * row["C12-C20"],
                            "C21+ (%)": 100 * row["C21+"],
                        }
                        for row in comparison["summaries"]
                    ]
                    st.dataframe(
                        comparison_rows, use_container_width=True, hide_index=True,
                        column_config={
                            "α": st.column_config.NumberColumn(format="%.3f"),
                            **{
                                name: st.column_config.NumberColumn(format="%.2f")
                                for name in ("Fração no alvo (%)", "CH4 (%)", "C2-C4 (%)", "C5-C11 (%)", "C12-C20 (%)", "C21+ (%)")
                            },
                        },
                    )
                    comparison_chart = (
                        alt.Chart(alt.Data(values=comparison["curve"]))
                        .mark_line(point=False)
                        .encode(
                            x=alt.X("carbon_number:Q", title="Número de carbono (Cn)"),
                            y=alt.Y("carbon_fraction:Q", title="Fração de carbono ASF", axis=alt.Axis(format=".1%")),
                            color=alt.Color("scenario:N", title="Cenário"),
                            strokeDash=alt.StrokeDash("target_group:N", title="Relação com o alvo"),
                            tooltip=["scenario:N", alt.Tooltip("alpha:Q", format=".3f"), "carbon_number:Q", alt.Tooltip("carbon_fraction:Q", format=".4%")],
                        )
                        .properties(height=320)
                    )
                    st.altair_chart(comparison_chart, use_container_width=True)
                    st.warning("Sensibilidade matemática condicionada ao α. Não é otimização nem recomendação experimental.")
    _step_buttons(STEP_CONDITIONS, STEP_EVIDENCE)


def _render_evidence() -> None:
    section_intro("Evidências e limites", "Interprete cada saída conforme sua origem e seu nível de maturidade.")
    st.markdown(
        "**Esta versão faz:** seleção de alvo, cálculo ASF condicionado ao α, "
        "validação de entradas e manutenção dos bloqueios científicos."
    )
    st.markdown(
        "**Esta versão não afirma:** conversão, produtividade, cinética calibrada, "
        "fase ativa confirmada, resultado DFT/experimental ou condição ótima."
    )
    st.markdown("### Modelagem de processo em preparação")
    reactor_col, thermo_col = st.columns(2)
    with reactor_col:
        with st.container(border=True):
            st.markdown("**Reator LTFT — infraestrutura parcial**")
            st.write(
                "Contrato, validação de entradas, inventário molar de alimentação e porta de "
                "prontidão implementados. Conversão e produtividade permanecem bloqueadas sem "
                "cinética validada e modelos físicos selecionados."
            )
    with thermo_col:
        with st.container(border=True):
            st.markdown("**Termodinâmica — contrato parcial**")
            st.write(
                "EOS, regra de mistura, pseudocomponentes, VLE, cobertura de fases, domínio e "
                "métricas têm contrato versionado. O pacote só fica pronto após comparação com "
                "dados rastreáveis."
            )
    st.markdown("### Catálogo de maturidade")
    for item in maturity_catalog():
        with st.container(border=True):
            maturity_badge(item["category"])
            st.write(item["definition"])
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
apply_global_design()
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
if st.session_state.show_home:
    _render_home()
else:
    renderers[st.session_state.workflow_step]()
