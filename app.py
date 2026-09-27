"""Interface web da Plataforma LTFT, independente do protótipo legado."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import streamlit as st

from plataforma_ltft import LTFTCase, plan_product_target, run_screening, validate_case


st.set_page_config(page_title="Plataforma LTFT", page_icon="⚗️", layout="wide")
st.title("Plataforma LTFT")
st.caption("Orientação científica para Fischer–Tropsch em baixa temperatura")
st.warning(
    "A plataforma diferencia orientação ASF, evidência, cálculo e experimento. "
    "Não apresenta heurísticas como cinética calibrada ou recomendação final."
)

target_tab, case_tab, limits_tab = st.tabs([
    "Planejar pelo produto", "Avaliar um caso", "Escopo e limites",
])

with target_tab:
    st.subheader("Qual hidrocarboneto deseja priorizar?")
    target = st.selectbox(
        "Produto ou faixa-alvo",
        ["CH4", "C2-C4", "C5-C11", "C12-C20", "C21+", "C5+"],
        index=3,
    )
    exact = st.text_input("Ou informe um hidrocarboneto individual entre C1 e C60", "")
    selected_target = exact.strip() or target
    try:
        plan = plan_product_target(selected_target)
    except ValueError as exc:
        st.error(str(exc))
    else:
        alpha = plan["asf_orientation"]
        st.info(plan["interpretation"])
        col1, col2 = st.columns(2)
        col1.metric("Alvo normalizado", plan["desired_product"])
        col2.metric("Orientação ASF", alpha["direction"].replace("_", " "))
        if alpha["finite_optimum"] is not None:
            st.write(f"**α do máximo matemático ASF:** {alpha['finite_optimum']:.4f}")
        st.caption(alpha["note"])
        st.markdown("#### Orientação catalítica")
        st.write(plan["catalyst_orientation"]["priority_question"])
        st.markdown("#### Direções experimentais qualitativas")
        for field, text in plan["condition_orientation"].items():
            if field != "status":
                st.write(f"- **{field}:** {text}")
        st.warning(plan["blocking_reason"])

with case_tab:
    st.subheader("Entradas do caso LTFT")
    with st.form("case_form"):
        c1, c2, c3 = st.columns(3)
        composition = c1.text_input("Composição", "Co")
        family = c2.selectbox("Família ativa", ["Co", "Fe", "Co-Fe"])
        phase = c3.text_input("Hipótese de fase ativa", "Co0 a confirmar")
        support = c1.text_input("Suporte", "Al2O3")
        loading = c2.number_input("Carga de metal ativo (% massa)", 0.01, 100.0, 20.0)
        product = c3.selectbox("Produto-alvo do caso", ["CH4", "C2-C4", "C5-C11", "C12-C20", "C21+", "C5+"])
        temperature = c1.number_input("Temperatura (°C)", -273.14, 1000.0, 220.0)
        pressure = c2.number_input("Pressão (bar absoluto)", 0.01, 500.0, 20.0)
        ratio = c3.number_input("Razão molar H₂/CO", 0.01, 10.0, 2.0)
        alpha = st.number_input("α informado pelo usuário", 0.001, 0.999, 0.850, step=0.01)
        submitted = st.form_submit_button("Avaliar distribuição ASF", type="primary")
    if submitted:
        case = LTFTCase(
            composition=composition,
            active_family=family,
            active_phase_hypothesis=phase,
            support=support,
            active_metal_loading_wt_pct=loading,
            temperature_c=temperature,
            pressure_bar=pressure,
            h2_co_molar_ratio=ratio,
            desired_product=product,
        )
        validation = validate_case(case)
        if not validation.valid_for_screening:
            st.error("Caso inválido: " + "; ".join(validation.errors or validation.missing_screening_fields))
        else:
            result = run_screening(case, alpha)
            st.success("Distribuição ASF condicional calculada.")
            st.bar_chart(result["product_bands"])
            st.metric("Fração de carbono na faixa-alvo", f"{100 * result['target_fraction']:.2f}%")
            st.json(result["readiness"])
            st.warning(result["warning"])

with limits_tab:
    st.subheader("O que esta versão faz")
    st.markdown(
        "- seleciona um hidrocarboneto ou faixa-alvo;\n"
        "- calcula a distribuição ASF condicionada ao α informado;\n"
        "- valida entradas científicas e experimentais;\n"
        "- mantém recomendações bloqueadas quando faltam evidências."
    )
    st.subheader("O que esta versão não afirma")
    st.markdown(
        "- conversão de CO ou produtividade;\n"
        "- cinética calibrada;\n"
        "- fase ativa confirmada;\n"
        "- resultado DFT ou experimental;\n"
        "- formulação ou condição ótima definitiva."
    )
